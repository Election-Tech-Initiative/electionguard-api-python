from electionguard.key_ceremony import (
    generate_election_key_pair,
    generate_rsa_auxiliary_key_pair,
)
from electionguard.serializable import read_json_object
from electionguard.group import int_to_q_unchecked
from fastapi import APIRouter, Body, HTTPException
from ..models import (
    AuxiliaryKeyPair,
    ElectionKeyPair,
    CreateElectionKeyPairRequest,
    AuxiliaryRequest,
)
from ..tags import KEY_CEREMONY

router = APIRouter()


@router.post("/election/generate", response_model=ElectionKeyPair, tags=[KEY_CEREMONY])
def generate_election_keys(
    request: CreateElectionKeyPairRequest = Body(...),
) -> ElectionKeyPair:
    """
    Generate election key pairs for use in election process
    :param request: Election key pair request
    :return: Election key pair
    """
    keys = generate_election_key_pair(
        request.owner_id,
        request.sequence_order,
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    if not keys:
        raise HTTPException(
            status_code=500,
            detail="Election keys failed to be generated",
        )
    return read_json_object(keys, ElectionKeyPair)


@router.post(
    "/auxiliary/generate", response_model=AuxiliaryKeyPair, tags=[KEY_CEREMONY]
)
def generate_auxiliary_keys(request: AuxiliaryRequest = Body(...)) -> AuxiliaryKeyPair:
    """
    Generate auxiliary key pair for auxiliary uses during process
    :return: Auxiliary key pair
    """
    keys = generate_rsa_auxiliary_key_pair(request.owner_id, request.sequence_order)

    if not keys:
        raise HTTPException(
            status_code=500, detail="Auxiliary keys failed to be generated"
        )
    return read_json_object(keys, AuxiliaryKeyPair)
