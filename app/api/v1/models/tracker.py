from electionguard.tracker import DEFAULT_SEPERATOR
from .base import Base

__all__ = [
    "TrackerWordsRequest",
    "TrackerWords",
]


class TrackerWordsRequest(Base):
    tracker_hash: str
    seperator: str = DEFAULT_SEPERATOR


class TrackerWords(Base):
    tracker_words: str
