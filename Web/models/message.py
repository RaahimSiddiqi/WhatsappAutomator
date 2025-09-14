from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from config import PLACEHOLDER_NAME, PLACEHOLDER_PHONE, PLACEHOLDER_DATE


@dataclass
class Message:
    text: str
    attachments: List[str] = field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    template_name: str = ""

    def get_personalized_text(self, name: str = "", phone: str = "") -> str:
        personalized = self.text

        if PLACEHOLDER_NAME in personalized:
            personalized = personalized.replace(PLACEHOLDER_NAME, name if name else "Friend")

        if PLACEHOLDER_PHONE in personalized:
            personalized = personalized.replace(PLACEHOLDER_PHONE, phone)

        if PLACEHOLDER_DATE in personalized:
            personalized = personalized.replace(
                PLACEHOLDER_DATE,
                datetime.now().strftime("%Y-%m-%d")
            )

        return personalized

    def add_attachment(self, file_path: str):
        if file_path not in self.attachments:
            self.attachments.append(file_path)

    def remove_attachment(self, file_path: str):
        if file_path in self.attachments:
            self.attachments.remove(file_path)

    def clear_attachments(self):
        self.attachments.clear()

    def has_attachments(self) -> bool:
        return len(self.attachments) > 0

    def is_scheduled(self) -> bool:
        return self.scheduled_time is not None

    def should_send_now(self) -> bool:
        if not self.is_scheduled():
            return True
        return datetime.now() >= self.scheduled_time

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'attachments': self.attachments,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'template_name': self.template_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        scheduled_time = None
        if data.get('scheduled_time'):
            scheduled_time = datetime.fromisoformat(data['scheduled_time'])

        return cls(
            text=data.get('text', ''),
            attachments=data.get('attachments', []),
            scheduled_time=scheduled_time,
            template_name=data.get('template_name', '')
        )

    def __str__(self) -> str:
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Message: {preview}"

    def __repr__(self) -> str:
        return f"Message(text='{self.text[:30]}...', attachments={len(self.attachments)})"