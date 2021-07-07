from typing import Any, List, Optional, Tuple
import sys

from fastapi import APIRouter, Body, HTTPException, Request, status

from electionguard.ballot import (
    SubmittedBallot,
    CiphertextBallot,
    from_ciphertext_ballot,
)
from electionguard.ballot_box import BallotBoxState
from electionguard.ballot_validator import ballot_is_valid_for_election
from electionguard.election import CiphertextElectionContext
from electionguard.manifest import InternalManifest, Manifest
from electionguard.serializable import write_json_object

from ....core.ballot import (
    get_ballot,
    set_ballots,
    get_ballot_inventory,
    upsert_ballot_inventory,
)
from ....core.repository import get_repository, DataCollection
from ....core.settings import Settings
from ....core.queue import get_message_queue, IMessageQueue
from ..models import (
    BaseResponse,
    BaseQueryRequest,
    BaseBallotRequest,
    BallotInventory,
    BallotInventoryResponse,
    BallotQueryResponse,
    CastBallotsRequest,
    SpoilBallotsRequest,
    SubmitBallotsRequest,
    SubmitBallotsResponse,
    ValidateBallotRequest,
)
from ..tags import BALLOTS

router = APIRouter()


@router.get("", tags=[BALLOTS])
def fetch_ballot(
    request: Request, election_id: str, ballot_id: str
) -> BallotQueryResponse:
    """
    Fetch A Ballot for a specific election
    """
    ballot = get_ballot(election_id, ballot_id, request.app.state.settings)

    return BallotQueryResponse(
        election_id=election_id,
        ballots=[ballot],
    )


@router.get("", tags=[BALLOTS])
def fetch_ballot_inventory(
    request: Request, election_id: str
) -> BallotInventoryResponse:
    """
    Fetch A Ballot for a specific election
    """
    inventory = get_ballot_inventory(election_id, request.app.state.settings)

    return BallotInventoryResponse(
        inventory=inventory,
    )


