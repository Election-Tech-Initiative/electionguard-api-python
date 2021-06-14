from app.api.v1.models.key import KeyCeremonyGuardianStatus, KeyCeremonyState
from typing import Any, List, Optional
import sys
from fastapi import APIRouter, Body, HTTPException, status

from electionguard.key_ceremony import (
    PublicKeySet,
    ElectionPartialKeyBackup,
    ElectionPartialKeyVerification,
    ElectionPartialKeyChallenge,
)
from electionguard.elgamal import elgamal_combine_public_keys
from electionguard.serializable import write_json_object, read_json_object
from electionguard.group import int_to_p_unchecked

from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseQueryRequest,
    BaseResponse,
    ResponseStatus,
    GuardianAnnounceRequest,
    GuardianSubmitBackupRequest,
    GuardianBackupQueryResponse,
    GuardianSubmitVerificationRequest,
    GuardianVerificationQueryResponse,
    GuardianSubmitChallengeRequest,
    GuardianChallengeQueryResponse,
    GuardianQueryResponse,
    KeyCeremony,
    KeyCeremonyGuardian,
    KeyCeremonyGuardianState,
    KeyCeremonyCreateRequest,
    GuardianQueryResponse,
    KeyCeremonyStateResponse,
    KeyCeremonyQueryResponse,
    ElectionJointKeyResponse,
)
from ..tags import KEY_CEREMONY

router = APIRouter()


# TODO: multi-tenancy
CLIENT_ID = "electionguard-default-client-id"

# TODO: move to guardian or user file?


@router.get("/guardian")
def get_guardian(guardian_id: str) -> GuardianQueryResponse:
    """
    Get a guardian
    """
    try:
        with get_repository(CLIENT_ID, DataCollection.GUARDIAN) as repository:
            query_result = repository.get({"guardian_id": guardian_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {guardian_id}",
                )
            guardian = read_json_object(query_result, KeyCeremonyGuardian)
            return GuardianQueryResponse(
                status=ResponseStatus.SUCCESS, guardians=[guardian]
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get guardian failed",
        ) from error


@router.get("/guardian/find")
def find_guardians(
    skip: int = 0, limit: int = 100, request: BaseQueryRequest = Body(...)
) -> GuardianQueryResponse:
    """
    Find Guardians.

    Search the repository for guardians that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will iterate all available data.
    """
    try:
        filter = write_json_object(request.filter) if request.filter else {}
        with get_repository(CLIENT_ID, DataCollection.GUARDIAN) as repository:
            cursor = repository.find(filter, skip, limit)
            guardians: List[KeyCeremonyGuardian] = []
            for item in cursor:
                guardians.append(read_json_object(item, KeyCeremonyGuardian))
            return GuardianQueryResponse(
                status=ResponseStatus.SUCCESS, guardians=guardians
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="find guardians failed",
        ) from error


# ROUND 0: Create Key Ceremony Guardians
@router.put("/guardian")
def put_guardian(request: KeyCeremonyGuardian = Body(...)) -> BaseResponse:
    """Create a guardian"""
    try:
        with get_repository(CLIENT_ID, DataCollection.GUARDIAN) as repository:
            query_result = repository.get({"guardian_id": request.guardian_id})
            if not query_result:
                repository.set(request)
                return BaseResponse(status=ResponseStatus.SUCCESS)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Already exists {request.guardian_id}",
            )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit ballots failed",
        ) from error


# ROUND 1: Announce guardians with public keys
@router.put("/ceremony/announce", tags=[KEY_CEREMONY])
def announce_guardian(
    request: GuardianAnnounceRequest = Body(...),
) -> BaseResponse:
    """
    Announce the guardian as present and participating in the Key Ceremony
    :param public_key_set: Both the guardians public keys
    """
    keyset = read_json_object(request.public_keys, PublicKeySet)
    guardian_id = keyset.election.owner_id

    ceremony = _get_key_ceremony(request.key_name)
    guardian = _get_guardian(guardian_id)

    guardian.public_keys = write_json_object(keyset)
    ceremony.guardian_status[
        guardian_id
    ].public_key_shared = KeyCeremonyGuardianStatus.COMPLETE

    _update_guardian(guardian_id, guardian)
    return _update_key_ceremony(request.key_name, ceremony)


