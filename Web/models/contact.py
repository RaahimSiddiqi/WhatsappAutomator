from dataclasses import dataclass
from typing import Optional


@dataclass
class Contact:
    phone: str
    name: str = ""
    email: str = ""
    group: str = ""
    custom_fields: Optional[dict] = None

    def __post_init__(self):
        if self.custom_fields is None:
            self.custom_fields = {}

        self.phone = self._clean_phone(self.phone)

    def _clean_phone(self, phone: str) -> str:
        return ''.join(filter(lambda x: x.isdigit() or x == '+', phone))

    def get_display_name(self) -> str:
        return self.name if self.name else self.phone

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'group': self.group,
            **self.custom_fields
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        return cls(
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            group=data.get('group', ''),
            custom_fields={k: v for k, v in data.items()
                         if k not in ['name', 'phone', 'email', 'group']}
        )

    def __str__(self) -> str:
        return f"{self.get_display_name()} ({self.phone})"

    def __repr__(self) -> str:
        return f"Contact(name='{self.name}', phone='{self.phone}', group='{self.group}')"