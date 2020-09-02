from electionguard.key_ceremony import (
    generate_election_key_pair,
    generate_rsa_auxiliary_key_pair,
)
from electionguard.group import int_to_q_unchecked
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

from app.utils.serialize import write_json_object

router = APIRouter()


class ElectionKeyPairRequest(BaseModel):
    quorum: int
    nonce: Optional[str] = None


class ElectionKeyPairResponse(BaseModel):
    secret_key: str
    public_key: str
    proof: Any
    polynomial: Any


class AuxiliaryKeyPairResponse(BaseModel):
    secret_key: str
    public_key: str


GuardianKeysRequest = ElectionKeyPairRequest


class GuardianKeysResponse(BaseModel):
    election: ElectionKeyPairResponse
    auxiliary: AuxiliaryKeyPairResponse


@router.post("/generate", response_model=GuardianKeysResponse)
def generate_keys(request: GuardianKeysRequest) -> GuardianKeysResponse:
    """
    Generate election key pairs for use in election process
    """
    election_keys = generate_election_key_pair(
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    auxiliary_keys = generate_rsa_auxiliary_key_pair()
    if not election_keys:
        raise HTTPException(
            status_code=500,
            detail="Election keys failed to be generated",
        )
    if not auxiliary_keys:
        raise HTTPException(
            status_code=500, detail="Auxiliary keys failed to be generated"
        )
    return GuardianKeysResponse(
        election=ElectionKeyPairResponse(
            public_key=str(election_keys.key_pair.public_key),
            secret_key=str(election_keys.key_pair.secret_key),
            proof=write_json_object(election_keys.proof),
            polynomial=write_json_object(election_keys.polynomial),
        ),
        auxiliary=AuxiliaryKeyPairResponse(
            public_key=auxiliary_keys.public_key, secret_key=auxiliary_keys.secret_key
        ),
    )


@router.post("/election/generate", response_model=ElectionKeyPairResponse)
def generate_election_keys(request: ElectionKeyPairRequest) -> ElectionKeyPairResponse:
    """
    Generate election key pairs for use in election process
    """
    keys = generate_election_key_pair(
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    if not keys:
        raise HTTPException(
            status_code=500,
            detail="Election keys failed to be generated",
        )
    return ElectionKeyPairResponse(
        public_key=str(keys.key_pair.public_key),
        secret_key=str(keys.key_pair.secret_key),
        proof=write_json_object(keys.proof),
        polynomial=write_json_object(keys.polynomial),
    )


@router.post("/auxiliary/generate", response_model=AuxiliaryKeyPairResponse)
def generate_auxiliary_keys() -> AuxiliaryKeyPairResponse:
    """
    Generate auxiliary key pair for auxiliary uses during process
    """
    keys = generate_rsa_auxiliary_key_pair()
    if not keys:
        raise HTTPException(
            status_code=500, detail="Auxiliary keys failed to be generated"
        )
    return AuxiliaryKeyPairResponse(
        public_key=keys.public_key, secret_key=keys.secret_key
    )
