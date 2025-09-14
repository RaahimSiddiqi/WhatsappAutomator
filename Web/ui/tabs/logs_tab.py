from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox,
    QLabel, QMessageBox
)
from PyQt6.QtCore import pyqtSlot, QDateTime
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
from pathlib import Path
import logging


class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Info", "Warning", "Error", "Debug"])
        self.filter_combo.currentTextChanged.connect(self.filter_logs)
        controls_layout.addWidget(self.filter_combo)

        self.auto_scroll_checkbox = QPushButton("Auto-scroll")
        self.auto_scroll_checkbox.setCheckable(True)
        self.auto_scroll_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_scroll_checkbox)

        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)

        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs_dialog)
        controls_layout.addWidget(export_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
            }
        """)
        layout.addWidget(self.log_display)

        self.all_logs = []

    def setup_logging(self):
        self.log_handler = GuiLogHandler(self)
        self.log_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.log_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)

    def add_log(self, message: str, level: str = "info"):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message
        }
        self.all_logs.append(log_entry)

        if self.should_display_log(level):
            self.append_log_to_display(log_entry)

        if self.auto_scroll_checkbox.isChecked():
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )

    def append_log_to_display(self, log_entry: dict):
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        format_map = {
            'DEBUG': (QColor('#808080'), QFont.Weight.Normal),
            'INFO': (QColor('#d4d4d4'), QFont.Weight.Normal),
            'WARNING': (QColor('#ce9178'), QFont.Weight.Bold),
            'ERROR': (QColor('#f48771'), QFont.Weight.Bold),
            'CRITICAL': (QColor('#ff0000'), QFont.Weight.Bold)
        }

        level = log_entry['level']
        color, weight = format_map.get(level, (QColor('#d4d4d4'), QFont.Weight.Normal))

        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor('#608b4e'))
        cursor.insertText(f"[{log_entry['timestamp']}] ", timestamp_format)

        level_format = QTextCharFormat()
        level_format.setForeground(color)
        level_format.setFontWeight(weight)
        cursor.insertText(f"[{level}] ", level_format)

        message_format = QTextCharFormat()
        message_format.setForeground(QColor('#d4d4d4'))
        cursor.insertText(f"{log_entry['message']}\n", message_format)

    def should_display_log(self, level: str) -> bool:
        filter_text = self.filter_combo.currentText()
        if filter_text == "All":
            return True
        return level.upper() == filter_text.upper()

    @pyqtSlot(str)
    def filter_logs(self, filter_text: str):
        self.log_display.clear()

        for log_entry in self.all_logs:
            if filter_text == "All" or log_entry['level'] == filter_text.upper():
                self.append_log_to_display(log_entry)

    @pyqtSlot()
    def clear_logs(self):
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Are you sure you want to clear all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.all_logs.clear()
            self.log_display.clear()

    @pyqtSlot()
    def export_logs_dialog(self):
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"whatsapp_logs_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            self.export_logs(file_path)

    def export_logs(self, file_path: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for log_entry in self.all_logs:
                    file.write(
                        f"[{log_entry['timestamp']}] [{log_entry['level']}] "
                        f"{log_entry['message']}\n"
                    )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Logs exported successfully to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export logs: {str(e)}"
            )


class GuiLogHandler(logging.Handler):
    def __init__(self, logs_tab):
        super().__init__()
        self.logs_tab = logs_tab

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname.lower()
        self.logs_tab.add_log(msg, level)