# ROUND 2: Share Election Partial Key Backups for compensating
@router.put("/ceremony/backup", tags=[KEY_CEREMONY])
def put_guardian_backup(
    request: GuardianSubmitBackupRequest = Body(...),
) -> BaseResponse:
    """
    put the guardian backups
    """
    backups = [
        read_json_object(backup, ElectionPartialKeyBackup) for backup in request.backups
    ]

    ceremony = _get_key_ceremony(request.key_name)
    guardian = _get_guardian(request.guardian_id)

    guardian.backups = [write_json_object(backup) for backup in backups]
    ceremony.guardian_status[
        request.guardian_id
    ].backups_shared = KeyCeremonyGuardianStatus.COMPLETE

    _update_guardian(request.guardian_id, guardian)
    return _update_key_ceremony(request.key_name, ceremony)


# ROUND 3: Share verifications of backups
@router.put("/ceremony/verify", tags=[KEY_CEREMONY])
def put_guardian_verification(
    request: GuardianSubmitVerificationRequest = Body(...),
) -> BaseResponse:
    """
    put the guardian backups
    """
    verifications = [
        read_json_object(verification, ElectionPartialKeyVerification)
        for verification in request.verifications
    ]

    ceremony = _get_key_ceremony(request.key_name)
    guardian = _get_guardian(request.guardian_id)

    guardian.verifications = [
        write_json_object(verification) for verification in verifications
    ]
    ceremony.guardian_status[
        request.guardian_id
    ].backups_verified = KeyCeremonyGuardianStatus.COMPLETE

    _update_guardian(request.guardian_id, guardian)
    return _update_key_ceremony(request.key_name, ceremony)


# ROUND 4 (Optional): If a verification fails, guardian must issue challenge
@router.put("/ceremony/challenge", tags=[KEY_CEREMONY])
def put_guardian_challenge(
    request: GuardianSubmitChallengeRequest = Body(...),
) -> BaseResponse:
    """
    Submit Challenges
    """
    challenges = [
        read_json_object(challenge, ElectionPartialKeyChallenge)
        for challenge in request.challenges
    ]

    ceremony = _get_key_ceremony(request.key_name)
    guardian = _get_guardian(request.guardian_id)

    guardian.challenges = [write_json_object(challenge) for challenge in challenges]
    ceremony.guardian_status[
        request.guardian_id
    ].backups_verified = KeyCeremonyGuardianStatus.ERROR

    _update_guardian(request.guardian_id, guardian)
    return _update_key_ceremony(request.key_name, ceremony)


# FINAL: Publish joint public election key
@router.post("/ceremony/publish", tags=[KEY_CEREMONY])
def publish_joint_key(
    key_name: str,
) -> KeyCeremonyQueryResponse:
    """
    Combine public election keys into a final one
    :return: Combine Election key
    """
    ceremony = _get_key_ceremony(key_name)

    _validate_can_publish(ceremony)

    election_public_keys = []
    for guardian_id in ceremony.guardian_ids:
        guardian = _get_guardian(guardian_id)
        if not guardian.public_keys:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Could not find guardian public key {guardian_id}",
            )
        election_public_keys.append(int_to_p_unchecked(guardian.public_keys.election))

    joint_key = elgamal_combine_public_keys(election_public_keys)
    ceremony.election_joint_key = write_json_object(joint_key)
    _update_key_ceremony(key_name, ceremony)

    return KeyCeremonyQueryResponse(
        joint_key=write_json_object(ceremony.election_joint_key)
    )


# --------- Key Ceremony --------


@router.get("/ceremony", tags=[KEY_CEREMONY])
def get_key_ceremony(
    key_name: str,
) -> KeyCeremonyQueryResponse:
    """
    Get a key ceremony
    """
    try:
        with get_repository(CLIENT_ID, DataCollection.KEY_CEREMONY) as repository:
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


@router.get("/ceremony/state", tags=[KEY_CEREMONY])
def get_key_ceremony_state(
    key_name: str,
) -> KeyCeremonyStateResponse:
    """
    Get Key Ceremony State
    """
    ceremonies = get_key_ceremony(key_name)

    return KeyCeremonyStateResponse(
        key_name=key_name,
        state=ceremonies.key_ceremonies[0].state,
        guardian_status=ceremonies.key_ceremonies[0].guardian_status,
    )


@router.get("/ceremony/find")
def find_key_ceremonies(
    skip: int = 0, limit: int = 100, request: BaseQueryRequest = Body(...)
) -> KeyCeremonyQueryResponse:
    """Find Key Ceremonies."""
    try:
        filter = write_json_object(request.filter) if request.filter else {}
        with get_repository(CLIENT_ID, DataCollection.KEY_CEREMONY) as repository:
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


