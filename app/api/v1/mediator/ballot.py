from typing import Any, List, Optional, Tuple
import sys

from fastapi import APIRouter, Body, HTTPException, status, Response

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

from ....core.repository import get_repository, DataCollection
from ....core.queue import get_message_queue, IMessageQueue
from ..models import (
    ResponseStatus,
    BaseResponse,
    BaseQueryRequest,
    BaseBallotRequest,
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
def get_ballot(election_id: str, ballot_id: str) -> BallotQueryResponse:
    """
    Get A Ballot for a specific election
    """
    with get_repository(election_id, DataCollection.SUBMITTED_BALLOT) as repository:
        ballot = repository.get({"object_id": ballot_id})
        if not ballot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find ballot {ballot_id}",
            )

        return BallotQueryResponse(
            status=ResponseStatus.SUCCESS,
            election_id=election_id,
            ballots=[write_json_object(ballot)],
        )


@router.get("/find", tags=[BALLOTS])
def find_ballots(
    election_id: str,
    skip: int = 0,
    limit: int = 100,
    request: BaseQueryRequest = Body(...),
) -> BallotQueryResponse:
    """Find Ballots."""
    try:
        filter = write_json_object(request.filter) if request.filter else {}
        with get_repository(election_id, DataCollection.SUBMITTED_BALLOT) as repository:
            cursor = repository.find(filter, skip, limit)
            ballots: List[Any] = []
            for item in cursor:
                ballots.append(write_json_object(item))
            return BallotQueryResponse(status=ResponseStatus.SUCCESS, ballots=ballots)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error


@router.post("/cast", tags=[BALLOTS], status_code=status.HTTP_202_ACCEPTED)
def cast_ballot(
    election_id: Optional[str] = None, request: CastBallotsRequest = Body(...)
) -> SubmitBallotsResponse:
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
def spoil_ballot(
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
    election_id: Optional[str] = None,
    request: SubmitBallotsRequest = Body(...),
) -> SubmitBallotsResponse:
    """
    Submit ballots for an election.

    This method expects an `election_id` is provided either in the query string or the request body.
    If both are provied, the query string will override.
    """

    manifest, context, election_id = _get_election_parameters(election_id, request)

    ballots = [SubmittedBallot.from_json_object(ballot) for ballot in request.ballots]
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

    return _submit_ballots(election_id, ballots)


@router.post("/validate", tags=[BALLOTS])
def validate_ballot(
    request: ValidateBallotRequest = Body(...),
) -> BaseResponse:
    """
    Validate a ballot for the given election data
    """
    _validate_ballot(request)
    return BaseResponse(
        status=ResponseStatus.SUCCESS, message="Ballot is valid for election"
    )


def _get_election_parameters(
    election_id: Optional[str], request: BaseBallotRequest
) -> Tuple[Manifest, CiphertextElectionContext, str]:
    # Check an election is assigned
    if not election_id:
        election_id = request.election_id

    if not election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="specify election_id in the query parameter or request body",
        )

    # TODO: load validation from repository
    if not request.manifest:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Query for Manifest Not Yet Implemented",
        )

    if not request.context:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Query for Context Not Yet Implemented",
        )

    manifest = request.manifest
    context = request.context
    return manifest, context, election_id


def _submit_ballots(
    election_id: str,
    ballots: List[SubmittedBallot],
) -> SubmitBallotsResponse:
    try:
        with get_repository(election_id, DataCollection.SUBMITTED_BALLOT) as repository:
            cacheable_ballots = [ballot.to_json_object() for ballot in ballots]
            keys = repository.set(cacheable_ballots)
            return SubmitBallotsResponse(
                status=ResponseStatus.SUCCESS,
                message="Ballot Successfully Submitted",
                cache_keys=keys,
                election_id=election_id,
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit ballots failed",
        ) from error


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
    return BaseResponse(
        status=ResponseStatus.SUCCESS, message="Ballot Successfully Submitted"
    )


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
