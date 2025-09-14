import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from models.contact import Contact
from models.message import Message

logger = logging.getLogger(__name__)


class FileHandler:
    @staticmethod
    def read_csv_contacts(file_path: str) -> List[Contact]:
        contacts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    contact = Contact(
                        name=row.get('name', ''),
                        phone=row.get('phone', row.get('number', '')),
                        email=row.get('email', ''),
                        group=row.get('group', '')
                    )
                    if contact.phone:
                        contacts.append(contact)

            logger.info(f"Loaded {len(contacts)} contacts from {file_path}")
            return contacts

        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            raise

    @staticmethod
    def read_excel_contacts(file_path: str) -> List[Contact]:
        contacts = []
        try:
            df = pd.read_excel(file_path)

            phone_column = None
            name_column = None

            for col in df.columns:
                col_lower = col.lower()
                if 'phone' in col_lower or 'number' in col_lower or 'mobile' in col_lower:
                    phone_column = col
                if 'name' in col_lower:
                    name_column = col

            if not phone_column:
                raise ValueError("No phone/number column found in Excel file")

            for _, row in df.iterrows():
                contact = Contact(
                    name=str(row.get(name_column, '')) if name_column else '',
                    phone=str(row.get(phone_column, '')),
                    email=str(row.get('email', '')) if 'email' in df.columns else '',
                    group=str(row.get('group', '')) if 'group' in df.columns else ''
                )
                if contact.phone and contact.phone != 'nan':
                    contacts.append(contact)

            logger.info(f"Loaded {len(contacts)} contacts from {file_path}")
            return contacts

        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            raise

    @staticmethod
    def save_contacts_csv(contacts: List[Contact], file_path: str):
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'phone', 'email', 'group']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                for contact in contacts:
                    writer.writerow({
                        'name': contact.name,
                        'phone': contact.phone,
                        'email': contact.email,
                        'group': contact.group
                    })

            logger.info(f"Saved {len(contacts)} contacts to {file_path}")

        except Exception as e:
            logger.error(f"Error saving contacts to CSV: {str(e)}")
            raise

    @staticmethod
    def read_message_template(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logger.info(f"Loaded message template from {file_path}")
            return content

        except Exception as e:
            logger.error(f"Error reading message template: {str(e)}")
            raise

    @staticmethod
    def save_message_template(content: str, file_path: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"Saved message template to {file_path}")

        except Exception as e:
            logger.error(f"Error saving message template: {str(e)}")
            raise

    @staticmethod
    def load_settings(file_path: str = "settings.json") -> Dict[str, Any]:
        try:
            if Path(file_path).exists():
                with open(file_path, 'r') as file:
                    return json.load(file)
            return {}

        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            return {}

    @staticmethod
    def save_settings(settings: Dict[str, Any], file_path: str = "settings.json"):
        try:
            with open(file_path, 'w') as file:
                json.dump(settings, file, indent=4)
            logger.info(f"Settings saved to {file_path}")

        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            raise

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        cleaned = ''.join(filter(str.isdigit, phone))
        return 7 <= len(cleaned) <= 15

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        return ''.join(filter(str.isdigit, phone))

    @staticmethod
    def format_phone_number(phone: str, country_code: str = "") -> str:
        cleaned = FileHandler.clean_phone_number(phone)

        if country_code and not cleaned.startswith(country_code):
            cleaned = country_code + cleaned

        return cleaned