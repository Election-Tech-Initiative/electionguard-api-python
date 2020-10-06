from typing import Any
from electionguard.group import ElementModQ
from electionguard.serializable import read_json_object
from electionguard.tracker import tracker_hash_to_words
from fastapi import APIRouter, Body

from ..models import (
    TrackerWords,
    TrackerWordsRequest,
)
from ..tags import UTILITY

router = APIRouter()


@router.post("/words", tags=[UTILITY])
def convert_tracker_to_words(request: TrackerWordsRequest = Body(...)) -> Any:
    """
    Convert tracker from hash to human readable / friendly words
    """

    tracker_hash = read_json_object(request.tracker_hash, ElementModQ)
    tracker_words = tracker_hash_to_words(tracker_hash, request.seperator)
    return TrackerWords(tracker_words=tracker_words)