@router.post("/find", tags=[BALLOTS])
def find_ballots(
    request: Request,
    election_id: str,
    skip: int = 0,
    limit: int = 100,
    data: BaseQueryRequest = Body(...),
) -> BallotQueryResponse:
    """
    Find Ballots.

    Search the repository for ballots that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    try:
        filter = write_json_object(data.filter) if data.filter else {}
        with get_repository(
            election_id, DataCollection.SUBMITTED_BALLOT, request.app.state.settings
        ) as repository:
            cursor = repository.find(filter, skip, limit)
            ballots: List[Any] = []
            for item in cursor:
                ballots.append(write_json_object(item))
            return BallotQueryResponse(ballots=ballots)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error


@router.post("/cast", tags=[BALLOTS], status_code=status.HTTP_202_ACCEPTED)
def cast_ballots(
    election_id: Optional[str] = None, request: CastBallotsRequest = Body(...)
) -> BaseResponse:
    """
    Cast ballot
    """
    manifest, context, election_id = _get_election_parameters(election_id, request)
    ballots = [
        from_ciphertext_ballot(
            CiphertextBallot.from_json_object(ballot), BallotBoxState.CAST
        )
        for ballot in request.ballots
    ]

    for ballot in ballots:
        validation_request = ValidateBallotRequest(
            ballot=ballot.to_json_object(), manifest=manifest, context=context
        )
        _validate_ballot(validation_request)

    return _submit_ballots(election_id, ballots)


@router.post("/spoil", tags=[BALLOTS], status_code=status.HTTP_202_ACCEPTED)
def spoil_ballots(
    election_id: Optional[str] = None, request: SpoilBallotsRequest = Body(...)
) -> BaseResponse:
    """
    Spoil ballot
    """
    manifest, context, election_id = _get_election_parameters(election_id, request)
    ballots = [
        from_ciphertext_ballot(
            CiphertextBallot.from_json_object(ballot), BallotBoxState.SPOILED
        )
        for ballot in request.ballots
    ]

    for ballot in ballots:
        validation_request = ValidateBallotRequest(
            ballot=ballot.to_json_object(), manifest=manifest, context=context
        )
        _validate_ballot(validation_request)

    return _submit_ballots(election_id, ballots)


@router.put("/submit", tags=[BALLOTS], status_code=status.HTTP_202_ACCEPTED)
def submit_ballots(
    request: Request,
    election_id: Optional[str] = None,
    data: SubmitBallotsRequest = Body(...),
) -> BaseResponse:
    """
    Submit ballots for an election.

    This method expects an `election_id` is provided either in the query string or the request body.
    If both are provied, the query string will override.
    """

    manifest, context, election_id = _get_election_parameters(
        election_id, data, request.app.state.settings
    )

    # Check each ballot's state and validate
    ballots = [SubmittedBallot.from_json_object(ballot) for ballot in data.ballots]
    for ballot in ballots:
        if ballot.state == BallotBoxState.UNKNOWN:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=f"Submitted ballot {ballot.object_id} must have a cast or spoil state",
            )
        validation_request = ValidateBallotRequest(
            ballot=ballot.to_json_object(), manifest=manifest, context=context
        )
        _validate_ballot(validation_request)

    return _submit_ballots(election_id, ballots, request.app.state.settings)


@router.post("/validate", tags=[BALLOTS])
def validate_ballot(
    request: ValidateBallotRequest = Body(...),
) -> BaseResponse:
    """
    Validate a ballot for the given election data
    """
    _validate_ballot(request)
    return BaseResponse(message="Ballot is valid for election")


def _get_election_parameters(
    election_id: Optional[str],
    request_data: BaseBallotRequest,
    settings: Settings = Settings(),
) -> Tuple[Manifest, CiphertextElectionContext, str]:
    """Get the election parameters either from the data cache or from the request body"""

    # Check an election is assigned
    if not election_id:
        election_id = request_data.election_id

    if not election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="specify election_id in the query parameter or request body",
        )

    # TODO: load validation from repository
    if not request_data.manifest:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Query for Manifest Not Yet Implemented",
        )

    if not request_data.context:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Query for Context Not Yet Implemented",
        )

    manifest = request_data.manifest
    context = request_data.context
    return manifest, context, election_id


def _submit_ballots(
    election_id: str, ballots: List[SubmittedBallot], settings: Settings = Settings()
) -> BaseResponse:
    """"""
    set_response = set_ballots(election_id, ballots, settings)
    if set_response.is_success():
        inventory = get_ballot_inventory(election_id, settings)
        for ballot in ballots:
            if ballot.state == BallotBoxState.CAST:
                inventory.cast_ballot_count += 1
                inventory.cast_ballots[ballot.code.to_hex()] = ballot.object_id
            elif ballot.state == BallotBoxState.SPOILED:
                inventory.spoiled_ballot_count += 1
                inventory.spoiled_ballots[ballot.code.to_hex()] = ballot.object_id
        upsert_ballot_inventory(election_id, inventory, settings)

    return set_response


def _validate_ballot(request: ValidateBallotRequest) -> None:
    ballot = CiphertextBallot.from_json_object(request.ballot)
    manifest = Manifest.from_json_object(request.manifest)
    internal_manifest = InternalManifest(manifest)
    context = CiphertextElectionContext.from_json_object(request.context)

    if not ballot_is_valid_for_election(ballot, internal_manifest, context):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"ballot {ballot.object_id} is not valid",
        )


@router.put("/test/submit_queue", tags=[BALLOTS], status_code=status.HTTP_202_ACCEPTED)
def test_submit_ballot(
    request: SubmitBallotsRequest = Body(...),
) -> BaseResponse:
    """
    Submit a single ballot using a queue.  For testing purposes only.
    """
    # TODO: complete the implementation

    if not request.election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must submit an election id",
        )

    try:
        ballots = [
            SubmittedBallot.from_json_object(ballot) for ballot in request.ballots
        ]
        with get_message_queue("submitted-ballots", "submitted-ballots") as queue:
            for ballot in ballots:
                queue.publish(ballot.to_json())
            _process_ballots(queue, request.election_id)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=500,
            detail="Ballot failed to be submitted",
        ) from error
    return BaseResponse(message="Ballot Successfully Submitted")


def _process_ballots(queue: IMessageQueue, election_id: str) -> None:
    try:
        with get_repository(election_id, DataCollection.SUBMITTED_BALLOT) as repository:
            for message in queue.subscribe():
                ballot = SubmittedBallot.from_json(message)
                key = repository.set(ballot.to_json_object())
                print(f"process_ballots: key {key}")
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=500,
            detail="Ballot failed to be processed",
        ) from error
