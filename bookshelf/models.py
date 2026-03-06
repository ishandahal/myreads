from dataclasses import dataclass, field
from datetime import datetime


VALID_STATUSES = ("want-to-read", "reading", "read")


@dataclass
class Book:
    title: str
    author: str
    status: str = "want-to-read"
    genre: str = ""
    notes: str = ""
    source: str = ""
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: int | None = None


class InvalidColumnError(Exception):
    pass


class BookNotFoundError(Exception):
    pass
