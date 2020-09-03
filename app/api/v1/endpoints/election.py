from electionguard.election import ElectionDescription, ElectionConstants
from fastapi import APIRouter, HTTPException
from os.path import realpath, join
from typing import Any

router = APIRouter()

DATA_FOLDER_PATH = realpath(join(__file__, "../../../../data"))
DESCRIPTION_FILE = join(DATA_FOLDER_PATH, "election_description.json")
READ = "r"


@router.get("/constants")
def get_election_constants() -> Any:
    """
    Return the constants defined for an election
    """
    constants = ElectionConstants()
    return constants.to_json_object()


@router.get("/description")
def get_default_election_description() -> Any:
    """
    Return a default election description
    """
    with open(DESCRIPTION_FILE, READ) as description_file:
        result = description_file.read()
        description = ElectionDescription.from_json(result)
    if not description:
        raise HTTPException(
            status_code=500,
            detail="Default description not found",
        )
    return description
