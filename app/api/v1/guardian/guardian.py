from typing import Any, Dict, List, Optional
import sys
from electionguard.types import GUARDIAN_ID
from fastapi import APIRouter, Body, status, HTTPException

from electionguard.auxiliary import AuxiliaryKeyPair, AuxiliaryPublicKey
from electionguard.election_polynomial import ElectionPolynomial
from electionguard.group import int_to_q_unchecked
from electionguard.key_ceremony import (
    ElectionKeyPair,
    ElectionPublicKey,
    ElectionPartialKeyBackup,
    ElectionPartialKeyChallenge,
    generate_election_key_pair,
    generate_rsa_auxiliary_key_pair,
    generate_election_partial_key_backup,
    generate_election_partial_key_challenge,
    verify_election_partial_key_backup,
    verify_election_partial_key_challenge,
)
from electionguard.rsa import rsa_decrypt, rsa_encrypt
from electionguard.serializable import read_json_object, write_json_object
from electionguard.utils import get_optional

from ....core.client import get_client_id
from ....core.guardian import get_guardian, update_guardian
from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseQueryRequest,
    BaseResponse,
    ResponseStatus,
    BackupChallengeRequest,
    BackupChallengeResponse,
    BackupReceiveVerificationRequest,
    BackupVerificationResponse,
    BackupVerificationRequest,
    ChallengeVerificationRequest,
    Guardian,
    CreateGuardianRequest,
    GuardianBackupResponse,
    GuardianBackupRequest,
)
from ..tags import GUARDIAN

router = APIRouter()

identity = lambda message, key: message


@router.get("", tags=[GUARDIAN])
def fetch_guardian(guardian_id: str, with_secrets: Optional[bool]) -> Guardian:
    """"""
    return get_guardian(guardian_id)


@router.post("", tags=[GUARDIAN])
def create_guardian(request: CreateGuardianRequest = Body(...)) -> BaseResponse:
    """
    Create a guardian for the election process with the associated keys
    """
    election_keys = generate_election_key_pair(
        request.guardian_id,
        request.sequence_order,
        request.quorum,
        int_to_q_unchecked(request.nonce) if request.nonce is not None else None,
    )
    if request.auxiliary_key_pair is None:
        auxiliary_keys = generate_rsa_auxiliary_key_pair(
            request.guardian_id, request.sequence_order
        )
    else:
        auxiliary_keys = read_json_object(request.auxiliary_key_pair, AuxiliaryKeyPair)
    if not election_keys:
        raise HTTPException(
            status_code=500,
            detail="Election keys failed to be generated",
        )
    if not auxiliary_keys:
        raise HTTPException(
            status_code=500, detail="Auxiliary keys failed to be generated"
        )
    guardian = Guardian(
        id=request.guardian_id,
        sequence_order=request.sequence_order,
        number_of_guardians=request.number_of_guardians,
        quorum=request.quorum,
        election_keys=ElectionKeyPair(
            owner_id=request.guardian_id,
            sequence_order=request.sequence_order,
            key_pair=election_keys.key_pair,
            polynomial=election_keys.polynomial,
        ),
        auxiliary_keys=AuxiliaryKeyPair(
            owner_id=request.guardian_id,
            sequence_order=request.sequence_order,
            public_key=auxiliary_keys.public_key,
            secret_key=auxiliary_keys.secret_key,
        ),
    )

    try:
        with get_repository(get_client_id(), DataCollection.GUARDIAN) as repository:
            query_result = repository.get({"guardian_id": request.guardian_id})
            if not query_result:
                repository.set(guardian.dict())
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


