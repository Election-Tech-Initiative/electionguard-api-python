from functools import lru_cache
from typing import Any
from electionguard.schema import get_election_description_schema

__all__ = ["get_description_schema"]


@lru_cache
def get_description_schema() -> Any:
    return get_election_description_schema()
