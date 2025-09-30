# updater.py
import os
import subprocess
import sys
import requests
from packaging import version
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from translations import get_string

VERSION_URL = "https://raw.githubusercontent.com/soulucasbonfim/Zabbix-Advanced-Report-Generator/main/version.json"

class Updater(QObject):
    check_finished = pyqtSignal(bool, dict)  # is_update_available, update_info
    download_progress = pyqtSignal(int)  # percentage
    status_update = pyqtSignal(str, str)  # code, details

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version

    def check_for_updates(self):
        if "YOUR_USERNAME" in VERSION_URL:
            self.status_update.emit("UPDATE_ERR_CONFIG", "")
            self.check_finished.emit(False, {})
            return

        try:
            response = requests.get(VERSION_URL, timeout=10, verify=False)
            response.raise_for_status()

            latest_info = response.json()
            latest_version_str = latest_info.get("latest_version")

            if version.parse(latest_version_str) > version.parse(self.current_version):
                self.check_finished.emit(True, latest_info)
            else:
                self.status_update.emit("UPDATE_OK_UPTODATE", "")
                self.check_finished.emit(False, {})

        except requests.RequestException as e:
            self.status_update.emit("UPDATE_ERR_NETWORK", str(e))
            self.check_finished.emit(False, {})
        except Exception as e:
            self.status_update.emit("UPDATE_ERR_UNEXPECTED", str(e))
            self.check_finished.emit(False, {})

    def apply_update(self, download_url):
        try:
            # Determina o caminho do executável, seja rodando via Python ou como .exe compilado
            current_exe = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            current_path = os.path.dirname(current_exe)
            base_name = os.path.basename(current_exe)
            new_exe_path = os.path.join(current_path, f"new_{base_name}")

            with requests.get(download_url, stream=True, timeout=300, verify=False) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0

                with open(new_exe_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.download_progress.emit(progress)

            self.download_progress.emit(100)
            self._create_updater_script(current_exe, new_exe_path)

            self.status_update.emit("UPDATE_RESTARTING", "")

            subprocess.Popen([os.path.join(current_path, "updater.bat")], shell=True)
            QTimer.singleShot(500, sys.exit)

        except Exception as e:
            self.status_update.emit("UPDATE_DOWNLOAD_FAILED", str(e))

    def _create_updater_script(self, old_exe, new_exe):
        script_path = os.path.join(os.path.dirname(old_exe), "updater.bat")
        basename = os.path.basename(old_exe)

        # Constrói o conteúdo do script usando o get_string para cada linha
        script_content = f"""
{get_string('UPDATER_SCRIPT_ECHO_OFF')}
{get_string('UPDATER_SCRIPT_WAIT')}
{get_string('UPDATER_SCRIPT_TIMEOUT')}
{get_string('UPDATER_SCRIPT_REPLACING')}
{get_string('UPDATER_SCRIPT_DELETE', old_exe=old_exe)}
{get_string('UPDATER_SCRIPT_CHECK_DELETE', old_exe=old_exe)}
{get_string('UPDATER_SCRIPT_DELETE_ERROR')}
{get_string('UPDATER_SCRIPT_PAUSE')}
{get_string('UPDATER_SCRIPT_EXIT')}
{get_string('UPDATER_SCRIPT_END_CHECK')}
{get_string('UPDATER_SCRIPT_RENAME', new_exe=new_exe, basename=basename)}
{get_string('UPDATER_SCRIPT_STARTING_NEW')}
{get_string('UPDATER_SCRIPT_START', old_exe=old_exe)}
{get_string('UPDATER_SCRIPT_CLEANING')}
{get_string('UPDATER_SCRIPT_DELETE_SELF')}
"""
        with open(script_path, "w", encoding='utf-8') as f:

            f.write(script_content)
