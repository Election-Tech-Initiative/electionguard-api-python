# pylint: disable=unused-argument
from typing import Dict
from logging import getLogger
from datetime import datetime
import sys

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from electionguard.ballot import BallotBoxState
from electionguard.decrypt_with_shares import decrypt_tally as decrypt
from electionguard.decryption_share import DecryptionShare
from electionguard.manifest import ElectionType, InternalManifest, Manifest
from electionguard.scheduler import Scheduler
from electionguard.serializable import read_json_object, write_json_object
from electionguard.type import CONTEST_ID
import electionguard.tally


from app.core.scheduler import get_scheduler
from app.core.settings import Settings
from app.core.ballot import get_ballot_inventory, filter_ballots
from app.core.election import get_election
from app.core.tally import (
    get_ciphertext_tally,
    set_ciphertext_tally,
    filter_ciphertext_tallies,
    set_plaintext_tally,
    filter_plaintext_tallies,
    update_plaintext_tally,
)
from app.core.tally_decrypt import filter_decryption_shares
from ..models import (
    BaseQueryRequest,
    CiphertextTallyQueryResponse,
    DecryptTallyRequest,
    CiphertextTally,
    PlaintextTally,
    PlaintextTallyState,
    PlaintextTallyQueryResponse,
)
from ..tags import TALLY


router = APIRouter()
logger = getLogger(__name__)


@router.get("", response_model=CiphertextTally, tags=[TALLY])
def fetch_ciphertext_tally(
    request: Request,
    election_id: str,
    tally_name: str,
) -> CiphertextTally:
    """
    Fetch a specific ciphertext tally.
    """
    tally = get_ciphertext_tally(election_id, tally_name, request.app.state.settings)
    return tally


@router.post("", response_model=CiphertextTally, tags=[TALLY])
def tally_ballots(
    request: Request,
    election_id: str,
    tally_name: str,
    scheduler: Scheduler = Depends(get_scheduler),
) -> CiphertextTally:
    """
    Start a new ciphertext tally of a collection of ballots.

    An election can have more than one tally.  Each tally must have a unique name.
    Each tally correlates to a snapshot of all ballots submitted for a given election.
    """
    election = get_election(election_id, request.app.state.settings)
    manifest = Manifest.from_json_object(election.manifest)
    context = election.context.to_sdk_format()

    # get the cast and spoiled ballots by checking the current ballot inventory
    # and filtering the table for
    inventory = get_ballot_inventory(election_id, request.app.state.settings)
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find a ballot inventory with election_id {election_id}",
        )
    cast_ballots = filter_ballots(
        election_id,
        {"state": BallotBoxState.CAST.name},
        0,
        inventory.cast_ballot_count,
        request.app.state.settings,
    )
    spoiled_ballots = filter_ballots(
        election_id,
        {"state": BallotBoxState.SPOILED.name},
        0,
        inventory.spoiled_ballot_count,
        request.app.state.settings,
    )
    # TODO: check inventory list matches find result above and throw if it does not.

    # append the ballots to the eg library tally
    sdk_tally = electionguard.tally.CiphertextTally(
        f"{election_id}-{tally_name}", InternalManifest(manifest), context
    )
    sdk_tally.batch_append(
        [(ballot.object_id, ballot) for ballot in cast_ballots], scheduler
    )
    sdk_tally.batch_append(
        [(ballot.object_id, ballot) for ballot in spoiled_ballots], scheduler
    )

    # create and cache the api tally.
    api_tally = CiphertextTally(
        election_id=election_id,
        tally_name=tally_name,
        created=datetime.now(),
        tally=sdk_tally.to_json_object(),
    )

    set_ciphertext_tally(api_tally, request.app.state.settings)

    return api_tally


