# gui.py
import sys
import locale
import subprocess
from datetime import datetime
from pathlib import Path
import requests

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
                             QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout,
                             QWidget, QProgressBar, QInputDialog, QStyle)
from PyQt6.QtGui import QAction

try:
    from report_logic import SEVERITY_MAP, ReportGenerator
    from updater import Updater
    from translations import get_string
except ImportError as e:
    # Esta é a única mensagem que não pode usar get_string, pois a importação falhou
    QMessageBox.critical(None, "Import Error",
                         f"Could not load an essential component: {e}\n\n"
                         "Please ensure that report_logic.py, updater.py, and translations.py are in the same folder.")
    sys.exit(1)

__version__ = "1.1.1"


class ZabbixReportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_string('window_title'))
        self.setGeometry(100, 100, 800, 700)

        # Estilo aprimorado para o menu se parecer com botões
        self.setStyleSheet("""
            QMenuBar {
                background-color: #F0F0F0;
                padding: 2px;
                border-bottom: 1px solid #C0C0C0;
            }
            QMenuBar::item {
                padding: 5px 12px;
                background-color: transparent;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenuBar::item:selected {
                background-color: #D6D6D6;
                border: 1px solid #B0B0B0;
            }
            QMenuBar::item:pressed {
                background-color: #C0C0C0;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_menu_bar()
        self._init_ui()

        self.report_thread = None
        self.report_worker = None
        self.update_thread = None
        self.update_worker = None
        self.update_info = {}

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(get_string('file_menu'))

        run_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        run_action = QAction(run_icon, get_string('run_menu'), self)
        run_action.triggered.connect(self._run_command_dialog)
        file_menu.addAction(run_action)

        file_menu.addSeparator()

        exit_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton)
        exit_action = QAction(exit_icon, get_string('exit_menu'), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu(get_string('help_menu'))

        update_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        update_action = QAction(update_icon, get_string('check_updates_menu'), self)
        update_action.triggered.connect(self._check_for_updates)
        help_menu.addAction(update_action)

        about_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)
        about_action = QAction(about_icon, get_string('about_menu'), self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _show_about_dialog(self):
        QMessageBox.about(self, get_string('about_title'), get_string('about_text', version=__version__))

    def _init_ui(self):
        config_group = QGroupBox(get_string('config_group'))
        form_layout = QFormLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(get_string('url_placeholder'))
        form_layout.addRow(get_string('zabbix_api_url'), self.url_input)
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(get_string('zabbix_api_token'), self.token_input)

        date_container_widget = QWidget()
        date_layout = QHBoxLayout(date_container_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)

        current_year = datetime.now().year
        self.year_input = QSpinBox()
        self.year_input.setRange(2020, current_year + 5)
        self.year_input.setValue(current_year)

        self.month_input = QComboBox()
        # Use locale-aware month names
        months = [datetime(2000, i, 1).strftime('%B').capitalize() for i in range(1, 13)]
        self.month_input.addItems(months)
        self.month_input.setCurrentIndex(datetime.now().month - 1)

        date_layout.addWidget(QLabel(get_string('year')))
        date_layout.addWidget(self.year_input)
        date_layout.addSpacing(20)
        date_layout.addWidget(QLabel(get_string('month')))
        date_layout.addWidget(self.month_input)
        date_layout.addStretch()

        form_layout.addRow(get_string('report_period'), date_container_widget)

        self.sla_input = QSpinBox()
        self.sla_input.setRange(1, 999)
        self.sla_input.setValue(20)
        self.sla_input.setSuffix(get_string('sla_suffix'))
        form_layout.addRow(get_string('ack_sla'), self.sla_input)
        config_group.setLayout(form_layout)
        self.main_layout.addWidget(config_group)

        severity_group = QGroupBox(get_string('severity_group'))
        self.severity_checkboxes = {}
        severity_layout = QGridLayout()
        # Ensure SEVERITY_MAP is sorted by numeric key for consistent UI layout
        sorted_severities = sorted(SEVERITY_MAP.items(), key=lambda item: int(item[0]), reverse=True)
        row, col = 0, 0
        for code, name in sorted_severities:
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)
            self.severity_checkboxes[code] = checkbox
            severity_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 2: col = 0; row += 1
        severity_group.setLayout(severity_layout)
        self.main_layout.addWidget(severity_group)

        output_group = QGroupBox(get_string('output_group'))
        output_layout = QHBoxLayout()
        self.output_path_input = QLineEdit(str(Path.home() / "Documents\\Zabbix Reports"))
        browse_btn = QPushButton(get_string('browse_button'))
        browse_btn.clicked.connect(self._browse_folder)
        output_layout.addWidget(self.output_path_input)
        output_layout.addWidget(browse_btn)
        output_group.setLayout(output_layout)
        self.main_layout.addWidget(output_group)

        self.generate_btn = QPushButton(get_string('generate_button'))
        self.generate_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        self.generate_btn.clicked.connect(self._start_report_generation)
        self.main_layout.addWidget(self.generate_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)

        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet(
            "background-color: #2b2b2b; color: #a9b7c6; font-family: Consolas, monaco, monospace;")
        self.main_layout.addWidget(self.log_console)

    def _browse_folder(self):
        directory = QFileDialog.getExistingDirectory(self, get_string('output_group'))
        if directory: self.output_path_input.setText(directory)

    def _validate_inputs(self, config):
        if not config['url'] or not config['token']:
            QMessageBox.warning(self, get_string('validation_error_title'), get_string('url_token_empty'))
            return False
        if not (config['url'].startswith('http://') or config['url'].startswith('https://')):
            QMessageBox.warning(self, get_string('validation_error_title'), get_string('url_invalid'))
            return False
        if not config['severities']:
            QMessageBox.warning(self, get_string('validation_error_title'), get_string('no_severity_selected'))
            return False
        try:
            config['output_dir'].mkdir(parents=True, exist_ok=True)
            (config['output_dir'] / ".permission_test").touch()
            (config['output_dir'] / ".permission_test").unlink()
        except Exception as e:
            QMessageBox.critical(self, get_string('permission_error_title'),
                                 get_string('cannot_access_output_dir', error=e))
            return False
        try:
            self._update_log(get_string('log_testing_connection', url=config['url']))
            QApplication.processEvents()
            response = requests.post(config['url'],
                                     json={"jsonrpc": "2.0", "method": "apiinfo.version", "params": {}, "id": 1},
                                     verify=False, timeout=10)
            response.raise_for_status()
            if 'error' in response.json(): raise requests.exceptions.RequestException(response.json()['error']['data'])
            self._update_log(get_string('connection_successful'))
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, get_string('connection_error_title'),
                                 get_string('zabbix_connection_failed', error=e))
            return False
        return True

    def _start_report_generation(self):
        config = {'url': self.url_input.text().strip(), 'token': self.token_input.text().strip(),
                  'year': self.year_input.value(), 'month': self.month_input.currentIndex() + 1,
                  'sla_threshold': self.sla_input.value(),
                  'severities': [code for code, checkbox in self.severity_checkboxes.items() if checkbox.isChecked()],
                  'output_dir': Path(self.output_path_input.text().strip())}
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText(get_string('validating_button'))
        self.log_console.clear()
        if not self._validate_inputs(config):
            self._reset_ui()
            return
        self.generate_btn.setText(get_string('generating_button'))
        self.report_thread = QThread()
        self.report_worker = ReportGenerator(config)
        self.report_worker.moveToThread(self.report_thread)
        self.report_thread.started.connect(self.report_worker.run)
        self.report_worker.finished.connect(self._on_finished)
        self.report_worker.error.connect(self._on_error)
        self.report_worker.progress.connect(self._update_log)
        self.report_worker.finished.connect(self.report_thread.quit)
        self.report_worker.error.connect(self.report_thread.quit)
        self.report_thread.finished.connect(self.report_thread.deleteLater)
        self.report_worker.finished.connect(self.report_worker.deleteLater)
        self.report_worker.error.connect(self.report_worker.deleteLater)
        self.report_thread.start()

    def _update_log(self, message):
        timestamp = datetime.now().strftime(get_string('log_timestamp_format'))
        self.log_console.appendPlainText(f"{timestamp} {message}")

    def _on_finished(self, message):
        self._update_log(f"{get_string('log_success_prefix')} {message}")
        QMessageBox.information(self, get_string('process_finished_title'), message)
        self._reset_ui()

    def _on_error(self, message):
        self._update_log(f"{get_string('log_error_prefix')} {message}")
        QMessageBox.critical(self, get_string('process_error_title'), message)
        self._reset_ui()

    def _reset_ui(self):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText(get_string('generate_button'))
        self.report_thread = None
        self.report_worker = None

    def _check_for_updates(self):
        if self.update_thread and self.update_thread.isRunning(): return
        self._update_log(get_string('log_checking_updates'))
        self.update_thread = QThread()
        self.update_worker = Updater(current_version=__version__)
        self.update_worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_worker.check_for_updates)
        self.update_worker.check_finished.connect(self._on_update_check_finished)
        self.update_worker.status_update.connect(self._on_update_status)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_worker.check_finished.connect(self.update_worker.deleteLater)
        self.update_thread.start()

    def _on_update_check_finished(self, is_available, info):
        self.update_thread.quit()
        if is_available:
            self.update_info = info
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle(get_string('update_available_title'))
            msg_box.setText(get_string('update_available_text', latest_version=info.get("latest_version"),
                                      current_version=__version__))
            changelog_text = info.get("changelog", get_string('not_applicable'))
            msg_box.setDetailedText(get_string('update_changelog_text', changelog=changelog_text))
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if msg_box.exec() == QMessageBox.StandardButton.Yes: self._start_update_download()

    def _start_update_download(self):
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText(get_string('updating_button'))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.update_worker = Updater(current_version=__version__)
        self.update_worker.download_progress.connect(self.progress_bar.setValue)
        self.update_worker.status_update.connect(self._on_update_status)
        self.update_worker.apply_update(self.update_info.get("download_url"))

    def _on_update_status(self, code, details):
        message = get_string(code, details=details)
        self._update_log(message)
        if "ERR" in code:
            QMessageBox.critical(self, get_string('update_error_title'), message)
            self.progress_bar.setVisible(False)
            self._reset_ui()

    def _run_command_dialog(self):
        """Abre uma caixa de diálogo para executar um comando, como no Windows."""
        command, ok = QInputDialog.getText(self, get_string('run_dialog_title'), get_string('run_dialog_label'))
        if ok and command:
            try:
                subprocess.Popen(f'start {command}', shell=True)
                self._update_log(get_string('log_executing_command', command=command))
            except Exception as e:
                QMessageBox.critical(self, get_string('execution_error_title'),
                                     get_string('execution_error_message', error=e))


if __name__ == "__main__":
    # Define o locale para o padrão do sistema para obter nomes de meses corretos, etc.
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print("Warning: Could not set system default locale.")

    app = QApplication(sys.argv)
    window = ZabbixReportApp()
    window.show()
    sys.exit(app.exec())