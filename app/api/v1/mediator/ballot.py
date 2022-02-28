from typing import List, Optional, Tuple, cast
from logging import getLogger
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

from app.api.v1.models.ballot import SubmitBallotsRequestDto

from ....core.ballot import (
    filter_ballots,
    get_ballot,
    set_ballots,
    get_ballot_inventory,
    upsert_ballot_inventory,
)
from ....core.election import get_election
from ....core.repository import get_repository, DataCollection
from ....core.settings import Settings
from ....core.queue import get_message_queue, IMessageQueue
from ..models import (
    BaseResponse,
    BaseQueryRequest,
    BaseBallotRequest,
    BallotInventoryResponse,
    BallotQueryResponse,
    CastBallotsRequest,
    SpoilBallotsRequest,
    SubmitBallotsRequest,
    ValidateBallotRequest,
)
from ..tags import BALLOTS

logger = getLogger(__name__)
router = APIRouter()


@router.get("", response_model=BallotQueryResponse, tags=[BALLOTS])
def fetch_ballot(
    request: Request, election_id: str, ballot_id: str
) -> BallotQueryResponse:
    """
    Fetch A Ballot for a specific election.
    """
    ballot = get_ballot(election_id, ballot_id, request.app.state.settings)
    return BallotQueryResponse(
        election_id=election_id,
        ballots=[ballot.to_json_object()],
    )


@router.get("/inventory", response_model=BallotInventoryResponse, tags=[BALLOTS])
def fetch_ballot_inventory(
    request: Request, election_id: str
) -> BallotInventoryResponse:
    """
    Fetch the Ballot Inventory for a specific election.
    """
    inventory = get_ballot_inventory(election_id, request.app.state.settings)

    return BallotInventoryResponse(
        inventory=inventory,
    )


@router.post("/find", response_model=BallotQueryResponse, tags=[BALLOTS])
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
    filter = write_json_object(data.filter) if data.filter else {}
    ballots = filter_ballots(
        election_id, filter, skip, limit, request.app.state.settings
    )
    return BallotQueryResponse(
        election_id=election_id, ballots=[ballot.to_json_object() for ballot in ballots]
    )


@router.post(
    "/cast",
    response_model=BaseResponse,
    tags=[BALLOTS],
    status_code=status.HTTP_202_ACCEPTED,
)
def cast_ballots(
    request: Request,
    election_id: Optional[str] = None,
    data: CastBallotsRequest = Body(...),
) -> BaseResponse:
    """
    Cast ballot
    """
    logger.info(f"casting ballot for election {election_id}")
    manifest, context, election_id = _get_election_parameters(election_id, data)
    ballots = [
        from_ciphertext_ballot(
            CiphertextBallot.from_json_object(ballot), BallotBoxState.CAST
        )
        for ballot in data.ballots
    ]

    for ballot in ballots:
        validation_request = ValidateBallotRequest(
            ballot=ballot.to_json_object(), manifest=manifest, context=context
        )
        _validate_ballot(validation_request)

    logger.info(f"all {len(ballots)} ballots validated successfully")
    return _submit_ballots(election_id, ballots, request.app.state.settings)


@router.post(
    "/spoil",
    response_model=BaseResponse,
    tags=[BALLOTS],
    status_code=status.HTTP_202_ACCEPTED,
)
def spoil_ballots(
    request: Request,
    election_id: Optional[str] = None,
    data: SpoilBallotsRequest = Body(...),
) -> BaseResponse:
    """
    Spoil ballot
    """
    manifest, context, election_id = _get_election_parameters(election_id, data)
    ballots = [
        from_ciphertext_ballot(
            CiphertextBallot.from_json_object(ballot), BallotBoxState.SPOILED
        )
        for ballot in data.ballots
    ]

    for ballot in ballots:
        validation_request = ValidateBallotRequest(
            ballot=ballot.to_json_object(), manifest=manifest, context=context
        )
        _validate_ballot(validation_request)

    return _submit_ballots(election_id, ballots, request.app.state.settings)


@router.put(
    "/submit",
    response_model=BaseResponse,
    tags=[BALLOTS],
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_ballots2(
    request: Request,
    election_id: str,
    data: SubmitBallotsRequestDto = Body(...),
) -> BaseResponse:
    """
    Submit ballots for an election.

    This method expects an `election_id` is provided either in the query string or the request body.
    If both are provied, the query string will override.
    """

    logger.info(f"Submitting ballots for {election_id}")

    settings = request.app.state.settings
    election_sdk = get_election(election_id, settings)
    manifest_sdk = election_sdk.manifest
    context_dto = election_sdk.context
    context_sdk = context_dto.to_sdk_format()

    res: str = ""
    logger.info(f"Converting {len(data.ballots)} ballots to sdk format")
    ballots_sdk = list(map(lambda b: b.to_sdk_format(), data.ballots))
    for ballot in ballots_sdk:
        if ballot.state == BallotBoxState.UNKNOWN:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=f"Submitted ballot {ballot.object_id} must have a cast or spoil state",
            )
        ballot_json = ballot.to_json_object()
        validation_request = ValidateBallotRequest(
            ballot=ballot_json,
            manifest=manifest_sdk,
            context=context_sdk,
        )
        logger.info("about to validate ballots")
        _validate_ballot(validation_request)
        logger.info("validated ballots successfully")
        res += str(ballot.state)

    return _submit_ballots(election_id, ballots_sdk, request.app.state.settings)


@router.post("/validate", response_model=BaseResponse, tags=[BALLOTS])
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
    """Get the election parameters either from the data cache or from the request body."""

    # Check an election is assigned
    if not election_id:
        election_id = request_data.election_id

    if not election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="specify election_id in the query parameter or request body.",
        )

    election = get_election(election_id, settings)

    if request_data.manifest:
        manifest = request_data.manifest
    else:
        manifest = Manifest.from_json_object(election.manifest)

    if request_data.context:
        context = cast(CiphertextElectionContext, request_data.context)
    else:
        context = election.context.to_sdk_format()

    return manifest, context, election_id


def _submit_ballots(
    election_id: str, ballots: List[SubmittedBallot], settings: Settings = Settings()
) -> BaseResponse:
    logger.info("submitting ballots")
    set_response = set_ballots(election_id, ballots, settings)
    if set_response.is_success():
        logger.info(f"successfully set ballots: {str(set_response)}")
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
            detail=f"ballot {ballot.object_id} is not valid.",
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
            detail="Must submit an election id.",
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
            detail="Ballot failed to be submitted.",
        ) from error
    return BaseResponse(message="Ballot Successfully Submitted.")


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
            detail="Ballot failed to be processed.",
        ) from error
