from typing import List
import sys
from fastapi import APIRouter, Body, HTTPException, status

from electionguard.hash import hash_elems
from electionguard.key_ceremony import (
    PublicKeySet,
    ElectionPublicKey,
    ElectionPartialKeyVerification,
    ElectionPartialKeyChallenge,
    verify_election_partial_key_challenge,
)
from electionguard.elgamal import elgamal_combine_public_keys
from electionguard.serializable import write_json_object, read_json_object
from electionguard.group import ElementModP

from ....core.client import get_client_id
from ....core.key_guardian import get_key_guardian
from ....core.key_ceremony import (
    from_query,
    get_key_ceremony,
    update_key_ceremony,
    update_key_ceremony_state,
    validate_can_publish,
)
from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseQueryRequest,
    BaseResponse,
    KeyCeremony,
    KeyCeremonyState,
    KeyCeremonyGuardian,
    KeyCeremonyGuardianStatus,
    KeyCeremonyGuardianState,
    KeyCeremonyCreateRequest,
    KeyCeremonyStateResponse,
    KeyCeremonyQueryResponse,
    KeyCeremonyVerifyChallengesResponse,
    PublishElectionJointKeyRequest,
    ElectionJointKeyResponse,
)
from ..tags import KEY_CEREMONY_ADMIN

router = APIRouter()


@router.get(
    "/ceremony", response_model=KeyCeremonyQueryResponse, tags=[KEY_CEREMONY_ADMIN]
)
def fetch_ceremony(
    key_name: str,
) -> KeyCeremonyQueryResponse:
    """
    Get a specific key ceremony by key_name.
    """
    key_ceremony = get_key_ceremony(key_name)
    return KeyCeremonyQueryResponse(key_ceremonies=[key_ceremony])


@router.put("/ceremony", response_model=BaseResponse, tags=[KEY_CEREMONY_ADMIN])
def create_ceremony(
    request: KeyCeremonyCreateRequest = Body(...),
) -> BaseResponse:
    """
    Create a Key Ceremony.

    Calling this method for an existing key_name will overwrite an existing one.
    """

    ceremony = KeyCeremony(
        key_name=request.key_name,
        state=KeyCeremonyState.CREATED,
        number_of_guardians=request.number_of_guardians,
        quorum=request.quorum,
        guardian_ids=request.guardian_ids,
        guardian_status={
            guardian_id: KeyCeremonyGuardianState()
            for guardian_id in request.guardian_ids
        },
    )

    try:
        with get_repository(get_client_id(), DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"key_name": request.key_name})
            if not query_result:
                repository.set(ceremony.dict())
                return BaseResponse()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Already exists {request.key_name}",
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Create Key Ceremony Failed",
        ) from error


@router.get(
    "/ceremony/state",
    response_model=KeyCeremonyStateResponse,
    tags=[KEY_CEREMONY_ADMIN],
)
def fetch_ceremony_state(
    key_name: str,
) -> KeyCeremonyStateResponse:
    """
    Get a specific key ceremony state by key_name.
    """
    ceremony = get_key_ceremony(key_name)

    return KeyCeremonyStateResponse(
        key_name=key_name,
        state=ceremony.state,
        guardian_status=ceremony.guardian_status,
    )


@router.get(
    "/ceremony/find", response_model=KeyCeremonyQueryResponse, tags=[KEY_CEREMONY_ADMIN]
)
def find_ceremonies(
    skip: int = 0, limit: int = 100, request: BaseQueryRequest = Body(...)
) -> KeyCeremonyQueryResponse:
    """
    Find Key Ceremonies according ot the filter criteria.
    """
    try:
        filter = write_json_object(request.filter) if request.filter else {}
        with get_repository(get_client_id(), DataCollection.KEY_CEREMONY) as repository:
            cursor = repository.find(filter, skip, limit)
            key_ceremonies: List[KeyCeremony] = []
            for item in cursor:
                key_ceremonies.append(from_query(item))
            return KeyCeremonyQueryResponse(key_ceremonies=key_ceremonies)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error


@router.post("/ceremony/open", response_model=BaseResponse, tags=[KEY_CEREMONY_ADMIN])
def open_ceremony(key_name: str) -> BaseResponse:
    """
    Open a key ceremony for participation.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.OPEN)


@router.post("/ceremony/close", response_model=BaseResponse, tags=[KEY_CEREMONY_ADMIN])
def close_ceremony(key_name: str) -> BaseResponse:
    """
    Close a key ceremony for participation.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.CLOSED)


