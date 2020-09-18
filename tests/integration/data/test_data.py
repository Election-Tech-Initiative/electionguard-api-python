from copy import deepcopy
from functools import lru_cache
import json
from typing import Any, Dict

# from electionguard.serializable import read_json_file

__all__ = ["get_ballot", "get_election_description"]

_DATA_DIRECTORY = "tests/integration/data"


def get_ballot(ballot_id: str) -> Any:
    ballot = deepcopy(_get_ballot_template())
    ballot["object_id"] = ballot_id
    return ballot


def get_election_description() -> Any:
    return deepcopy(_get_election_description_template())


def _get_ballot_template() -> Dict:
    return _read_json_file(f"{_DATA_DIRECTORY}/ballot.json")


@lru_cache
def _get_election_description_template() -> Dict:
    return _read_json_file(f"{_DATA_DIRECTORY}/election_description.json")


@lru_cache
def _read_json_file(path: str) -> Dict:
    with open(path, "r") as file:
        return json.load(file)
