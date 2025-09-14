#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from config import APP_NAME, APP_VERSION
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppAutomatorApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(APP_NAME)
        self.setApplicationDisplayName(f"{APP_NAME} v{APP_VERSION}")
        self.setOrganizationName("WhatsApp Automator")

        icon_path = Path(__file__).parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

        self.main_window = None

    def run(self):
        try:
            self.main_window = MainWindow()
            self.main_window.show()
            logger.info(f"{APP_NAME} started successfully")
            return self.exec()
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            return 1


def main():
    app = WhatsAppAutomatorApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()