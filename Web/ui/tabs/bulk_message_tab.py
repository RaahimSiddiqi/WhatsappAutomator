from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QGroupBox,
    QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QSpinBox, QProgressBar, QComboBox,
    QHeaderView, QDialog, QDialogButtonBox, QFormLayout,
    QSplitter, QMenu
)
from PyQt6.QtCore import pyqtSlot, Qt, QPoint
from PyQt6.QtGui import QAction
from pathlib import Path
from typing import List
import logging
from models.contact import Contact
from models.message import Message
from services.whatsapp_service import BulkSendWorker
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class BulkMessageTab(QWidget):
    def __init__(self, whatsapp_service):
        super().__init__()
        self.whatsapp_service = whatsapp_service
        self.contacts: List[Contact] = []
        self.bulk_worker = None
        self.attachments = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        contacts_group = QGroupBox("Contacts")
        contacts_layout = QVBoxLayout()

        import_layout = QHBoxLayout()
        import_csv_btn = QPushButton("Import CSV")
        import_csv_btn.clicked.connect(self.import_csv)
        import_layout.addWidget(import_csv_btn)

        import_excel_btn = QPushButton("Import Excel")
        import_excel_btn.clicked.connect(self.import_excel)
        import_layout.addWidget(import_excel_btn)

        add_manual_btn = QPushButton("Add Contact")
        add_manual_btn.clicked.connect(self.add_contact_manually)
        import_layout.addWidget(add_manual_btn)

        clear_contacts_btn = QPushButton("Clear All")
        clear_contacts_btn.clicked.connect(self.clear_contacts)
        import_layout.addWidget(clear_contacts_btn)

        export_btn = QPushButton("Export Contacts")
        export_btn.clicked.connect(self.export_contacts)
        import_layout.addWidget(export_btn)

        import_layout.addStretch()
        contacts_layout.addLayout(import_layout)

        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(4)
        self.contacts_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "Group"])
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.contacts_table.setAlternatingRowColors(True)
        self.contacts_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.contacts_table.customContextMenuRequested.connect(self.show_contact_context_menu)
        self.contacts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Remove maximum height to allow more rows
        contacts_layout.addWidget(self.contacts_table)

        self.contacts_count_label = QLabel("Total contacts: 0")
        contacts_layout.addWidget(self.contacts_count_label)

        contacts_group.setLayout(contacts_layout)
        layout.addWidget(contacts_group)

        message_group = QGroupBox("Message")
        message_layout = QVBoxLayout()

        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("No Template")
        self.load_templates()
        self.template_combo.currentTextChanged.connect(self.load_template)
        template_layout.addWidget(self.template_combo)
        message_layout.addLayout(template_layout)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText(
            "Enter your message here...\n\n"
            "Placeholders:\n"
            "%NAME% - Contact's name\n"
            "%PHONE% - Contact's phone\n"
            "%DATE% - Current date"
        )
        self.message_input.setMinimumHeight(150)
        message_layout.addWidget(self.message_input)

        attachments_layout = QHBoxLayout()
        attach_btn = QPushButton("Add Attachments")
        attach_btn.clicked.connect(self.add_attachments)
        attachments_layout.addWidget(attach_btn)

        self.attachments_label = QLabel("No attachments")
        attachments_layout.addWidget(self.attachments_label)

        clear_attach_btn = QPushButton("Clear Attachments")
        clear_attach_btn.clicked.connect(self.clear_attachments)
        attachments_layout.addWidget(clear_attach_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings_dialog)
        attachments_layout.addWidget(settings_btn)

        attachments_layout.addStretch()
        message_layout.addLayout(attachments_layout)

        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        # Initialize sending settings (hidden by default in dialog)
        self.country_code = ""
        self.delay_seconds = 5

        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Ready to send")
        progress_layout.addWidget(self.progress_label)

        self.results_label = QLabel("")
        progress_layout.addWidget(self.results_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        action_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Bulk Send")
        self.start_btn.clicked.connect(self.start_bulk_send)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)
        action_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_bulk_send)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        action_layout.addWidget(self.stop_btn)

        layout.addLayout(action_layout)
        layout.addStretch()

    def load_templates(self):
        data_dir = Path("data/templates")
        if data_dir.exists():
            for template_file in data_dir.glob("*.txt"):
                self.template_combo.addItem(template_file.stem)

    @pyqtSlot(str)
    def load_template(self, template_name: str):
        if template_name == "No Template":
            return

        template_path = Path("data/templates") / f"{template_name}.txt"
        if template_path.exists():
            try:
                content = FileHandler.read_message_template(str(template_path))
                self.message_input.setText(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load template: {str(e)}")

    @pyqtSlot()
    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import CSV",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            self.import_contacts(file_path)

    @pyqtSlot()
    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        if file_path:
            self.import_contacts(file_path)

    def import_contacts(self, file_path: str):
        try:
            logger.info(f"Importing contacts from {file_path}")

            if file_path.endswith('.csv'):
                new_contacts = FileHandler.read_csv_contacts(file_path)
            else:
                new_contacts = FileHandler.read_excel_contacts(file_path)

            # Validate contacts before adding
            valid_contacts = []
            invalid_count = 0

            for contact in new_contacts:
                if not contact.phone:
                    logger.warning(f"Contact validation failed: Missing phone number for {contact.name or 'unnamed contact'}")
                    invalid_count += 1
                    continue

                if not FileHandler.validate_phone_number(contact.phone):
                    logger.warning(f"Contact validation failed: Invalid phone number format for {contact.name}: {contact.phone}")
                    invalid_count += 1
                    continue

                valid_contacts.append(contact)
                logger.debug(f"Contact added: {contact.name} ({contact.phone})")

            self.contacts.extend(valid_contacts)
            self.update_contacts_table()

            success_msg = f"Imported {len(valid_contacts)} contacts successfully!"
            if invalid_count > 0:
                success_msg += f"\n{invalid_count} contacts skipped due to invalid data."

            logger.info(f"Import complete: {len(valid_contacts)} valid, {invalid_count} invalid")

            QMessageBox.information(self, "Import Complete", success_msg)

        except Exception as e:
            logger.error(f"Failed to import contacts from {file_path}: {str(e)}")
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import contacts: {str(e)}"
            )

    @pyqtSlot()
    def add_contact_manually(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Contact")
        dialog.setModal(True)

        layout = QFormLayout()

        name_input = QLineEdit()
        phone_input = QLineEdit()
        email_input = QLineEdit()
        group_input = QLineEdit()

        layout.addRow("Name:", name_input)
        layout.addRow("Phone:", phone_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Group:", group_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            phone = phone_input.text().strip()
            name = name_input.text().strip()

            if not phone:
                logger.warning("Contact creation failed: No phone number provided")
                QMessageBox.warning(self, "Invalid Contact", "Phone number is required")
                return

            if not FileHandler.validate_phone_number(phone):
                logger.warning(f"Contact creation failed: Invalid phone number format: {phone}")
                QMessageBox.warning(self, "Invalid Phone", "Invalid phone number format")
                return

            contact = Contact(
                name=name,
                phone=phone,
                email=email_input.text().strip(),
                group=group_input.text().strip()
            )
            self.contacts.append(contact)
            self.update_contacts_table()
            logger.info(f"Contact manually added: {name or 'Unnamed'} ({phone})")

    @pyqtSlot()
    def clear_contacts(self):
        if not self.contacts:
            return

        reply = QMessageBox.question(
            self,
            "Clear Contacts",
            f"Are you sure you want to clear all {len(self.contacts)} contacts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            count = len(self.contacts)
            self.contacts.clear()
            self.update_contacts_table()
            logger.info(f"Cleared all {count} contacts")

    def show_contact_context_menu(self, position: QPoint):
        if not self.contacts_table.selectedItems():
            return

        menu = QMenu(self)

        # Get selected rows
        selected_rows = set()
        for item in self.contacts_table.selectedItems():
            selected_rows.add(item.row())

        # Delete action
        delete_action = QAction("Delete Selected", self)
        delete_action.triggered.connect(lambda: self.delete_selected_contacts(selected_rows))
        menu.addAction(delete_action)

        # Edit action
        if len(selected_rows) == 1:
            edit_action = QAction("Edit Contact", self)
            edit_action.triggered.connect(lambda: self.edit_contact(list(selected_rows)[0]))
            menu.addAction(edit_action)

        # Copy phone number
        copy_phone_action = QAction("Copy Phone Number(s)", self)
        copy_phone_action.triggered.connect(lambda: self.copy_phone_numbers(selected_rows))
        menu.addAction(copy_phone_action)

        menu.exec(self.contacts_table.mapToGlobal(position))

    def delete_selected_contacts(self, rows: set):
        if not rows:
            return

        # Get contacts to delete
        contacts_to_delete = []
        for row in sorted(rows, reverse=True):
            if row < len(self.contacts):
                contacts_to_delete.append(self.contacts[row])

        if len(contacts_to_delete) == 1:
            msg = f"Delete contact {contacts_to_delete[0].name or contacts_to_delete[0].phone}?"
        else:
            msg = f"Delete {len(contacts_to_delete)} selected contacts?"

        reply = QMessageBox.question(
            self,
            "Delete Contacts",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove contacts from list
            for contact in contacts_to_delete:
                self.contacts.remove(contact)
                logger.info(f"Contact deleted: {contact.name or 'Unnamed'} ({contact.phone})")

            self.update_contacts_table()
            logger.info(f"Deleted {len(contacts_to_delete)} contacts")

    def edit_contact(self, row: int):
        if row >= len(self.contacts):
            return

        contact = self.contacts[row]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Contact")
        dialog.setModal(True)

        layout = QFormLayout()

        name_input = QLineEdit(contact.name)
        phone_input = QLineEdit(contact.phone)
        email_input = QLineEdit(contact.email)
        group_input = QLineEdit(contact.group)

        layout.addRow("Name:", name_input)
        layout.addRow("Phone:", phone_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Group:", group_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            phone = phone_input.text().strip()

            if not phone:
                logger.warning("Contact edit failed: No phone number provided")
                QMessageBox.warning(self, "Invalid Contact", "Phone number is required")
                return

            if not FileHandler.validate_phone_number(phone):
                logger.warning(f"Contact edit failed: Invalid phone number format: {phone}")
                QMessageBox.warning(self, "Invalid Phone", "Invalid phone number format")
                return

            old_info = f"{contact.name or 'Unnamed'} ({contact.phone})"

            contact.name = name_input.text().strip()
            contact.phone = phone
            contact.email = email_input.text().strip()
            contact.group = group_input.text().strip()

            self.update_contacts_table()
            logger.info(f"Contact edited: {old_info} -> {contact.name or 'Unnamed'} ({contact.phone})")

    def copy_phone_numbers(self, rows: set):
        from PyQt6.QtWidgets import QApplication

        phones = []
        for row in rows:
            if row < len(self.contacts):
                phones.append(self.contacts[row].phone)

        if phones:
            QApplication.clipboard().setText("\n".join(phones))
            logger.debug(f"Copied {len(phones)} phone numbers to clipboard")

    @pyqtSlot()
    def export_contacts(self):
        if not self.contacts:
            QMessageBox.warning(self, "Warning", "No contacts to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Contacts",
            "contacts.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )

        if file_path:
            try:
                FileHandler.save_contacts_csv(self.contacts, file_path)
                QMessageBox.information(self, "Success", "Contacts exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export contacts: {str(e)}")

    def update_contacts_table(self):
        self.contacts_table.setRowCount(len(self.contacts))

        for i, contact in enumerate(self.contacts):
            self.contacts_table.setItem(i, 0, QTableWidgetItem(contact.name))
            self.contacts_table.setItem(i, 1, QTableWidgetItem(contact.phone))
            self.contacts_table.setItem(i, 2, QTableWidgetItem(contact.email))
            self.contacts_table.setItem(i, 3, QTableWidgetItem(contact.group))

        self.contacts_count_label.setText(f"Total contacts: {len(self.contacts)}")

    def show_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sending Settings")
        dialog.setModal(True)

        layout = QFormLayout()

        country_code_input = QLineEdit(self.country_code)
        country_code_input.setPlaceholderText("+1")
        layout.addRow("Country Code:", country_code_input)

        delay_spinbox = QSpinBox()
        delay_spinbox.setMinimum(1)
        delay_spinbox.setMaximum(60)
        delay_spinbox.setValue(self.delay_seconds)
        delay_spinbox.setSuffix(" seconds")
        layout.addRow("Delay between messages:", delay_spinbox)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.country_code = country_code_input.text().strip()
            self.delay_seconds = delay_spinbox.value()

    @pyqtSlot()
    def add_attachments(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Attachments",
            "",
            "All Files (*.*)"
        )
        if files:
            self.attachments.extend(files)
            self.attachments_label.setText(f"{len(self.attachments)} file(s) selected")

    @pyqtSlot()
    def clear_attachments(self):
        self.attachments.clear()
        self.attachments_label.setText("No attachments")

    @pyqtSlot()
    def start_bulk_send(self):
        if not self.contacts:
            QMessageBox.warning(self, "Warning", "No contacts loaded")
            return

        message_text = self.message_input.toPlainText().strip()
        if not message_text and not self.attachments:
            QMessageBox.warning(self, "Warning", "Please enter a message or add attachments")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Bulk Send",
            f"Are you sure you want to send messages to {len(self.contacts)} contacts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        message = Message(
            text=message_text,
            attachments=self.attachments.copy()
        )

        country_code = self.country_code
        delay = self.delay_seconds

        # Update headless setting before starting bulk send
        from PyQt6.QtCore import QSettings
        settings = QSettings("WhatsAppAutomator", "Settings")
        headless_enabled = settings.value("headless_mode", False) == "true"
        print(f"DEBUG: Bulk message - headless setting = {settings.value('headless_mode', False)}, enabled = {headless_enabled}")
        self.whatsapp_service.headless_enabled = headless_enabled

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting bulk send...")

        self.bulk_worker = BulkSendWorker(
            self.whatsapp_service,
            self.contacts,
            message,
            country_code,
            delay
        )

        self.bulk_worker.status_update.connect(self.update_status)
        self.bulk_worker.progress_update.connect(self.update_progress)
        self.bulk_worker.message_sent.connect(self.on_message_sent)
        self.bulk_worker.completed.connect(self.on_bulk_complete)

        self.bulk_worker.start()

    @pyqtSlot()
    def stop_bulk_send(self):
        if self.bulk_worker:
            self.bulk_worker.stop()
            self.stop_btn.setEnabled(False)

    @pyqtSlot(str)
    def update_status(self, status: str):
        self.progress_label.setText(status)

    @pyqtSlot(int)
    def update_progress(self, progress: int):
        self.progress_bar.setValue(progress)

    @pyqtSlot(str, bool)
    def on_message_sent(self, phone: str, success: bool):
        status = "✓" if success else "✗"
        self.progress_label.setText(f"{status} {phone}")

    @pyqtSlot(int, int)
    def on_bulk_complete(self, successful: int, failed: int):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        self.results_label.setText(f"Completed: {successful} successful, {failed} failed")

        QMessageBox.information(
            self,
            "Bulk Send Complete",
            f"Bulk sending completed!\n\n"
            f"Successful: {successful}\n"
            f"Failed: {failed}"
        )