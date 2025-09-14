from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QComboBox, QMessageBox
)
from PyQt6.QtCore import pyqtSlot, QSettings
from pathlib import Path
from utils.file_handler import FileHandler


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("WhatsAppAutomator", "Settings")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()

        country_layout = QHBoxLayout()
        country_layout.addWidget(QLabel("Default Country Code:"))
        self.country_code_input = QLineEdit()
        self.country_code_input.setPlaceholderText("+1")
        self.country_code_input.setMaximumWidth(100)
        country_layout.addWidget(self.country_code_input)
        country_layout.addStretch()
        general_layout.addLayout(country_layout)

        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Default Message Delay (seconds):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(1)
        self.delay_spinbox.setMaximum(300)
        self.delay_spinbox.setValue(5)
        delay_layout.addWidget(self.delay_spinbox)
        delay_layout.addStretch()
        general_layout.addLayout(delay_layout)

        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Page Load Timeout (seconds):"))
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setMinimum(10)
        self.timeout_spinbox.setMaximum(120)
        self.timeout_spinbox.setValue(30)
        timeout_layout.addWidget(self.timeout_spinbox)
        timeout_layout.addStretch()
        general_layout.addLayout(timeout_layout)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        browser_group = QGroupBox("Browser Settings")
        browser_layout = QVBoxLayout()

        self.headless_checkbox = QCheckBox("Run browser in headless mode")
        self.headless_checkbox.setToolTip("Run browser without GUI (not recommended for WhatsApp)")
        browser_layout.addWidget(self.headless_checkbox)

        self.persist_session_checkbox = QCheckBox("Persist login session")
        self.persist_session_checkbox.setChecked(True)
        self.persist_session_checkbox.setToolTip("Stay logged in between sessions")
        browser_layout.addWidget(self.persist_session_checkbox)

        self.auto_close_checkbox = QCheckBox("Auto-close browser after sending")
        browser_layout.addWidget(self.auto_close_checkbox)

        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Chrome Profile Directory:"))
        self.profile_dir_input = QLineEdit()
        self.profile_dir_input.setReadOnly(True)
        profile_layout.addWidget(self.profile_dir_input)

        browse_profile_btn = QPushButton("Browse")
        browse_profile_btn.clicked.connect(self.browse_profile_directory)
        profile_layout.addWidget(browse_profile_btn)

        browser_layout.addLayout(profile_layout)

        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)

        notification_group = QGroupBox("Notifications")
        notification_layout = QVBoxLayout()

        self.success_notification_checkbox = QCheckBox("Show success notifications")
        self.success_notification_checkbox.setChecked(True)
        notification_layout.addWidget(self.success_notification_checkbox)

        self.error_notification_checkbox = QCheckBox("Show error notifications")
        self.error_notification_checkbox.setChecked(True)
        notification_layout.addWidget(self.error_notification_checkbox)

        self.sound_notification_checkbox = QCheckBox("Enable sound notifications")
        notification_layout.addWidget(self.sound_notification_checkbox)

        notification_group.setLayout(notification_layout)
        layout.addWidget(notification_group)

        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout()

        data_dir_layout = QHBoxLayout()
        data_dir_layout.addWidget(QLabel("Data Directory:"))
        self.data_dir_input = QLineEdit()
        self.data_dir_input.setText(str(Path("data").absolute()))
        self.data_dir_input.setReadOnly(True)
        data_dir_layout.addWidget(self.data_dir_input)
        data_layout.addLayout(data_dir_layout)

        data_buttons_layout = QHBoxLayout()

        clear_cache_btn = QPushButton("Clear Browser Cache")
        clear_cache_btn.clicked.connect(self.clear_browser_cache)
        data_buttons_layout.addWidget(clear_cache_btn)

        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        data_buttons_layout.addWidget(clear_logs_btn)

        backup_btn = QPushButton("Backup Settings")
        backup_btn.clicked.connect(self.backup_settings)
        data_buttons_layout.addWidget(backup_btn)

        restore_btn = QPushButton("Restore Settings")
        restore_btn.clicked.connect(self.restore_settings)
        data_buttons_layout.addWidget(restore_btn)

        data_buttons_layout.addStretch()
        data_layout.addLayout(data_buttons_layout)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        action_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)
        action_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        action_layout.addWidget(reset_btn)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        layout.addStretch()

    @pyqtSlot()
    def browse_profile_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Chrome Profile Directory"
        )
        if directory:
            self.profile_dir_input.setText(directory)

    @pyqtSlot()
    def clear_browser_cache(self):
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "This will clear the browser cache and you may need to login again. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            profile_dir = Path.home() / ".whatsapp_automator" / "chrome_profile"
            if profile_dir.exists():
                import shutil
                try:
                    shutil.rmtree(profile_dir)
                    profile_dir.mkdir(parents=True, exist_ok=True)
                    QMessageBox.information(self, "Success", "Browser cache cleared successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to clear cache: {str(e)}")

    @pyqtSlot()
    def clear_logs(self):
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "This will clear all application logs. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            log_file = Path("whatsapp_automator.log")
            if log_file.exists():
                try:
                    log_file.unlink()
                    QMessageBox.information(self, "Success", "Logs cleared successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}")

    @pyqtSlot()
    def backup_settings(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Backup Settings",
            "settings_backup.json",
            "JSON Files (*.json)"
        )

        if file_path:
            settings_dict = self.get_settings_dict()
            try:
                FileHandler.save_settings(settings_dict, file_path)
                QMessageBox.information(self, "Success", "Settings backed up successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to backup settings: {str(e)}")

    @pyqtSlot()
    def restore_settings(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Restore Settings",
            "",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                settings_dict = FileHandler.load_settings(file_path)
                self.apply_settings_dict(settings_dict)
                self.save_settings()
                QMessageBox.information(self, "Success", "Settings restored successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore settings: {str(e)}")

    def get_settings_dict(self) -> dict:
        return {
            "country_code": self.country_code_input.text(),
            "default_delay": self.delay_spinbox.value(),
            "timeout": self.timeout_spinbox.value(),
            "headless_mode": self.headless_checkbox.isChecked(),
            "persist_session": self.persist_session_checkbox.isChecked(),
            "auto_close_browser": self.auto_close_checkbox.isChecked(),
            "success_notifications": self.success_notification_checkbox.isChecked(),
            "error_notifications": self.error_notification_checkbox.isChecked(),
            "sound_notifications": self.sound_notification_checkbox.isChecked()
        }

    def apply_settings_dict(self, settings: dict):
        self.country_code_input.setText(settings.get("country_code", ""))
        self.delay_spinbox.setValue(settings.get("default_delay", 5))
        self.timeout_spinbox.setValue(settings.get("timeout", 30))
        self.headless_checkbox.setChecked(settings.get("headless_mode", False))
        self.persist_session_checkbox.setChecked(settings.get("persist_session", True))
        self.auto_close_checkbox.setChecked(settings.get("auto_close_browser", False))
        self.success_notification_checkbox.setChecked(settings.get("success_notifications", True))
        self.error_notification_checkbox.setChecked(settings.get("error_notifications", True))
        self.sound_notification_checkbox.setChecked(settings.get("sound_notifications", False))

    @pyqtSlot()
    def save_settings(self):
        settings_dict = self.get_settings_dict()

        for key, value in settings_dict.items():
            self.settings.setValue(key, value)

        profile_dir = Path.home() / ".whatsapp_automator" / "chrome_profile"
        self.profile_dir_input.setText(str(profile_dir))

        QMessageBox.information(self, "Success", "Settings saved successfully!")

    @pyqtSlot()
    def load_settings(self):
        self.country_code_input.setText(self.settings.value("country_code", ""))
        self.delay_spinbox.setValue(int(self.settings.value("default_delay", 5)))
        self.timeout_spinbox.setValue(int(self.settings.value("timeout", 30)))
        self.headless_checkbox.setChecked(self.settings.value("headless_mode", False) == "true")
        self.persist_session_checkbox.setChecked(self.settings.value("persist_session", True) != "false")
        self.auto_close_checkbox.setChecked(self.settings.value("auto_close_browser", False) == "true")
        self.success_notification_checkbox.setChecked(self.settings.value("success_notifications", True) != "false")
        self.error_notification_checkbox.setChecked(self.settings.value("error_notifications", True) != "false")
        self.sound_notification_checkbox.setChecked(self.settings.value("sound_notifications", False) == "true")

        profile_dir = Path.home() / ".whatsapp_automator" / "chrome_profile"
        self.profile_dir_input.setText(str(profile_dir))

    @pyqtSlot()
    def reset_to_defaults(self):
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.country_code_input.setText("")
            self.delay_spinbox.setValue(5)
            self.timeout_spinbox.setValue(30)
            self.headless_checkbox.setChecked(False)
            self.persist_session_checkbox.setChecked(True)
            self.auto_close_checkbox.setChecked(False)
            self.success_notification_checkbox.setChecked(True)
            self.error_notification_checkbox.setChecked(True)
            self.sound_notification_checkbox.setChecked(False)
            self.save_settings()