from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QFileDialog,
    QMessageBox, QStatusBar, QToolBar, QSplitter, QMenu,
    QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QAction, QIcon
from pathlib import Path
import logging
from ui.tabs.single_message_tab import SingleMessageTab
from ui.tabs.bulk_message_tab import BulkMessageTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.logs_tab import LogsTab
from services.whatsapp_service import WhatsAppService
from config import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.whatsapp_service = WhatsAppService(self)
        self.full_status_text = ""  # Store full text for copying
        self.setup_ui()
        self.setup_connections()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)

        self.setup_menubar()
        self.setup_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumHeight(60)
        self.status_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.status_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.status_label.customContextMenuRequested.connect(self.show_status_context_menu)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.status_label)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        self.single_message_tab = SingleMessageTab(self.whatsapp_service)
        self.bulk_message_tab = BulkMessageTab(self.whatsapp_service)
        self.settings_tab = SettingsTab()
        self.logs_tab = LogsTab()

        self.tab_widget.addTab(self.single_message_tab, "Single Message")
        self.tab_widget.addTab(self.bulk_message_tab, "Bulk Messages")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.logs_tab, "Logs")

        main_layout.addWidget(self.tab_widget)

        self.setup_statusbar()

        self.apply_styles()

    def setup_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        import_contacts_action = QAction("Import Contacts", self)
        import_contacts_action.setShortcut("Ctrl+I")
        import_contacts_action.triggered.connect(self.import_contacts)
        file_menu.addAction(import_contacts_action)

        export_logs_action = QAction("Export Logs", self)
        export_logs_action.setShortcut("Ctrl+E")
        export_logs_action.triggered.connect(self.export_logs)
        file_menu.addAction(export_logs_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        whatsapp_menu = menubar.addMenu("WhatsApp")

        login_action = QAction("Login to WhatsApp", self)
        login_action.triggered.connect(self.login_whatsapp)
        whatsapp_menu.addAction(login_action)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout_whatsapp)
        whatsapp_menu.addAction(logout_action)

        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        login_action = QAction("Login", self)
        login_action.triggered.connect(self.login_whatsapp)
        toolbar.addAction(login_action)

        toolbar.addSeparator()

        send_single_action = QAction("Send Single", self)
        send_single_action.triggered.connect(self.send_single_message)
        toolbar.addAction(send_single_action)

        send_bulk_action = QAction("Send Bulk", self)
        send_bulk_action.triggered.connect(self.send_bulk_messages)
        toolbar.addAction(send_bulk_action)

        toolbar.addSeparator()

        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_sending)
        toolbar.addAction(stop_action)

    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: red;
                font-weight: bold;
                padding: 0 10px;
            }
        """)

        self.progress_label = QLabel("No tasks running")

        self.status_bar.addWidget(self.connection_status)
        self.status_bar.addWidget(self.progress_label)

    def setup_connections(self):
        self.whatsapp_service.status_update.connect(self.update_status)
        self.whatsapp_service.logged_in.connect(self.on_logged_in)
        self.whatsapp_service.login_required.connect(self.on_login_required)
        self.whatsapp_service.error_occurred.connect(self.on_error)
        self.whatsapp_service.progress_update.connect(self.update_progress)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #25D366;
            }
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
            QPushButton:pressed {
                background-color: #075E54;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

    @pyqtSlot()
    def login_whatsapp(self):
        self.status_label.setText("Logging in to WhatsApp...")
        self.whatsapp_service.login()

    @pyqtSlot()
    def logout_whatsapp(self):
        reply = QMessageBox.question(
            self,
            "Logout Confirmation",
            "Are you sure you want to logout from WhatsApp?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.whatsapp_service.close()
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("QLabel { color: red; font-weight: bold; padding: 0 10px; }")
            self.status_label.setText("Logged out")

    @pyqtSlot()
    def send_single_message(self):
        self.tab_widget.setCurrentWidget(self.single_message_tab)
        self.single_message_tab.send_message()

    @pyqtSlot()
    def send_bulk_messages(self):
        self.tab_widget.setCurrentWidget(self.bulk_message_tab)
        self.bulk_message_tab.start_bulk_send()

    @pyqtSlot()
    def stop_sending(self):
        self.whatsapp_service.stop_bulk_sending()
        self.bulk_message_tab.stop_bulk_send()

    @pyqtSlot()
    def import_contacts(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Contacts",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*.*)"
        )

        if file_path:
            self.bulk_message_tab.import_contacts(file_path)

    @pyqtSlot()
    def export_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            "whatsapp_logs.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            self.logs_tab.export_logs(file_path)

    @pyqtSlot(str)
    def update_status(self, status: str):
        # Store full text for copying
        self.full_status_text = status

        # Truncate very long messages to prevent UI issues
        if len(status) > 200:
            display_status = status[:197] + "..."
        else:
            display_status = status
        self.status_label.setText(display_status)
        self.status_label.setToolTip(status)  # Show full text on hover
        self.logs_tab.add_log(status)

    @pyqtSlot()
    def on_logged_in(self):
        self.connection_status.setText("Connected")
        self.connection_status.setStyleSheet("QLabel { color: green; font-weight: bold; padding: 0 10px; }")
        self.status_label.setText("Successfully logged in to WhatsApp")
        QMessageBox.information(self, "Success", "Successfully logged in to WhatsApp!")

    @pyqtSlot()
    def on_login_required(self):
        QMessageBox.information(
            self,
            "Login Required",
            "Please scan the QR code in the browser window to login to WhatsApp Web."
        )

    @pyqtSlot(str)
    def on_error(self, error: str):
        # Store full text for copying
        self.full_status_text = f"Error: {error}"

        # Truncate error message for status label
        if len(error) > 150:
            display_error = error[:147] + "..."
        else:
            display_error = error
        self.status_label.setText(f"Error: {display_error}")
        self.status_label.setToolTip(error)  # Show full error on hover
        self.logs_tab.add_log(f"ERROR: {error}", "error")

        # Also truncate for message box if extremely long
        if len(error) > 500:
            msgbox_error = error[:497] + "..."
        else:
            msgbox_error = error
        QMessageBox.critical(self, "Error", msgbox_error)

    @pyqtSlot(int)
    def update_progress(self, progress: int):
        self.progress_label.setText(f"Progress: {progress}%")

    def show_status_context_menu(self, position):
        menu = QMenu(self)

        # Copy truncated text action
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(self.status_label.text()))
        menu.addAction(copy_action)

        # Copy full text action
        copy_full_action = QAction("Copy Full Message", self)
        copy_full_action.triggered.connect(lambda: QApplication.clipboard().setText(self.full_status_text))
        menu.addAction(copy_full_action)

        # Clear status action
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(lambda: self.update_status("Ready"))
        menu.addAction(clear_action)

        menu.exec(self.status_label.mapToGlobal(position))

    @pyqtSlot()
    def show_about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "A professional WhatsApp automation tool built with PyQt6.\n\n"
            "Features:\n"
            "• Send single and bulk messages\n"
            "• Message personalization\n"
            "• Attachment support\n"
            "• Session persistence\n"
            "• Contact management\n\n"
            "© 2024 WhatsApp Automator"
        )

    @pyqtSlot()
    def show_documentation(self):
        QMessageBox.information(
            self,
            "Documentation",
            "For detailed documentation, please visit:\n"
            "https://github.com/your-repo/whatsapp-automator\n\n"
            "Quick Start:\n"
            "1. Click 'Login' to connect to WhatsApp Web\n"
            "2. Scan the QR code with your phone\n"
            "3. Import contacts or enter a phone number\n"
            "4. Compose your message\n"
            "5. Send!"
        )

    def load_settings(self):
        pass

    def save_settings(self):
        pass

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.save_settings()
            self.whatsapp_service.close()
            event.accept()
        else:
            event.ignore()