@router.post("/ceremony/create", tags=[KEY_CEREMONY])
def create_key_ceremony(
    request: KeyCeremonyCreateRequest = Body(...),
) -> BaseResponse:
    """
    Create a Key Ceremony.

    Will overwrite an existing one.
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
        with get_repository(CLIENT_ID, DataCollection.KEY_CEREMONY) as repository:
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


@router.post("/ceremony/open", tags=[KEY_CEREMONY])
def open_key_ceremony(key_name: str) -> BaseResponse:
    """
    Open a Key Ceremony.
    """
    return _update_key_ceremony_state(key_name, KeyCeremonyState.OPEN)


@router.post("/ceremony/close", tags=[KEY_CEREMONY])
def close_key_ceremony(key_name: str) -> BaseResponse:
    """
    Close a Key Ceremony.
    """
    return _update_key_ceremony_state(key_name, KeyCeremonyState.CLOSED)


@router.post("/ceremony/challenge", tags=[KEY_CEREMONY])
def challenge_key_ceremony(key_name: str) -> BaseResponse:
    """
    Challenge a Key Ceremony.
    """
    return _update_key_ceremony_state(key_name, KeyCeremonyState.CHALLENGED)


@router.post("/ceremony/cancel", tags=[KEY_CEREMONY])
def cancel_key_ceremony(key_name: str) -> BaseResponse:
    """
    Cancel a Key Ceremony.
    """
    return _update_key_ceremony_state(key_name, KeyCeremonyState.CANCELLED)


@router.get("/ceremony/joint_key", tags=[KEY_CEREMONY])
def get_joint_key(
    key_name: str,
) -> ElectionJointKeyResponse:
    """
    Get The Joint Election Key
    """
    ceremony = _get_key_ceremony(key_name)
    if not ceremony.election_joint_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=f"No joint key for {key_name}",
        )

    return ElectionJointKeyResponse(
        status=ResponseStatus.SUCCESS,
        joint_key=write_json_object(ceremony.election_joint_key),
    )


def _validate_can_publish(ceremony: KeyCeremony) -> None:
    # TODO: better validation
    for guardian_id, state in ceremony.guardian_status.items():
        if (
            state.public_key_shared != KeyCeremonyGuardianStatus.COMPLETE
            or state.backups_shared != KeyCeremonyGuardianStatus.COMPLETE
            or state.backups_verified != KeyCeremonyGuardianStatus.COMPLETE
        ):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=f"Publish Constraint not satisfied for {guardian_id}",
            )


def _get_guardian(guardian_id: str) -> KeyCeremonyGuardian:
    try:
        with get_repository(CLIENT_ID, DataCollection.GUARDIAN) as repository:
            query_result = repository.get({"guardian_id": guardian_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {guardian_id}",
                )

            return read_json_object(query_result, KeyCeremonyGuardian)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get key ceremony guardian failed",
        ) from error


def _update_guardian(guardian_id: str, guardian: KeyCeremonyGuardian) -> BaseResponse:
    try:
        with get_repository(CLIENT_ID, DataCollection.GUARDIAN) as repository:
            query_result = repository.get({"guardian_id": guardian_id})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {guardian_id}",
                )
            repository.update({"guardian_id": guardian_id}, guardian.dict())
            return BaseResponse(status=ResponseStatus.SUCCESS)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update guardian failed",
        ) from error


def _get_key_ceremony(key_name: str) -> KeyCeremony:
    try:
        with get_repository(CLIENT_ID, DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"guardian_id": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find guardian {key_name}",
                )

            return read_json_object(query_result, KeyCeremony)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="get key ceremony failed",
        ) from error


def _update_key_ceremony(key_name: str, ceremony: KeyCeremony) -> BaseResponse:
    try:
        with get_repository(CLIENT_ID, DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            repository.update({"key_name": key_name}, ceremony.dict())
            return BaseResponse(status=ResponseStatus.SUCCESS)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update election failed",
        ) from error


def _update_key_ceremony_state(
    key_name: str, new_state: KeyCeremonyState
) -> BaseResponse:
    try:
        with get_repository(CLIENT_ID, DataCollection.KEY_CEREMONY) as repository:
            query_result = repository.get({"key_name": key_name})
            if not query_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Could not find key ceremony {key_name}",
                )
            document = read_json_object(query_result, KeyCeremony)
            document.state = new_state

            repository.update({"key_name": key_name}, document.dict())
            return BaseResponse(status=ResponseStatus.SUCCESS)
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="update key ceremony state failed",
        ) from error