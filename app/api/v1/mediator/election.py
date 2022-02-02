from typing import Any
from uuid import uuid4


from fastapi import APIRouter, Body, HTTPException, Request, status

from electionguard.election import (
    ElectionConstants,
    make_ciphertext_election_context,
)
from electionguard.group import ElementModP, ElementModQ
from electionguard.manifest import Manifest
from electionguard.serializable import read_json_object, write_json_object
from electionguard.utils import get_optional

from .manifest import get_manifest
from ....core.ballot import upsert_ballot_inventory
from ....core.key_ceremony import get_key_ceremony
from ....core.election import (
    get_election,
    set_election,
    update_election_state,
    filter_elections,
)
from ..models import (
    BaseResponse,
    BallotInventory,
    Election,
    ElectionState,
    ElectionQueryRequest,
    ElectionQueryResponse,
    MakeElectionContextRequest,
    MakeElectionContextResponse,
    SubmitElectionRequest,
)
from ..tags import ELECTION

router = APIRouter()


@router.get("/constants", tags=[ELECTION])
def get_election_constants() -> Any:
    """
    Get the constants defined for an election.
    """
    constants = ElectionConstants()
    return constants.to_json_object()


@router.get("", response_model=ElectionQueryResponse, tags=[ELECTION])
def fetch_election(request: Request, election_id: str) -> ElectionQueryResponse:
    """Get an election by election id."""
    election = get_election(election_id, request.app.state.settings)
    return ElectionQueryResponse(
        elections=[election],
    )


@router.put("", response_model=BaseResponse, tags=[ELECTION])
def create_election(
    request: Request,
    data: SubmitElectionRequest = Body(...),
) -> BaseResponse:
    """
    Submit an election.

    Method expects a manifest to already be submitted or to optionally be provided
    as part of the request body.  If a manifest is provided as part of the body
    then it will override any cached value, however the hash must match the hash
    contained in the CiphertextelectionContext.
    """
    if data.election_id:
        election_id = data.election_id
    else:
        election_id = str(uuid4())

    key_ceremony = get_key_ceremony(data.key_name, request.app.state.settings)
    try:
        context = data.context.to_sdk_format()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # if a manifest is provided use it, but don't cache it
    if data.manifest:
        sdk_manifest = Manifest.from_json_object(data.manifest)
    else:
        api_manifest = get_manifest(context.manifest_hash, request.app.state.settings)
        sdk_manifest = Manifest.from_json_object(api_manifest.manifest)

    # validate that the context was built against the correct manifest
    if context.manifest_hash != sdk_manifest.crypto_hash().to_hex():
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="manifest hash does not match provided context hash",
        )

    # validate that the context provided matches a known key ceremony
    if context.elgamal_public_key != key_ceremony.elgamal_public_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="key ceremony public key does not match provided context public key",
        )

    election = Election(
        election_id=election_id,
        key_name=data.key_name,
        state=ElectionState.CREATED,
        context=context.to_json_object(),
        manifest=sdk_manifest.to_json_object(),
    )

    return set_election(election, request.app.state.settings)


@router.post("/find", response_model=ElectionQueryResponse, tags=[ELECTION])
def find_elections(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    data: ElectionQueryRequest = Body(...),
) -> ElectionQueryResponse:
    """
    Find elections.

    Search the repository for elections that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    filter = write_json_object(data.filter) if data.filter else {}
    elections = filter_elections(filter, skip, limit, request.app.state.settings)
    return ElectionQueryResponse(elections=elections)


@router.post("/open", response_model=BaseResponse, tags=[ELECTION])
def open_election(request: Request, election_id: str) -> BaseResponse:
    """
    Open an election.
    """
    # create the ballot inventory on election open
    ballot_inventory = BallotInventory(election_id=election_id)
    upsert_ballot_inventory(election_id, ballot_inventory, request.app.state.settings)

    return update_election_state(
        election_id, ElectionState.OPEN, request.app.state.settings
    )


@router.post("/close", response_model=BaseResponse, tags=[ELECTION])
def close_election(request: Request, election_id: str) -> BaseResponse:
    """
    Close an election.
    """
    return update_election_state(
        election_id, ElectionState.CLOSED, request.app.state.settings
    )


@router.post("/publish", response_model=BaseResponse, tags=[ELECTION])
def publish_election(request: Request, election_id: str) -> BaseResponse:
    """
    Publish an election.
    """
    return update_election_state(
        election_id, ElectionState.PUBLISHED, request.app.state.settings
    )


@router.post("/context", response_model=MakeElectionContextResponse, tags=[ELECTION])
def build_election_context(
    request: Request,
    data: MakeElectionContextRequest = Body(...),
) -> MakeElectionContextResponse:
    """
    Build a CiphertextElectionContext for a given election and returns it.

    Caller must specify the manifest to build against
    by either providing the manifest hash in the request body;
    or by providing the manifest directly in the request body.
    """

    if data.manifest:
        sdk_manifest = Manifest.from_json_object(data.manifest)
    else:
        manifest_hash = read_json_object(get_optional(data.manifest_hash), ElementModQ)
        api_manifest = get_manifest(
            manifest_hash,
            request.app.state.settings,
        )
        sdk_manifest = Manifest.from_json_object(api_manifest.manifest)

    elgamal_public_key: ElementModP = read_json_object(
        data.elgamal_public_key, ElementModP
    )
    commitment_hash = read_json_object(data.commitment_hash, ElementModQ)
    number_of_guardians = data.number_of_guardians
    quorum = data.quorum

    context = make_ciphertext_election_context(
        number_of_guardians,
        quorum,
        elgamal_public_key,
        commitment_hash,
        sdk_manifest.crypto_hash(),
    )

    return MakeElectionContextResponse(context=context.to_json_object())