@router.post(
    "/ceremony/challenge", response_model=BaseResponse, tags=[KEY_CEREMONY_ADMIN]
)
def challenge_ceremony(key_name: str) -> BaseResponse:
    """
    Mark the key ceremony challenged.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.CHALLENGED)


@router.get(
    "/ceremony/challenge/verify", response_model=BaseResponse, tags=[KEY_CEREMONY_ADMIN]
)
def verify_ceremony_challenges(key_name: str) -> BaseResponse:
    """
    Verify a challenged key ceremony.
    """
    ceremony = get_key_ceremony(key_name)
    challenge_guardians: List[KeyCeremonyGuardian] = []
    for guardian_id, state in ceremony.guardian_status.items():
        if state.backups_verified == KeyCeremonyGuardianStatus.ERROR:
            challenge_guardians.append(get_key_guardian(key_name, guardian_id))

    if not any(challenge_guardians):
        return BaseResponse(message="no challenges exist")

    verifications: List[ElectionPartialKeyVerification] = []
    for guardian in challenge_guardians:
        if not guardian.challenges:
            continue
        for challenge in guardian.challenges:
            verifications.append(
                verify_election_partial_key_challenge(
                    "API",
                    read_json_object(challenge, ElectionPartialKeyChallenge),
                )
            )

    return KeyCeremonyVerifyChallengesResponse(verifications=verifications)


@router.post("/ceremony/cancel", response_model=BaseResponse, tags=[KEY_CEREMONY_ADMIN])
def cancel_ceremony(key_name: str) -> BaseResponse:
    """
    Cancel a Key Ceremony.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.CANCELLED)


@router.get(
    "/ceremony/joint_key",
    response_model=ElectionJointKeyResponse,
    tags=[KEY_CEREMONY_ADMIN],
)
def fetch_joint_key(
    key_name: str,
) -> ElectionJointKeyResponse:
    """
    Get The Joint Election Key
    """
    ceremony = get_key_ceremony(key_name)
    if not ceremony.elgamal_public_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f"No joint key for {key_name}",
        )
    if not ceremony.commitment_hash:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f"No commitment hash for {key_name}",
        )

    return ElectionJointKeyResponse(
        elgamal_public_key=write_json_object(ceremony.elgamal_public_key),
        commitment_hash=write_json_object(ceremony.commitment_hash),
    )


@router.post(
    "/ceremony/combine",
    response_model=ElectionJointKeyResponse,
    tags=[KEY_CEREMONY_ADMIN],
)
def combine_election_keys(
    request: PublishElectionJointKeyRequest,
) -> ElectionJointKeyResponse:
    """
    Combine public election keys into a final one without mutating the state of the key ceremony.
    :return: Combine Election key
    """
    election_public_keys: List[ElementModP] = []
    coefficient_commitments: List[ElementModP] = []
    for public_key in request.election_public_keys:
        key = read_json_object(public_key, ElectionPublicKey)
        election_public_keys.append(key.key)
        for commitment in key.coefficient_commitments:
            coefficient_commitments.append(commitment)
    return _elgamal_combine_keys(election_public_keys, coefficient_commitments)


# FINAL: Publish joint public election key
@router.post(
    "/ceremony/publish",
    response_model=ElectionJointKeyResponse,
    tags=[KEY_CEREMONY_ADMIN],
)
def publish_joint_key(
    key_name: str,
) -> ElectionJointKeyResponse:
    """
    Publish joint election key from the public keys of all guardians
    """
    ceremony = get_key_ceremony(key_name)

    validate_can_publish(ceremony)

    election_public_keys: List[ElementModP] = []
    coefficient_commitments: List[ElementModP] = []
    for guardian_id in ceremony.guardian_ids:
        guardian = get_key_guardian(key_name, guardian_id)
        if not guardian.public_keys:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Could not find guardian public key {guardian_id}",
            )

        public_keys = read_json_object(guardian.public_keys, PublicKeySet)
        election_public_keys.append(public_keys.election.key)
        for commitment in public_keys.election.coefficient_commitments:
            coefficient_commitments.append(commitment)

    response = _elgamal_combine_keys(election_public_keys, coefficient_commitments)

    ceremony.elgamal_public_key = response.elgamal_public_key
    ceremony.commitment_hash = response.commitment_hash
    update_key_ceremony(key_name, ceremony)

    return response


def _elgamal_combine_keys(
    election_public_keys: List[ElementModP], coefficient_commitments: List[ElementModP]
) -> ElectionJointKeyResponse:
    elgamal_public_key = elgamal_combine_public_keys(election_public_keys)
    commitment_hash = hash_elems(coefficient_commitments)
    return ElectionJointKeyResponse(
        elgamal_public_key=write_json_object(elgamal_public_key),
        commitment_hash=write_json_object(commitment_hash),
    )
