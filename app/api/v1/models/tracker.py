from electionguard.tracker import DEFAULT_SEPERATOR
from .base import Base

__all__ = [
    "TrackerWordsRequest",
    "TrackerWords",
    "TrackerHashRequest",
    "TrackerHash",
]


class TrackerWordsRequest(Base):
    tracker_hash: str
    seperator: str = DEFAULT_SEPERATOR


class TrackerWords(Base):
    tracker_words: str


class TrackerHashRequest(Base):
    tracker_words: str
    seperator: str = DEFAULT_SEPERATOR


class TrackerHash(Base):
    tracker_hash: str
