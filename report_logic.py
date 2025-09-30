# report_logic.py
import calendar
import logging
import time
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import requests
from PyQt6.QtCore import QObject, pyqtSignal
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from translations import get_string

# --- CONFIGURAÇÕES E EXCEÇÕES CUSTOMIZADAS ---
VERIFY_SSL = False
if not VERIFY_SSL:
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Exceção customizada para identificar erros da API
class ZabbixAPIError(Exception):
    pass


# Mapas de tradução (gerados dinamicamente no início da execução)
ACK_ACTION_MAP = {
    '1': get_string('ack_close_problem'), '2': get_string('ack_acknowledge_event'),
    '4': get_string('ack_add_comment'), '8': get_string('ack_change_severity')
}
SEVERITY_MAP = {
    '0': get_string('sev_not_classified'), '1': get_string('sev_information'),
    '2': get_string('sev_warning'), '3': get_string('sev_average'),
    '4': get_string('sev_high'), '5': get_string('sev_disaster')
}


class ReportGenerator(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.api_session = requests.Session()
        self.api_session.headers.update({'Content-Type': 'application/json'})

    def run(self):
        """Método de execução principal com tratamento de erro aprimorado."""
        try:
            self.progress.emit(get_string('log_starting'))
            start_time = time.time()

            problem_events = self._fetch_all_events()
            if not problem_events:
                self.finished.emit(get_string('log_no_events'))
                return

            self.progress.emit(get_string('log_events_found', count=len(problem_events)))

            related_data = self._fetch_related_data(problem_events)
            problem_rows, ack_rows = self._process_events_to_rows(problem_events, related_data)

            df_problems = pd.DataFrame(problem_rows)
            df_acks = pd.DataFrame(ack_rows)

            self.progress.emit(get_string('log_preparing_data'))
            df_problems_naive, df_acks_naive = self._prepare_dataframes(df_problems, df_acks)

            all_report_data = self._generate_sla_reports(df_problems_naive)
            final_data_sheets = self._build_final_sheets(df_problems_naive, df_acks_naive, all_report_data)

            if not final_data_sheets:
                self.finished.emit(get_string('log_no_data'))
                return

            self.progress.emit(get_string('log_saving_report'))
            outfile_consolidated = self._save_report(final_data_sheets, all_report_data)
            self.progress.emit(get_string('log_report_saved', outfile=outfile_consolidated))

            end_time = time.time()
            self.progress.emit(get_string('log_process_complete', seconds=end_time - start_time))
            self.finished.emit(get_string('log_success_message', path=self.config['output_dir']))

        except ZabbixAPIError as e:
            error_message = str(e)
            if "Session terminated" in error_message or "Not authorised" in error_message:
                friendly_message = get_string('zabbix_auth_error_friendly')
                self.error.emit(friendly_message)
            else:
                self.error.emit(get_string('zabbix_generic_api_error', details=error_message))
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado: {e}", exc_info=True)
            self.error.emit(get_string('unexpected_error_details', error=e))

    def _call_zabbix_api(self, method: str, params: dict) -> list | dict:
        """Função centralizada para chamadas à API, agora lança uma exceção customizada."""
        payload = {'jsonrpc': '2.0', 'method': method, 'params': params, 'auth': self.config['token'], 'id': 1}
        try:
            response = self.api_session.post(self.config['url'], json=payload, verify=VERIFY_SSL, timeout=600)
            response.raise_for_status()
            result = response.json()
            if 'error' in result:
                err_msg = result['error'].get('data', 'Unknown Zabbix API error')
                raise ZabbixAPIError(get_string('zabbix_api_call_error', method=method, error_message=err_msg))
            return result.get('result', [])
        except RequestException as e:
            raise Exception(get_string('zabbix_connection_call_error', error=e))

    def _fetch_all_events(self):
        """Fetches all primary problem events for the month."""
        year, month = self.config['year'], self.config['month']
        local_tz = datetime.now().astimezone().tzinfo
        _, last_day = calendar.monthrange(year, month)
        start_of_month = datetime(year, month, 1)
        end_of_month = datetime(year, month, last_day)
        all_events = []

        total_days = (end_of_month - start_of_month).days + 1

        self.progress.emit(get_string('log_fetching_days', start_date=start_of_month.strftime('%Y-%m-%d'),
                                      end_date=end_of_month.strftime('%Y-%m-%d')))

        for day_num in range(total_days):
            current_day = start_of_month + timedelta(days=day_num)
            time_from = current_day.replace(tzinfo=local_tz)
            time_till = current_day.replace(hour=23, minute=59, second=59, tzinfo=local_tz)

            self.progress.emit(get_string('log_fetching_day_progress', day_num=day_num + 1, total_days=total_days,
                                          date=current_day.strftime('%Y-%m-%d')))

            params = {
                'output': ['eventid', 'clock', 'severity', 'name', 'r_eventid', 'acknowledged'],
                'severities': self.config['severities'],
                'source': 0, 'object': 0, 'value': 1,
                'time_from': int(time_from.timestamp()),
                'time_till': int(time_till.timestamp()),
                'selectHosts': ['hostid'], 'selectTags': 'extend',
                'select_alerts': 'count', 'select_acknowledges': 'extend',
                'sortfield': ['clock', 'eventid'], 'sortorder': 'ASC'
            }
            daily_events = self._call_zabbix_api('event.get', params)
            all_events.extend(daily_events)
            time.sleep(0.1)
        return all_events

    def _chunk_list(self, data: list, size: int):
        for i in range(0, len(data), size):
            yield data[i:i + size]

    def _fetch_related_data(self, events: list) -> tuple[dict, dict, dict]:
        """Fetches related data (recoveries, hosts, users) in batches."""
        r_eventids = list({e['r_eventid'] for e in events if e.get('r_eventid') and e['r_eventid'] != '0'})
        hostids = list({h['hostid'] for e in events if e.get('hosts') for h in e['hosts']})
        userids = list({ack['userid'] for e in events if e.get('acknowledges') for ack in e['acknowledges']})

        recovery_times = {}
        self.progress.emit(get_string('log_fetching_recoveries', count=len(r_eventids)))
        for id_chunk in self._chunk_list(r_eventids, 2000):
            if not id_chunk: continue
            recovery_events_chunk = self._call_zabbix_api('event.get',
                                                          {'eventids': id_chunk, 'output': ['eventid', 'clock']})
            for event in recovery_events_chunk:
                recovery_times[event['eventid']] = int(event['clock'])
            time.sleep(0.1)

        self.progress.emit(get_string('log_fetching_hosts', count=len(hostids)))
        hosts = self._call_zabbix_api('host.get', {'hostids': hostids, 'output': ['hostid', 'name']}) if hostids else []
        host_map = {h['hostid']: h['name'] for h in hosts}

        self.progress.emit(get_string('log_fetching_users', count=len(userids)))
        users = self._call_zabbix_api('user.get', {'userids': userids,
                                                 'output': ['userid', 'alias', 'name', 'surname']}) if userids else []
        user_map = {
            u['userid']: get_string(
                'user_display_format',
                name=u.get('name', ''),
                surname=u.get('surname', ''),
                alias=u.get('alias', get_string('user_alias_fallback'))
            ).strip() for u in users
        }

        return recovery_times, host_map, user_map

    def _process_events_to_rows(self, events, related_data):
        """Processes raw event data into structured lists of rows."""
        recovery_times, host_map, user_map = related_data
        problem_rows, ack_rows = [], []
        self.progress.emit(get_string('log_processing_events'))

        for event in events:
            start_dt = datetime.fromtimestamp(int(event['clock']), tz=timezone.utc).astimezone()
            is_closed = event.get('r_eventid') and event['r_eventid'] != '0'
            recovery_ts = recovery_times.get(event.get('r_eventid'))
            rec_dt = datetime.fromtimestamp(recovery_ts, tz=timezone.utc).astimezone() if recovery_ts else None
            duration = (rec_dt - start_dt) if rec_dt else None
            host_id = event['hosts'][0]['hostid'] if event.get('hosts') else None

            first_ack_dt, first_ack_user = None, None
            if event.get('acknowledges'):
                first_ack = min(event['acknowledges'], key=lambda x: int(x['clock']))
                first_ack_dt = datetime.fromtimestamp(int(first_ack['clock']), tz=timezone.utc).astimezone()
                first_ack_user = user_map.get(first_ack['userid'], f"{get_string('user_id_prefix')}{first_ack['userid']}")

            problem_rows.append({
                'EventID': event['eventid'], 'Time': start_dt,
                'Severity': SEVERITY_MAP.get(event.get('severity', '0')), 'Recovery Time': rec_dt,
                'Status': get_string('status_resolved') if is_closed else get_string('status_problem'),
                'Host': host_map.get(host_id, get_string('not_applicable')),
                'Problem': event.get('name', ''), 'Duration': duration,
                'Ack': get_string('ack_yes') if event.get('acknowledged') == '1' else get_string('ack_no'),
                'First Ack Time': first_ack_dt, 'First Ack User': first_ack_user,
                'Actions': get_string('messages_sent_format', count=event.get('alerts', '0')),
                'Tags': get_string('tag_separator').join(f"{t['tag']}={t['value']}" for t in event.get('tags', []))
            })

            for ack in event.get('acknowledges', []):
                action_code = ack.get('action', '0')
                action_desc = [desc for code, desc in ACK_ACTION_MAP.items() if int(action_code) & int(code)]
                ack_rows.append({
                    'Event Time': start_dt, 'Host': host_map.get(host_id, get_string('not_applicable')),
                    'Problem': event.get('name', ''),
                    'User': user_map.get(ack['userid'], f"{get_string('user_id_prefix')}{ack['userid']}"),
                    'Action Type': get_string('action_separator').join(action_desc) if action_desc else get_string('ack_unknown'),
                    'Message': ack.get('message', ''),
                    'Ack Time': datetime.fromtimestamp(int(ack['clock']), tz=timezone.utc).astimezone()
                })
        return problem_rows, ack_rows

    def _prepare_dataframes(self, df_problems, df_acks):
        df_problems_naive = df_problems.copy()
        for col in ['Time', 'Recovery Time', 'First Ack Time']:
            if col in df_problems_naive.columns and not df_problems_naive[col].isnull().all():
                df_problems_naive[col] = pd.to_datetime(df_problems_naive[col]).dt.tz_localize(None)

        df_acks_naive = df_acks.copy()
        if not df_acks_naive.empty:
            for col in ['Event Time', 'Ack Time']:
                if col in df_acks_naive.columns and not df_acks_naive[col].isnull().all():
                    df_acks_naive[col] = pd.to_datetime(df_acks_naive[col]).dt.tz_localize(None)
        return df_problems_naive, df_acks_naive

    def _generate_sla_reports(self, df_problems: pd.DataFrame) -> dict:
        """Generates all DataFrames for the multi-sheet SLA analysis report."""
        self.progress.emit(get_string('log_generating_sla'))
        sla_threshold_minutes = self.config['sla_threshold']

        df_acknowledged = df_problems[df_problems['First Ack Time'].notna()].copy()
        if df_acknowledged.empty:
            self.progress.emit(get_string('log_warn_no_acks'))
            return {}

        df_acknowledged['Ack Duration (min)'] = (
                (df_acknowledged['First Ack Time'] - df_acknowledged['Time']).dt.total_seconds() / 60)
        df_acknowledged['SLA Status'] = np.where(df_acknowledged['Ack Duration (min)'] <= sla_threshold_minutes,
                                                 get_string('sla_met'), get_string('sla_violated'))

        df_sla_details = df_acknowledged[
            ['EventID', 'Host', 'Problem', 'Time', 'First Ack Time', 'First Ack User', 'Ack Duration (min)',
             'SLA Status']].copy()
        df_sla_details['Ack Duration (min)'] = df_sla_details['Ack Duration (min)'].round(2)

        df_sla_details['Date'] = df_sla_details['Time'].dt.normalize()
        df_daily_sla = df_sla_details.groupby(['Date', 'SLA Status']).size().unstack(fill_value=0)

        met_col, violated_col = get_string('sla_met'), get_string('sla_violated')
        if met_col not in df_daily_sla.columns: df_daily_sla[met_col] = 0
        if violated_col not in df_daily_sla.columns: df_daily_sla[violated_col] = 0

        df_daily_sla['Total Acks'] = df_daily_sla[met_col] + df_daily_sla[violated_col]
        df_daily_sla['% Met'] = (df_daily_sla[met_col] / df_daily_sla['Total Acks'] * 100).round(2)
        df_daily_sla = df_daily_sla.reset_index()

        df_problems['Date'] = df_problems['Time'].dt.normalize()
        df_daily_volume = df_problems.groupby('Date').size().reset_index(name='Total Events')
        df_top_10 = df_problems.groupby('Problem').size().nlargest(10).reset_index(name='Count')
        df_user_prod = df_sla_details.groupby('First Ack User').agg(
            Total_Acks=('EventID', 'count'),
            SLA_Violations=('SLA Status', lambda x: (x == violated_col).sum())
        ).reset_index().sort_values(by='Total_Acks', ascending=False)

        df_monthly_summary = pd.DataFrame(
            {'Status': [met_col, violated_col],
             'Count': [df_daily_sla[met_col].sum(), df_daily_sla[violated_col].sum()]})

        return {
            'SLA Details': df_sla_details, 'Daily SLA Summary': df_daily_sla,
            'Daily Event Volume': df_daily_volume, 'Top 10 Problems': df_top_10,
            'User Productivity': df_user_prod, 'Monthly Summary Data': df_monthly_summary
        }

    def _build_final_sheets(self, df_problems_naive, df_acks_naive, all_report_data):
        """Prepares final dataframes for saving, translating sheet names and column headers."""
        final_data_sheets = {}

        column_map = {
            'Time': get_string('col_time'), 'Severity': get_string('col_severity'),
            'Recovery Time': get_string('col_recovery_time'),
            'Status': get_string('col_status'), 'Host': get_string('col_host'), 'Problem': get_string('col_problem'),
            'Duration': get_string('col_duration'), 'Ack': get_string('col_ack'), 'Actions': get_string('col_actions'),
            'Tags': get_string('col_tags'), 'Event Time': get_string('col_event_time'), 'User': get_string('col_user'),
            'Action Type': get_string('col_action_type'), 'Message': get_string('col_message'),
            'Ack Time': get_string('col_ack_time'),
            'EventID': get_string('col_event_id'), 'First Ack Time': get_string('col_first_ack_time'),
            'First Ack User': get_string('col_first_ack_user'),
            'Ack Duration (min)': get_string('col_ack_duration_min'),
            'SLA Status': get_string('col_sla_status'), 'Date': get_string('col_date'),
            get_string('sla_met'): get_string('col_met'),
            get_string('sla_violated'): get_string('col_violated'), 'Total Acks': get_string('col_total_acks'),
            '% Met': get_string('col_percent_met'),
            'Total Events': get_string('col_total_events'), 'Count': get_string('col_count'),
            'SLA_Violations': get_string('col_sla_violations')
        }

        if not df_problems_naive.empty:
            df_problems_to_save = df_problems_naive.drop(
                columns=['EventID', 'First Ack Time', 'First Ack User', 'Date'], errors='ignore'
            ).rename(columns=column_map)
            final_data_sheets[get_string('sheet_problems')] = df_problems_to_save

        if not df_acks_naive.empty:
            df_acks_to_save = df_acks_naive.rename(columns=column_map)
            final_data_sheets[get_string('sheet_actions')] = df_acks_to_save

        if all_report_data:
            chart_data_key = 'Monthly Summary Data'
            sheet_name_map = {
                'SLA Details': get_string('sheet_sla_details'), 'Daily SLA Summary': get_string('sheet_daily_sla'),
                'Daily Event Volume': get_string('sheet_daily_volume'), 'Top 10 Problems': get_string('sheet_top_10'),
                'User Productivity': get_string('sheet_user_prod')
            }
            for key, df in all_report_data.items():
                if key != chart_data_key:
                    df_to_save = df.rename(columns=column_map)
                    final_data_sheets[sheet_name_map[key]] = df_to_save
        return final_data_sheets

    def _save_report(self, final_data_sheets, all_report_data):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename_prefix = get_string('report_filename_prefix')
        outfile = self.config[
                      'output_dir'] / f"{filename_prefix}_{self.config['year']}_{self.config['month']:02d}_{timestamp}.xlsx"

        with pd.ExcelWriter(str(outfile), engine='xlsxwriter', engine_kwargs={'options': {'strings_to_urls': False}},
                            datetime_format='yyyy-mm-dd hh:mm:ss', date_format='yyyy-mm-dd') as writer:
            self._write_formatted_sheets(writer, final_data_sheets)
            self._add_charts_to_report(writer, all_report_data)

        return outfile

    def _write_formatted_sheets(self, writer, dataframes_dict: dict):
        """Writes and formats multiple DataFrames to a single Excel writer object."""
        workbook = writer.book
        for sheet_name, df in dataframes_dict.items():
            if df.empty:
                self.progress.emit(get_string('log_warn_empty_sheet', sheet_name=sheet_name))
                continue

            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=1)
            worksheet = writer.sheets[sheet_name]

            (max_row, max_col) = df.shape
            column_settings = [{'header': str(column)} for column in df.columns]
            worksheet.add_table(0, 0, max_row, max_col - 1,
                                {'columns': column_settings, 'style': 'Table Style Medium 9'})

            for i, col in enumerate(df.columns):
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    worksheet.set_column(i, i, 20)
                elif str(col) == get_string('col_tags'):
                    worksheet.set_column(i, i, 80)
                else:
                    column_len = max(df[col].astype(str).str.len().max(), len(str(col)))
                    worksheet.set_column(i, i, min(column_len + 2, 60))

            severity_col_name = get_string('col_severity')
            if severity_col_name in df.columns:
                severity_col_idx = df.columns.get_loc(severity_col_name)
                severity_formats = {
                    get_string('sev_disaster'): workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'}),
                    get_string('sev_high'): workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'}),
                    get_string('sev_average'): workbook.add_format({'bg_color': '#FFFFCC', 'font_color': '#595959'}),
                }
                for severity_text, style_format in severity_formats.items():
                    worksheet.conditional_format(1, severity_col_idx, max_row, severity_col_idx, {
                        'type': 'cell', 'criteria': '==', 'value': f'"{severity_text}"', 'format': style_format
                    })

            sla_col_name = get_string('col_sla_status')
            if sla_col_name in df.columns:
                sla_col_idx = df.columns.get_loc(sla_col_name)
                sla_formats = {
                    get_string('sla_met'): workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'}),
                    get_string('sla_violated'): workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                }
                for status_text, style_format in sla_formats.items():
                    worksheet.conditional_format(1, sla_col_idx, max_row, sla_col_idx, {
                        'type': 'cell', 'criteria': '==', 'value': f'"{status_text}"', 'format': style_format
                    })
            worksheet.freeze_panes(1, 0)

    def _add_charts_to_report(self, writer, report_data: dict):
        """Adds dashboard charts to the Excel report."""
        if 'Daily SLA Summary' not in report_data or 'Monthly Summary Data' not in report_data:
            self.progress.emit(get_string('log_warn_no_sla_data'))
            return

        workbook = writer.book

        daily_sheet_name = get_string('sheet_daily_sla')
        met_col, violated_col = get_string('col_met'), get_string('col_violated')
        percent_met_col = get_string('col_percent_met')

        daily_df_orig = report_data['Daily SLA Summary']
        worksheet = writer.sheets[daily_sheet_name]
        column_chart = workbook.add_chart({'type': 'column'})
        num_rows = len(daily_df_orig)

        daily_df = daily_df_orig.rename(columns={
            get_string('sla_met'): met_col,
            get_string('sla_violated'): violated_col,
            '% Met': percent_met_col,
            'Date': get_string('col_date')
        })

        column_chart.add_series({
            'name': [daily_sheet_name, 0, daily_df.columns.get_loc(met_col)],
            'categories': [daily_sheet_name, 1, 0, num_rows, 0],
            'values': [daily_sheet_name, 1, daily_df.columns.get_loc(met_col), num_rows,
                       daily_df.columns.get_loc(met_col)],
            'fill': {'color': '#00B050'},
        })
        column_chart.add_series({
            'name': [daily_sheet_name, 0, daily_df.columns.get_loc(violated_col)],
            'categories': [daily_sheet_name, 1, 0, num_rows, 0],
            'values': [daily_sheet_name, 1, daily_df.columns.get_loc(violated_col), num_rows,
                       daily_df.columns.get_loc(violated_col)],
            'fill': {'color': '#C00000'},
        })

        line_chart = workbook.add_chart({'type': 'line'})
        line_chart.add_series({
            'name': [daily_sheet_name, 0, daily_df.columns.get_loc(percent_met_col)],
            'categories': [daily_sheet_name, 1, 0, num_rows, 0],
            'values': [daily_sheet_name, 1, daily_df.columns.get_loc(percent_met_col), num_rows,
                       daily_df.columns.get_loc(percent_met_col)],
            'line': {'color': '#4472C4'},
            'y2_axis': True,
        })

        column_chart.combine(line_chart)
        column_chart.set_title({'name': get_string('chart_daily_sla_title')})
        column_chart.set_x_axis({'name': get_string('chart_daily_sla_x'), 'date_axis': True})
        column_chart.set_y_axis({'name': get_string('chart_daily_sla_y')})
        column_chart.set_y2_axis({'name': get_string('chart_daily_sla_y2'), 'min': 0, 'max': 100})
        worksheet.insert_chart('G2', column_chart, {'x_scale': 2.5, 'y_scale': 1.5})

        monthly_df = report_data['Monthly Summary Data']
        sheet_name = get_string('sheet_dashboard')
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.write_row('A1', monthly_df.columns)
        for r, row in enumerate(monthly_df.values):
            worksheet.write_row(r + 1, 0, row)
        num_rows = len(monthly_df)

        col_chart_monthly = workbook.add_chart({'type': 'column'})
        col_chart_monthly.add_series({
            'name': get_string('chart_monthly_bar_name'),
            'categories': [sheet_name, 1, 0, num_rows, 0],
            'values': [sheet_name, 1, 1, num_rows, 1],
            'points': [{'fill': {'color': '#00B050'}}, {'fill': {'color': '#C00000'}}],
        })
        col_chart_monthly.set_title({'name': get_string('chart_monthly_bar_title')})
        worksheet.insert_chart('D2', col_chart_monthly, {'x_scale': 1.5, 'y_scale': 1.5})

        pie_chart = workbook.add_chart({'type': 'pie'})
        pie_chart.add_series({
            'name': get_string('chart_monthly_pie_name'),
            'categories': [sheet_name, 1, 0, num_rows, 0],
            'values': [sheet_name, 1, 1, num_rows, 1],
            'points': [{'fill': {'color': '#00B050'}}, {'fill': {'color': '#C00000'}}],
            'data_labels': {'percentage': True, 'leader_lines': True},
        })
        pie_chart.set_title({'name': get_string('chart_monthly_pie_title')})
        worksheet.insert_chart('M2', pie_chart, {'x_scale': 1.5, 'y_scale': 1.5})