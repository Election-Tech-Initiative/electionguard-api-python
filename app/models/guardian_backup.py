from typing import Any, List

from .base import Base


class GuardianBackup(Base):
    id: str
    election_partial_key_backups: List[Any]
