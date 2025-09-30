# translations.py
import locale

# Dicionário com todas as strings da UI e do relatório em ambos os idiomas
LANGUAGES = {
    'pt_BR': {
        # Títulos
        'window_title': "Gerador de Relatórios Avançado do Zabbix",
        'config_group': "Configurações do Relatório",
        'severity_group': "Filtro de Severidade (incluir no relatório)",
        'output_group': "Local de Saída",
        'about_title': "Sobre a Ferramenta",
        'update_available_title': "Atualização Disponível",
        'validation_error_title': "Erro de Validação",
        'permission_error_title': "Erro de Permissão",
        'connection_error_title': "Erro de Conexão",
        'process_finished_title': "Processo Concluído",
        'process_error_title': "Erro no Processo",
        'update_error_title': "Erro na Atualização",
        'run_executable_title': "Selecionar Executável",
        'run_dialog_title': "Executar",
        'import_error_title': "Erro de Importação",
        'execution_error_title': "Erro ao Executar",

        # Labels e Botões
        'zabbix_api_url': "URL da API Zabbix:",
        'zabbix_api_token': "Token da API Zabbix:",
        'report_period': "Período do Relatório:",
        'year': "Ano:",
        'month': "Mês:",
        'ack_sla': "SLA para Acknowledgement:",
        'browse_button': "Procurar...",
        'generate_button': "Gerar Relatório",
        'generating_button': "Gerando...",
        'validating_button': "Validando...",
        'updating_button': "Atualizando...",
        'run_dialog_label': 'Digite o nome de um programa, pasta, documento ou recurso da Internet e o Windows o abrirá para você.',
        'sla_suffix': " minutos",
        'url_placeholder': "https://zabbix.suaempresa.com/api_jsonrpc.php",

        # Menus
        'file_menu': "&Arquivo",
        'run_menu': "Executar...",
        'exit_menu': "Sair",
        'help_menu': "&Ajuda",
        'check_updates_menu': "Verificar Atualizações...",
        'about_menu': "Sobre...",

        # Cabeçhalho
        'app_subtitle': "Uma ferramenta para extrair e analisar dados de SLA do Zabbix.",
        'app_version_display': "Versão {version}",

        # Mensagens de Diálogo e Status
        'about_text': """
            <b>Gerador de Relatórios Avançado do Zabbix</b><br>
            <b>Sua Versão:</b> {version}<br><br>
            Esta ferramenta conecta-se à API do Zabbix para gerar relatórios completos em Excel, incluindo análises de SLA e dashboards visuais.
            <br><br>
            <b>Desenvolvido por:</b> Lucas Bonfim de Oliveira Lima<br>
            <b>LinkedIn:</b> <a href="https://www.linkedin.com/in/soulucasbonfim">linkedin.com/in/soulucasbonfim</a>
        """,
        'update_available_text': "Uma nova versão ({latest_version}) está disponível!\nVocê está usando a versão {current_version}.\n\nDeseja atualizar agora?",
        'update_changelog_text': "Novidades da versão:\n\n{changelog}",
        'url_token_empty': "A URL e o Token da API não podem estar vazios.",
        'url_invalid': "A URL da API é inválida. Ela deve começar com 'http://' ou 'https://'.",
        'no_severity_selected': "Selecione pelo menos uma severidade.",
        'cannot_access_output_dir': "Não foi possível criar ou acessar o diretório de saída:\n{error}",
        'zabbix_connection_failed': "Não foi possível conectar à API do Zabbix.\n\nDetalhes: {error}",
        'connection_successful': "Conexão bem-sucedida. ✔️",
        'import_error_message': "Não foi possível carregar um componente essencial: {error}\n\nCertifique-se que os arquivos report_logic.py, updater.py e translations.py estão na mesma pasta.",
        'execution_error_message': "Não foi possível executar o comando:\n{error}",

        # Mensagens de Erro Aprimoradas
        'zabbix_auth_error_friendly': 'Erro de Autenticação: O Token da API é inválido ou expirou. Por favor, verifique o token e tente novamente.',
        'zabbix_generic_api_error': 'Erro na API do Zabbix: {details}',
        'unexpected_error_details': 'Ocorreu um erro inesperado. Verifique os logs para detalhes. Erro: {error}',
        'zabbix_api_call_error': "Ao chamar '{method}': {error_message}",
        'zabbix_connection_call_error': "Erro de conexão ao chamar a API do Zabbix: {error}",

        # Lógica do Relatório (Logs e Nomes de Arquivo)
        'log_starting': "Iniciando a geração do relatório...",
        'log_checking_updates': "Verificando atualizações...",
        'log_executing_command': "Executando comando: {command}",
        'log_no_events': "Nenhum evento encontrado para o período e severidades selecionados. Encerrando.",
        'log_events_found': "Total de eventos encontrados: {count}.",
        'log_fetching_days': "Buscando eventos de {start_date} a {end_date}...",
        'log_fetching_day_progress': "Buscando dia {day_num}/{total_days}: {date}",
        'log_fetching_recoveries': "Buscando detalhes de {count} eventos de recuperação...",
        'log_fetching_hosts': "Buscando nomes para {count} hosts...",
        'log_fetching_users': "Buscando nomes para {count} usuários...",
        'log_processing_events': "Processando eventos e construindo relatórios...",
        'log_preparing_data': "Preparando dados e convertendo datas para os relatórios...",
        'log_generating_sla': "Gerando relatórios de análise de SLA...",
        'log_warn_no_acks': "Aviso: Nenhum evento com acknowledgement encontrado para gerar relatórios de SLA.",
        'log_no_data': "Nenhum dado disponível para gerar um relatório.",
        'log_saving_report': "Salvando relatório consolidado em Excel com gráficos...",
        'log_report_saved': "Relatório completo com dashboards exportado para: {outfile}",
        'log_process_complete': "✅ Processo concluído em {seconds:.2f} segundos.",
        'log_success_message': "Relatório gerado com sucesso em {path}",
        'log_warn_empty_sheet': "Aviso: Pulando aba vazia: {sheet_name}",
        'log_warn_no_sla_data': "Aviso: Pulando geração de gráficos pois os dados de SLA estão ausentes.",
        'log_success_prefix': "SUCESSO:",
        'log_error_prefix': "ERRO:",
        'log_testing_connection': "Testando conexão com {url}...",
        'log_timestamp_format': "[%H:%M:%S]",

        # Mapas e Formatos
        'sev_not_classified': "Não classificado", 'sev_information': "Informação", 'sev_warning': "Atenção",
        'sev_average': "Média", 'sev_high': "Alta", 'sev_disaster': "Desastre",
        'ack_close_problem': "Fechar Problema", 'ack_acknowledge_event': "Reconhecer Evento",
        'ack_add_comment': "Adicionar Comentário", 'ack_change_severity': "Mudar Severidade",
        'ack_unknown': "Ação Desconhecida",
        'user_id_prefix': "ID:",
        'user_display_format': "{name} {surname} ({alias})",
        'user_alias_fallback': "sem_alias",
        'action_separator': ' + ',
        'tag_separator': '; ',
        'messages_sent_format': "Mensagens enviadas: {count}",

        # Valores de Células
        'status_resolved': "Resolvido", 'status_problem': "Problema",
        'ack_yes': "Sim", 'ack_no': "Não",
        'sla_met': "Dentro do SLA", 'sla_violated': "Fora do SLA",
        'not_applicable': "N/A",

        # Nomes de Planilhas e Colunas
        'sheet_problems': "Problemas", 'sheet_actions': "Ações", 'sheet_sla_details': "Detalhes SLA",
        'sheet_daily_sla': "SLA Diário", 'sheet_daily_volume': "Volume Diário de Eventos",
        'sheet_top_10': "Top 10 Problemas", 'sheet_user_prod': "Produtividade por Usuário",
        'sheet_dashboard': "Dashboard Mensal",
        'col_event_id': "ID do Evento", 'col_time': "Hora", 'col_severity': "Severidade",
        'col_recovery_time': "Hora da Recuperação", 'col_status': "Status", 'col_host': "Host",
        'col_problem': "Problema", 'col_duration': "Duração", 'col_ack': "Reconhecido",
        'col_first_ack_time': "Hora 1º Recon.", 'col_first_ack_user': "Usuário 1º Recon.",
        'col_actions': "Ações", 'col_tags': "Tags", 'col_event_time': "Hora do Evento",
        'col_user': "Usuário", 'col_action_type': "Tipo da Ação", 'col_message': "Mensagem",
        'col_ack_time': "Hora da Ação", 'col_ack_duration_min': "Duração Recon. (min)",
        'col_sla_status': "Status SLA", 'col_date': "Data", 'col_met': "Dentro do SLA",
        'col_violated': "Fora do SLA", 'col_total_acks': "Total Recon.",
        'col_percent_met': "% Dentro do SLA", 'col_total_events': "Total de Eventos",
        'col_count': "Contagem", 'col_sla_violations': "Violações de SLA",
        'report_filename_prefix': "relatorio_zabbix_completo",

        # Gráficos
        'chart_daily_sla_title': "Tendência Diária de SLA", 'chart_daily_sla_x': "Data",
        'chart_daily_sla_y': "Contagem de Eventos", 'chart_daily_sla_y2': "% Dentro do SLA",
        'chart_monthly_bar_title': "Resumo Mensal de SLA (Contagem)", 'chart_monthly_bar_name': "Contagem SLA Mensal",
        'chart_monthly_pie_title': "Distribuição Mensal de SLA", 'chart_monthly_pie_name': "Percentual SLA Mensal",

        # Códigos de Status do Updater
        'UPDATE_OK_UPTODATE': "Você já está com a versão mais recente.",
        'UPDATE_ERR_CONFIG': "Sistema de atualização não configurado. Verificação ignorada.",
        'UPDATE_ERR_NETWORK': "Erro de rede ao verificar atualizações: {details}",
        'UPDATE_ERR_UNEXPECTED': "Erro inesperado na verificação: {details}",
        'UPDATE_DOWNLOAD_FAILED': "Falha no download da atualização: {details}",
        'UPDATE_RESTARTING': "Atualização baixada. A aplicação será reiniciada.",

        # Script do Updater (.bat)
        'UPDATER_SCRIPT_ECHO_OFF': "@echo off",
        'UPDATER_SCRIPT_WAIT': "echo Aguardando o aplicativo fechar...",
        'UPDATER_SCRIPT_TIMEOUT': "timeout /t 2 /nobreak > NUL",
        'UPDATER_SCRIPT_REPLACING': "echo Substituindo o executavel antigo...",
        'UPDATER_SCRIPT_DELETE': 'del "{old_exe}"',
        'UPDATER_SCRIPT_CHECK_DELETE': 'if exist "{old_exe}" (',
        'UPDATER_SCRIPT_DELETE_ERROR': "    echo Nao foi possivel deletar o arquivo antigo. Abortando.",
        'UPDATER_SCRIPT_PAUSE': "    pause",
        'UPDATER_SCRIPT_EXIT': "    exit",
        'UPDATER_SCRIPT_END_CHECK': ")",
        'UPDATER_SCRIPT_RENAME': 'ren "{new_exe}" "{basename}"',
        'UPDATER_SCRIPT_STARTING_NEW': "echo Iniciando a nova versao...",
        'UPDATER_SCRIPT_START': 'start "" "{old_exe}"',
        'UPDATER_SCRIPT_CLEANING': "echo Limpando...",
        'UPDATER_SCRIPT_DELETE_SELF': 'del "%~f0"',
    },
    'en_US': {
        # Titles
        'window_title': "Zabbix Advanced Report Generator",
        'config_group': "Report Settings",
        'severity_group': "Severity Filter (include in report)",
        'output_group': "Output Location",
        'about_title': "About",
        'update_available_title': "Update Available",
        'validation_error_title': "Validation Error",
        'permission_error_title': "Permission Error",
        'connection_error_title': "Connection Error",
        'process_finished_title': "Process Finished",
        'process_error_title': "Process Error",
        'update_error_title': "Update Error",
        'run_executable_title': "Select Executable",
        'run_dialog_title': "Run",
        'import_error_title': "Import Error",
        'execution_error_title': "Execution Error",

        # Labels & Buttons
        'zabbix_api_url': "Zabbix API URL:",
        'zabbix_api_token': "Zabbix API Token:",
        'report_period': "Report Period:",
        'year': "Year:",
        'month': "Month:",
        'ack_sla': "SLA for Acknowledgement:",
        'browse_button': "Browse...",
        'generate_button': "Generate Report",
        'generating_button': "Generating...",
        'validating_button': "Validating...",
        'updating_button': "Updating...",
        'run_dialog_label': 'Type the name of a program, folder, document, or Internet resource, and Windows will open it for you.',
        'sla_suffix': " minutes",
        'url_placeholder': "https://zabbix.yourcompany.com/api_jsonrpc.php",

        # Menus
        'file_menu': "&File",
        'run_menu': "Run...",
        'exit_menu': "Exit",
        'help_menu': "&Help",
        'check_updates_menu': "Check for Updates...",
        'about_menu': "About...",

        # Header
        'app_subtitle': "A tool to extract and analyze SLA data from Zabbix.",
        'app_version_display': "Version {version}",

        # Dialog Messages & Status
        'about_text': """
            <b>Zabbix Advanced Report Generator</b><br>
            <b>Your Version:</b> {version}<br><br>
            This tool connects to the Zabbix API to generate comprehensive Excel reports, including SLA analysis and visual dashboards.
            <br><br>
            <b>Developed by:</b> Lucas Bonfim de Oliveira Lima<br>
            <b>LinkedIn:</b> <a href="https://www.linkedin.com/in/soulucasbonfim">linkedin.com/in/soulucasbonfim</a>
        """,
        'update_available_text': "A new version ({latest_version}) is available!\nYou are using version {current_version}.\n\nDo you want to update now?",
        'update_changelog_text': "Release notes:\n\n{changelog}",
        'url_token_empty': "The API URL and Token cannot be empty.",
        'url_invalid': "The API URL is invalid. It must start with 'http://' or 'https://'.",
        'no_severity_selected': "Please select at least one severity.",
        'cannot_access_output_dir': "Could not create or access the output directory:\n{error}",
        'zabbix_connection_failed': "Could not connect to the Zabbix API.\n\nDetails: {error}",
        'connection_successful': "Connection successful. ✔️",
        'import_error_message': "Could not load an essential component: {error}\n\nPlease ensure that report_logic.py, updater.py, and translations.py are in the same folder.",
        'execution_error_message': "Could not execute the command:\n{error}",

        # Enhanced Error Messages
        'zabbix_auth_error_friendly': 'Authentication Error: The API Token is invalid or has expired. Please check the token and try again.',
        'zabbix_generic_api_error': 'Zabbix API Error: {details}',
        'unexpected_error_details': 'An unexpected error occurred. Please check the logs for details. Error: {error}',
        'zabbix_api_call_error': "While calling '{method}': {error_message}",
        'zabbix_connection_call_error': "Connection error while calling Zabbix API: {error}",

        # Report Logic (Logs & Filenames)
        'log_starting': "Starting report generation...",
        'log_checking_updates': "Checking for updates...",
        'log_executing_command': "Executing command: {command}",
        'log_no_events': "No events found for the selected period and severities. Exiting.",
        'log_events_found': "Total events found: {count}.",
        'log_fetching_days': "Fetching events from {start_date} to {end_date}...",
        'log_fetching_day_progress': "Fetching day {day_num}/{total_days}: {date}",
        'log_fetching_recoveries': "Fetching details for {count} recovery events...",
        'log_fetching_hosts': "Fetching names for {count} hosts...",
        'log_fetching_users': "Fetching names for {count} users...",
        'log_processing_events': "Processing events and building reports...",
        'log_preparing_data': "Preparing data and converting dates for reports...",
        'log_generating_sla': "Generating SLA analysis reports...",
        'log_warn_no_acks': "Warning: No acknowledged events found to generate SLA reports.",
        'log_no_data': "No data available to generate a report.",
        'log_saving_report': "Saving consolidated Excel report with charts...",
        'log_report_saved': "Full report with dashboards exported to: {outfile}",
        'log_process_complete': "✅ Process completed in {seconds:.2f} seconds.",
        'log_success_message': "Report generated successfully in {path}",
        'log_warn_empty_sheet': "Warning: Skipping empty sheet: {sheet_name}",
        'log_warn_no_sla_data': "Warning: Skipping chart generation as SLA data is missing.",
        'log_success_prefix': "SUCCESS:",
        'log_error_prefix': "ERROR:",
        'log_testing_connection': "Testing connection with {url}...",
        'log_timestamp_format': "[%H:%M:%S]",

        # Maps & Formats
        'sev_not_classified': "Not classified", 'sev_information': "Information", 'sev_warning': "Warning",
        'sev_average': "Average", 'sev_high': "High", 'sev_disaster': "Disaster",
        'ack_close_problem': "Close Problem", 'ack_acknowledge_event': "Acknowledge Event",
        'ack_add_comment': "Add Comment", 'ack_change_severity': "Change Severity", 'ack_unknown': "Unknown Action",
        'user_id_prefix': "ID:",
        'user_display_format': "{name} {surname} ({alias})",
        'user_alias_fallback': "no_alias",
        'action_separator': ' + ',
        'tag_separator': '; ',
        'messages_sent_format': "Messages sent: {count}",

        # Cell Values
        'status_resolved': "Resolved", 'status_problem': "Problem",
        'ack_yes': "Yes", 'ack_no': "No",
        'sla_met': "Met", 'sla_violated': "Violated",
        'not_applicable': "N/A",

        # Sheet and Column Names
        'sheet_problems': "Problems", 'sheet_actions': "Actions", 'sheet_sla_details': "SLA Details",
        'sheet_daily_sla': "Daily SLA Summary", 'sheet_daily_volume': "Daily Event Volume",
        'sheet_top_10': "Top 10 Problems", 'sheet_user_prod': "User Productivity",
        'sheet_dashboard': "Monthly Dashboard",
        'col_event_id': "EventID", 'col_time': "Time", 'col_severity': "Severity",
        'col_recovery_time': "Recovery Time", 'col_status': "Status", 'col_host': "Host",
        'col_problem': "Problem", 'col_duration': "Duration", 'col_ack': "Ack",
        'col_first_ack_time': "First Ack Time", 'col_first_ack_user': "First Ack User",
        'col_actions': "Actions", 'col_tags': "Tags", 'col_event_time': "Event Time",
        'col_user': "User", 'col_action_type': "Action Type", 'col_message': "Message",
        'col_ack_time': "Ack Time", 'col_ack_duration_min': "Ack Duration (min)",
        'col_sla_status': "SLA Status", 'col_date': "Date", 'col_met': "Met",
        'col_violated': "Violated", 'col_total_acks': "Total Acks",
        'col_percent_met': "% Met", 'col_total_events': "Total Events",
        'col_count': "Count", 'col_sla_violations': "SLA Violations",
        'report_filename_prefix': "zabbix_full_report",

        # Charts
        'chart_daily_sla_title': "Daily SLA Trend", 'chart_daily_sla_x': "Date",
        'chart_daily_sla_y': "Event Count", 'chart_daily_sla_y2': "Percentage (%) Met",
        'chart_monthly_bar_title': "Monthly SLA Summary (Count)", 'chart_monthly_bar_name': "Monthly SLA Count",
        'chart_monthly_pie_title': "Monthly SLA Distribution", 'chart_monthly_pie_name': "Monthly SLA Percentage",

        # Updater Status Codes
        'UPDATE_OK_UPTODATE': "You are already using the latest version.",
        'UPDATE_ERR_CONFIG': "Update system not configured. Check skipped.",
        'UPDATE_ERR_NETWORK': "Network error while checking for updates: {details}",
        'UPDATE_ERR_UNEXPECTED': "Unexpected error during update check: {details}",
        'UPDATE_DOWNLOAD_FAILED': "Failed to download the update: {details}",
        'UPDATE_RESTARTING': "Update downloaded. The application will now restart.",

        # Updater Script (.bat)
        'UPDATER_SCRIPT_ECHO_OFF': "@echo off",
        'UPDATER_SCRIPT_WAIT': "echo Waiting for the application to close...",
        'UPDATER_SCRIPT_TIMEOUT': "timeout /t 2 /nobreak > NUL",
        'UPDATER_SCRIPT_REPLACING': "echo Replacing the old executable...",
        'UPDATER_SCRIPT_DELETE': 'del "{old_exe}"',
        'UPDATER_SCRIPT_CHECK_DELETE': 'if exist "{old_exe}" (',
        'UPDATER_SCRIPT_DELETE_ERROR': "    echo Could not delete the old file. Aborting.",
        'UPDATER_SCRIPT_PAUSE': "    pause",
        'UPDATER_SCRIPT_EXIT': "    exit",
        'UPDATER_SCRIPT_END_CHECK': ")",
        'UPDATER_SCRIPT_RENAME': 'ren "{new_exe}" "{basename}"',
        'UPDATER_SCRIPT_STARTING_NEW': "echo Starting the new version...",
        'UPDATER_SCRIPT_START': 'start "" "{old_exe}"',
        'UPDATER_SCRIPT_CLEANING': "echo Cleaning up...",
        'UPDATER_SCRIPT_DELETE_SELF': 'del "%~f0"',
    }
}


def get_string(key, **kwargs):
    """
    Retorna a string traduzida para o idioma detectado.
    Permite formatação com .format(**kwargs).
    """
    if not hasattr(get_string, "strings"):
        lang_code, _ = locale.getdefaultlocale()
        if lang_code and lang_code.lower().startswith('pt'):
            lang_code = 'pt_BR'

        if lang_code not in LANGUAGES:
            lang_code = 'en_US'
        get_string.strings = LANGUAGES[lang_code]

    base_string = get_string.strings.get(key, f"<{key}>")
    return base_string.format(**kwargs)