@router.post("/find", response_model=CiphertextTallyQueryResponse, tags=[TALLY])
def find_ciphertext_tallies(
    request: Request,
    election_id: str,
    skip: int = 0,
    limit: int = 100,
    data: BaseQueryRequest = Body(...),
) -> CiphertextTallyQueryResponse:
    """
    Find tallies.

    Search the repository for tallies that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    filter = write_json_object(data.filter) if data.filter else {}
    tallies = filter_ciphertext_tallies(
        election_id, filter, skip, limit, request.app.state.settings
    )
    return CiphertextTallyQueryResponse(tallies=tallies)


@router.post("/decrypt", response_model=PlaintextTallyQueryResponse, tags=[TALLY])
async def decrypt_tally(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    restart: bool = False,
    data: DecryptTallyRequest = Body(...),
) -> PlaintextTallyQueryResponse:
    """
    Decrypt a tally from a collection of decrypted guardian shares.

    Requires that all guardian shares have been submitted.

    The decryption process can take some time,
    so the method returns immediately and continues processing in the background.
    """

    # if we already have a value cached, then return it.
    plaintext_tallies = filter_plaintext_tallies(
        data.election_id,
        {"election_id": data.election_id, "tally_name": data.tally_name},
        0,
        1,
        request.app.state.settings,
    )
    if not restart and len(plaintext_tallies) > 0:
        logger.info("returning plaintext tally from cache")
        return PlaintextTallyQueryResponse(tallies=plaintext_tallies)

    logger.info("no tally exists in cache")

    tally = PlaintextTally(
        election_id=data.election_id,
        tally_name=data.tally_name,
        created=datetime.now(),
        state=PlaintextTallyState.CREATED,
    )
    set_plaintext_tally(tally, request.app.state.settings)

    # queue a background task to execute the tally
    # TODO: determine whether we wait or continue
    # asyncio.create_task(_decrypt_tally(tally, request.app.state.settings))
    await _decrypt_tally(tally, request.app.state.settings)

    response.status_code = status.HTTP_202_ACCEPTED
    return PlaintextTallyQueryResponse(
        message="tally computing, check back in a few minutes.", tallies=[tally]
    )


async def _decrypt_tally(
    api_plaintext_tally: PlaintextTally, settings: Settings = Settings()
) -> None:

    try:
        # set the tally state to processing
        api_plaintext_tally.state = PlaintextTallyState.PROCESSING
        update_plaintext_tally(api_plaintext_tally, settings)

        api_ciphertext_tally = get_ciphertext_tally(
            api_plaintext_tally.election_id, api_plaintext_tally.tally_name, settings
        )

        election = get_election(api_plaintext_tally.election_id, settings)
        context = election.context.to_sdk_format()

        # filter the guardian shares
        query_shares = filter_decryption_shares(
            api_plaintext_tally.tally_name,
            None,
            0,
            context.number_of_guardians,
            settings,
        )

        # validate we have all of the guardian shares
        # TODO: support thresholding
        if len(query_shares) != context.number_of_guardians:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"{len(query_shares)} of {context.number_of_guardians} guardians have submitted shares",
            )

        # transform the tally shares
        tally_shares = {
            share.guardian_id: read_json_object(share.tally_share, DecryptionShare)
            for share in query_shares
        }

        # TODO: HACK: Remove The Empty Manifest
        # Note: The CiphertextTally requires an internal manifest passed into its constructor
        # but it is not actually used when executing `compute_decryption_share` so we create a fake.
        # see: https://github.com/microsoft/electionguard-python/issues/391
        internal_manifest = InternalManifest(
            Manifest(
                "",
                "",
                ElectionType.other,
                datetime.now(),
                datetime.now(),
                [],
                [],
                [],
                [],
                [],
            )
        )
        sdk_ciphertext_tally = electionguard.tally.CiphertextTally(
            api_ciphertext_tally.tally_name, internal_manifest, context
        )
        contests: Dict[CONTEST_ID, electionguard.tally.CiphertextTallyContest] = {
            contest_id: read_json_object(
                contest, electionguard.tally.CiphertextTallyContest
            )
            for contest_id, contest in api_ciphertext_tally.tally["contests"].items()
        }
        sdk_ciphertext_tally.contests = contests

        # decrypt
        sdk_plaintext_tally = decrypt(
            sdk_ciphertext_tally,
            tally_shares,
            context.crypto_extended_base_hash,
        )
        if not sdk_plaintext_tally:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to decrypt tally",
            )

        # cache the tally plaintext tally
        api_plaintext_tally.tally = write_json_object(sdk_plaintext_tally)
        api_plaintext_tally.state = PlaintextTallyState.COMPLETE
        update_plaintext_tally(api_plaintext_tally, settings)

    except HTTPException:
        api_plaintext_tally.state = PlaintextTallyState.ERROR
        update_plaintext_tally(api_plaintext_tally, settings)
        print(sys.exc_info())
        raise
    except Exception as error:
        api_plaintext_tally.state = PlaintextTallyState.ERROR
        update_plaintext_tally(api_plaintext_tally, settings)
        logger.exception(sys.exc_info())
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="decrypt plaintext tally failed",
        ) from error
