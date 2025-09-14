from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QGroupBox,
    QListWidget, QFileDialog, QMessageBox, QComboBox
)
from PyQt6.QtCore import pyqtSlot
from pathlib import Path
from models.contact import Contact
from models.message import Message
from services.whatsapp_service import WhatsAppService
from utils.file_handler import FileHandler


class SingleMessageTab(QWidget):
    def __init__(self, whatsapp_service: WhatsAppService):
        super().__init__()
        self.whatsapp_service = whatsapp_service
        self.attachments = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        contact_group = QGroupBox("Contact Information")
        contact_layout = QVBoxLayout()

        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Phone Number:"))
        self.country_code_input = QLineEdit()
        self.country_code_input.setPlaceholderText("+1")
        self.country_code_input.setMaximumWidth(60)
        phone_layout.addWidget(self.country_code_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        phone_layout.addWidget(self.phone_input)
        contact_layout.addLayout(phone_layout)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name (Optional):"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter contact name")
        name_layout.addWidget(self.name_input)
        contact_layout.addLayout(name_layout)

        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)

        message_group = QGroupBox("Message")
        message_layout = QVBoxLayout()

        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("No Template")
        self.load_templates()
        self.template_combo.currentTextChanged.connect(self.load_template)
        template_layout.addWidget(self.template_combo)

        save_template_btn = QPushButton("Save as Template")
        save_template_btn.clicked.connect(self.save_template)
        template_layout.addWidget(save_template_btn)
        message_layout.addLayout(template_layout)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText(
            "Enter your message here...\n\n"
            "You can use placeholders:\n"
            "%NAME% - Contact's name\n"
            "%PHONE% - Contact's phone\n"
            "%DATE% - Current date"
        )
        self.message_input.setMinimumHeight(200)
        message_layout.addWidget(self.message_input)

        placeholders_layout = QHBoxLayout()
        placeholders_layout.addWidget(QLabel("Insert:"))

        name_placeholder_btn = QPushButton("%NAME%")
        name_placeholder_btn.clicked.connect(lambda: self.insert_placeholder("%NAME%"))
        placeholders_layout.addWidget(name_placeholder_btn)

        phone_placeholder_btn = QPushButton("%PHONE%")
        phone_placeholder_btn.clicked.connect(lambda: self.insert_placeholder("%PHONE%"))
        placeholders_layout.addWidget(phone_placeholder_btn)

        date_placeholder_btn = QPushButton("%DATE%")
        date_placeholder_btn.clicked.connect(lambda: self.insert_placeholder("%DATE%"))
        placeholders_layout.addWidget(date_placeholder_btn)

        placeholders_layout.addStretch()
        message_layout.addLayout(placeholders_layout)

        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        attachments_group = QGroupBox("Attachments")
        attachments_layout = QVBoxLayout()

        attach_buttons_layout = QHBoxLayout()
        attach_image_btn = QPushButton("Add Image")
        attach_image_btn.clicked.connect(self.add_image_attachment)
        attach_buttons_layout.addWidget(attach_image_btn)

        attach_document_btn = QPushButton("Add Document")
        attach_document_btn.clicked.connect(self.add_document_attachment)
        attach_buttons_layout.addWidget(attach_document_btn)

        attach_video_btn = QPushButton("Add Video")
        attach_video_btn.clicked.connect(self.add_video_attachment)
        attach_buttons_layout.addWidget(attach_video_btn)

        clear_attachments_btn = QPushButton("Clear All")
        clear_attachments_btn.clicked.connect(self.clear_attachments)
        attach_buttons_layout.addWidget(clear_attachments_btn)

        attach_buttons_layout.addStretch()
        attachments_layout.addLayout(attach_buttons_layout)

        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(100)
        attachments_layout.addWidget(self.attachments_list)

        attachments_group.setLayout(attachments_layout)
        layout.addWidget(attachments_group)

        action_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send Message")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
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
        action_layout.addWidget(self.send_btn)

        clear_btn = QPushButton("Clear Form")
        clear_btn.clicked.connect(self.clear_form)
        action_layout.addWidget(clear_btn)

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
    def save_template(self):
        from PyQt6.QtWidgets import QInputDialog

        template_name, ok = QInputDialog.getText(
            self,
            "Save Template",
            "Enter template name:"
        )

        if ok and template_name:
            templates_dir = Path("data/templates")
            templates_dir.mkdir(parents=True, exist_ok=True)

            template_path = templates_dir / f"{template_name}.txt"
            try:
                FileHandler.save_message_template(
                    self.message_input.toPlainText(),
                    str(template_path)
                )
                self.template_combo.addItem(template_name)
                self.template_combo.setCurrentText(template_name)
                QMessageBox.information(self, "Success", "Template saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save template: {str(e)}")

    @pyqtSlot(str)
    def insert_placeholder(self, placeholder: str):
        cursor = self.message_input.textCursor()
        cursor.insertText(placeholder)

    @pyqtSlot()
    def add_image_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.gif *.webp)"
        )
        if file_path:
            self.attachments.append(file_path)
            self.attachments_list.addItem(Path(file_path).name)

    @pyqtSlot()
    def add_document_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.txt)"
        )
        if file_path:
            self.attachments.append(file_path)
            self.attachments_list.addItem(Path(file_path).name)

    @pyqtSlot()
    def add_video_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.wmv *.flv)"
        )
        if file_path:
            self.attachments.append(file_path)
            self.attachments_list.addItem(Path(file_path).name)

    @pyqtSlot()
    def clear_attachments(self):
        self.attachments.clear()
        self.attachments_list.clear()

    @pyqtSlot()
    def send_message(self):
        phone = self.phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Warning", "Please enter a phone number")
            return

        message_text = self.message_input.toPlainText().strip()
        if not message_text and not self.attachments:
            QMessageBox.warning(self, "Warning", "Please enter a message or add attachments")
            return

        if not FileHandler.validate_phone_number(phone):
            QMessageBox.warning(self, "Warning", "Invalid phone number format")
            return

        contact = Contact(
            phone=phone,
            name=self.name_input.text().strip()
        )

        message = Message(
            text=message_text,
            attachments=self.attachments.copy()
        )

        country_code = self.country_code_input.text().strip()

        self.send_btn.setEnabled(False)
        self.send_btn.setText("Sending...")

        success = self.whatsapp_service.send_message(contact, message, country_code)

        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send Message")

        if success:
            QMessageBox.information(self, "Success", "Message sent successfully!")
            if QMessageBox.question(
                self,
                "Clear Form",
                "Do you want to clear the form?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
                self.clear_form()

    @pyqtSlot()
    def clear_form(self):
        self.phone_input.clear()
        self.name_input.clear()
        self.message_input.clear()
        self.clear_attachments()
        self.template_combo.setCurrentIndex(0)