@router.post("/backup", response_model=GuardianBackupResponse, tags=[GUARDIAN])
def create_guardian_backup(request: GuardianBackupRequest) -> GuardianBackupResponse:
    """
    Generate all election partial key backups based on existing public keys
    :param request: Guardian backup request
    :return: Guardian backup
    """
    guardian = get_guardian(request.guardian_id)

    encrypt = identity if request.override_rsa else rsa_encrypt
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    for auxiliary_public_key in request.auxiliary_public_keys:
        backup = generate_election_partial_key_backup(
            request.guardian_id,
            read_json_object(guardian.election_keys["polynomial"], ElectionPolynomial),
            AuxiliaryPublicKey(
                auxiliary_public_key.owner_id,
                auxiliary_public_key.sequence_order,
                auxiliary_public_key.key,
            ),
            encrypt,
        )
        if not backup:
            raise HTTPException(
                status_code=500,
                detail=f"Backup failed to be generated for {auxiliary_public_key.owner_id}",
            )
        backups[auxiliary_public_key.owner_id] = backup

    # TODO: serialize the backups, probably through the dicts

    return GuardianBackupResponse(
        status=ResponseStatus.SUCCESS,
        guardian_id=request.guardian_id,
        election_partial_key_backups=backups,
    )


@router.post("/backup/receive", tags=[GUARDIAN])
def receive_backup(request: BackupReceiveVerificationRequest) -> BaseResponse:
    """Receive and verify election partial key backup value is in polynomial."""
    guardian = get_guardian(request.guardian_id)
    backup = read_json_object(
        request.election_partial_key_backup, ElectionPartialKeyBackup
    )
    election_key = read_json_object(
        guardian.cohort_election_keys[backup.owner_id], ElectionPublicKey
    )
    auxiliary_key = read_json_object(
        guardian.cohort_auxiliary_keys[backup.owner_id], AuxiliaryKeyPair
    )
    decrypt = identity if request.override_rsa else rsa_decrypt
    verification = verify_election_partial_key_backup(
        request.guardian_id,
        backup,
        election_key,
        auxiliary_key,
        decrypt,
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Backup verification process failed",
        )

    guardian.cohort_backups[backup.owner_id] = backup
    return BaseResponse(status=ResponseStatus.SUCCESS)


@router.post("/backup/verify", tags=[GUARDIAN])
def verify_backup(request: BackupVerificationRequest) -> BackupVerificationResponse:
    """Verify election partial key backup value is in polynomial."""

    decrypt = identity if request.override_rsa else rsa_decrypt
    verification = verify_election_partial_key_backup(
        request.verifier_id,
        read_json_object(request.election_partial_key_backup, ElectionPartialKeyBackup),
        read_json_object(request.election_public_key, ElectionPublicKey),
        read_json_object(request.auxiliary_key_pair, AuxiliaryKeyPair),
        decrypt,
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Backup verification process failed",
        )
    return BackupVerificationResponse(
        status=ResponseStatus.SUCCESS, verification=write_json_object(verification)
    )


@router.post("/challenge", tags=[GUARDIAN])
def create_backup_challenge(request: BackupChallengeRequest) -> BaseResponse:
    """Publish election backup challenge of election partial key verification."""
    guardian = get_guardian(request.guardian_id)

    challenge = generate_election_partial_key_challenge(
        read_json_object(request.election_partial_key_backup, ElectionPartialKeyBackup),
        read_json_object(guardian.election_keys.polynomial, ElectionPolynomial),
    )
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup challenge generation failed",
        )

    return BackupChallengeResponse(
        status=ResponseStatus.SUCCESS, challenge=write_json_object(challenge)
    )


@router.post("/challenge/verify", tags=[GUARDIAN])
def verify_challenge(
    request: ChallengeVerificationRequest,
) -> BackupVerificationResponse:
    """Verify challenge of previous verification of election partial key."""
    verification = verify_election_partial_key_challenge(
        request.verifier_id,
        read_json_object(
            request.election_partial_key_challenge, ElectionPartialKeyChallenge
        ),
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Challenge verification process failed",
        )
    return BackupVerificationResponse(
        status=ResponseStatus.SUCCESS, verification=write_json_object(verification)
    )
