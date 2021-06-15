from typing import Any, List, Optional
import sys
from fastapi import APIRouter, Body, HTTPException, status

from electionguard.key_ceremony import (
    PublicKeySet,
    ElectionPartialKeyBackup,
    ElectionPartialKeyVerification,
    ElectionPartialKeyChallenge,
    verify_election_partial_key_challenge,
)
from electionguard.elgamal import elgamal_combine_public_keys
from electionguard.serializable import write_json_object, read_json_object
from electionguard.group import int_to_p_unchecked

from ....core.client import get_client_id
from ....core.guardian import get_guardian
from ....core.key_ceremony import (
    get_key_ceremony,
    update_key_ceremony,
    update_key_ceremony_state,
    validate_can_publish,
)
from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseQueryRequest,
    BaseResponse,
    ResponseStatus,
    KeyCeremony,
    KeyCeremonyState,
    KeyCeremonyGuardian,
    KeyCeremonyGuardianStatus,
    KeyCeremonyGuardianState,
    KeyCeremonyCreateRequest,
    KeyCeremonyStateResponse,
    KeyCeremonyQueryResponse,
    KeyCeremonyVerifyChallengesResponse,
    ElectionJointKeyResponse,
)
from ..tags import KEY_CEREMONY

router = APIRouter()


@router.get("/ceremony", tags=[KEY_CEREMONY])
def get_ceremony(
    key_name: str,
) -> KeyCeremonyQueryResponse:
    """
    Get a specific key ceremony by key_name.
    """
    try:
        with get_repository(get_client_id(), DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            key_ceremony = read_json_object(query_result, KeyCeremony)
            return KeyCeremonyQueryResponse(
                status=ResponseStatus.SUCCESS, KeyCeremonies=[key_ceremony]
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get key ceremony failed",
        ) from error


@router.put("/ceremony", tags=[KEY_CEREMONY])
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
                repository.set(ceremony)
                return BaseResponse(status=ResponseStatus.SUCCESS)
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


@router.get("/ceremony/state", tags=[KEY_CEREMONY])
def get_ceremony_state(
    key_name: str,
) -> KeyCeremonyStateResponse:
    """
    Get a specific key ceremony state by key_name.
    """
    ceremonies = get_key_ceremony(key_name)

    return KeyCeremonyStateResponse(
        key_name=key_name,
        state=ceremonies.key_ceremonies[0].state,
        guardian_status=ceremonies.key_ceremonies[0].guardian_status,
    )


@router.get("/ceremony/find")
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
                key_ceremonies.append(read_json_object(item, KeyCeremony))
            return KeyCeremonyQueryResponse(
                status=ResponseStatus.SUCCESS, key_ceremonies=key_ceremonies
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error


@router.post("/ceremony/open", tags=[KEY_CEREMONY])
def open_ceremony(key_name: str) -> BaseResponse:
    """
    Open a key ceremony for participation.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.OPEN)


@router.post("/ceremony/close", tags=[KEY_CEREMONY])
def close_ceremony(key_name: str) -> BaseResponse:
    """
    Close a key ceremony for participation
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.CLOSED)


@router.post("/ceremony/challenge", tags=[KEY_CEREMONY])
def challenge_ceremony(key_name: str) -> BaseResponse:
    """
    Mark the key ceremony challenged.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.CHALLENGED)


@router.post("/ceremony/challenge/verify", tags=[KEY_CEREMONY])
def verify_ceremony_challenges(key_name: str) -> BaseResponse:
    """
    Verify a challenged key ceremony.
    """
    ceremony = get_key_ceremony(key_name)
    challenge_guardians: List[KeyCeremonyGuardian] = []
    for guardian_id, state in ceremony.guardian_status.items():
        if state.backups_verified == KeyCeremonyGuardianStatus.ERROR:
            challenge_guardians.append(get_guardian(guardian_id))

    if not any(challenge_guardians):
        return BaseResponse(
            status=ResponseStatus.SUCCESS, message="no challenges exist"
        )

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

    return KeyCeremonyVerifyChallengesResponse(
        status=ResponseStatus.SUCCESS, verifications=verifications
    )


@router.post("/ceremony/cancel", tags=[KEY_CEREMONY])
def cancel_ceremony(key_name: str) -> BaseResponse:
    """
    Cancel a Key Ceremony.
    """
    return update_key_ceremony_state(key_name, KeyCeremonyState.CANCELLED)


@router.get("/ceremony/joint_key", tags=[KEY_CEREMONY])
def get_joint_key(
    key_name: str,
) -> ElectionJointKeyResponse:
    """
    Get The Joint Election Key
    """
    ceremony = get_key_ceremony(key_name)
    if not ceremony.election_joint_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f"No joint key for {key_name}",
        )

    return ElectionJointKeyResponse(
        status=ResponseStatus.SUCCESS,
        joint_key=write_json_object(ceremony.election_joint_key),
    )


# FINAL: Publish joint public election key
@router.post("/ceremony/publish", tags=[KEY_CEREMONY])
def publish_joint_key(
    key_name: str,
) -> KeyCeremonyQueryResponse:
    """
    Publish joint election key from the public keys of all guardians
    """
    ceremony = get_key_ceremony(key_name)

    validate_can_publish(ceremony)

    election_public_keys = []
    for guardian_id in ceremony.guardian_ids:
        guardian = get_guardian(guardian_id)
        if not guardian.public_keys:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Could not find guardian public key {guardian_id}",
            )
        election_public_keys.append(int_to_p_unchecked(guardian.public_keys.election))

    joint_key = elgamal_combine_public_keys(election_public_keys)
    ceremony.election_joint_key = write_json_object(joint_key)
    update_key_ceremony(key_name, ceremony)

    return KeyCeremonyQueryResponse(
        joint_key=write_json_object(ceremony.election_joint_key)
    )
