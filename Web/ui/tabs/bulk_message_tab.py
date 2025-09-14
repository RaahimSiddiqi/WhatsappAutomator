from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QGroupBox,
    QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QSpinBox, QProgressBar, QComboBox,
    QHeaderView
)
from PyQt6.QtCore import pyqtSlot, Qt
from pathlib import Path
from typing import List
from models.contact import Contact
from models.message import Message
from services.whatsapp_service import BulkSendWorker
from utils.file_handler import FileHandler


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
        self.contacts_table.setMaximumHeight(200)
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

        attachments_layout.addStretch()
        message_layout.addLayout(attachments_layout)

        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        settings_group = QGroupBox("Sending Settings")
        settings_layout = QHBoxLayout()

        settings_layout.addWidget(QLabel("Country Code:"))
        self.country_code_input = QLineEdit()
        self.country_code_input.setPlaceholderText("+1")
        self.country_code_input.setMaximumWidth(60)
        settings_layout.addWidget(self.country_code_input)

        settings_layout.addWidget(QLabel("Delay (seconds):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(1)
        self.delay_spinbox.setMaximum(60)
        self.delay_spinbox.setValue(5)
        settings_layout.addWidget(self.delay_spinbox)

        settings_layout.addStretch()
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

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
            if file_path.endswith('.csv'):
                new_contacts = FileHandler.read_csv_contacts(file_path)
            else:
                new_contacts = FileHandler.read_excel_contacts(file_path)

            self.contacts.extend(new_contacts)
            self.update_contacts_table()

            QMessageBox.information(
                self,
                "Success",
                f"Imported {len(new_contacts)} contacts successfully!"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import contacts: {str(e)}"
            )

    @pyqtSlot()
    def add_contact_manually(self):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

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
            if phone:
                contact = Contact(
                    name=name_input.text().strip(),
                    phone=phone,
                    email=email_input.text().strip(),
                    group=group_input.text().strip()
                )
                self.contacts.append(contact)
                self.update_contacts_table()

    @pyqtSlot()
    def clear_contacts(self):
        self.contacts.clear()
        self.update_contacts_table()

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

        country_code = self.country_code_input.text().strip()
        delay = self.delay_spinbox.value()

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