from typing import Dict
import sys

from fastapi import APIRouter, Body, status, HTTPException

from electionguard.auxiliary import AuxiliaryKeyPair
from electionguard.election_polynomial import ElectionPolynomial
from electionguard.group import hex_to_q_unchecked
from electionguard.key_ceremony import (
    PublicKeySet,
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
from electionguard.types import GUARDIAN_ID

from ....core.client import get_client_id
from ....core.guardian import get_guardian, update_guardian
from ....core.repository import get_repository, DataCollection
from ..models import (
    BaseResponse,
    ResponseStatus,
    BackupChallengeRequest,
    BackupChallengeResponse,
    BackupVerificationRequest,
    BackupVerificationResponse,
    ChallengeVerificationRequest,
    Guardian,
    CreateGuardianRequest,
    GuardianPublicKeysResponse,
    GuardianBackupResponse,
    GuardianBackupRequest,
    to_sdk_guardian,
)
from ..tags import GUARDIAN

router = APIRouter()

identity = lambda message, key: message


@router.get("", tags=[GUARDIAN])
def fetch_guardian(guardian_id: str) -> Guardian:
    """
    Fetch a guardian.  The response includes the private key information of the guardian.
    """
    return get_guardian(guardian_id)


@router.get("/public-keys", tags=[GUARDIAN])
def fetch_public_keys(guardian_id: str) -> GuardianPublicKeysResponse:
    """
    Fetch the public key information for a guardian.
    """
    guardian = get_guardian(guardian_id)
    sdk_guardian = to_sdk_guardian(guardian)

    return GuardianPublicKeysResponse(
        status=ResponseStatus.SUCCESS,
        public_keys=write_json_object(sdk_guardian.share_public_keys()),
    )


@router.post("", tags=[GUARDIAN])
def create_guardian(request: CreateGuardianRequest = Body(...)) -> BaseResponse:
    """
    Create a guardian for the election process with the associated keys.
    """
    election_keys = generate_election_key_pair(
        request.guardian_id,
        request.sequence_order,
        request.quorum,
        hex_to_q_unchecked(request.nonce) if request.nonce is not None else None,
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
        guardian_id=request.guardian_id,
        sequence_order=request.sequence_order,
        number_of_guardians=request.number_of_guardians,
        quorum=request.quorum,
        election_keys=write_json_object(election_keys),
        auxiliary_keys=write_json_object(auxiliary_keys),
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
    Generate election partial key backups by using the public keys included in the request.
    """
    guardian = get_guardian(request.guardian_id)
    polynomial = read_json_object(
        guardian.election_keys["polynomial"], ElectionPolynomial
    )

    encrypt = identity if request.override_rsa else rsa_encrypt
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    cohort_public_keys: Dict[GUARDIAN_ID, PublicKeySet] = {}
    for key_set in request.public_keys:
        cohort_key_set = read_json_object(key_set, PublicKeySet)
        cohort_owner_id = cohort_key_set.election.owner_id

        backup = generate_election_partial_key_backup(
            guardian.guardian_id,
            polynomial,
            cohort_key_set.auxiliary,
            encrypt,
        )
        if not backup:
            raise HTTPException(
                status_code=500,
                detail=f"Backup failed to be generated for {cohort_owner_id}",
            )
        backups[cohort_owner_id] = backup
        cohort_public_keys[cohort_owner_id] = cohort_key_set

    guardian.backups = {
        owner_id: write_json_object(backup) for (owner_id, backup) in backups.items()
    }
    guardian.cohort_public_keys = {
        owner_id: write_json_object(key_set)
        for (owner_id, key_set) in cohort_public_keys.items()
    }
    update_guardian(guardian.guardian_id, guardian)

    return GuardianBackupResponse(
        status=ResponseStatus.SUCCESS,
        guardian_id=request.guardian_id,
        backups=[write_json_object(backup) for (id, backup) in backups.items()],
    )


@router.post("/backup/verify", tags=[GUARDIAN])
def verify_backup(request: BackupVerificationRequest) -> BaseResponse:
    """Receive and verify election partial key backup value is in polynomial."""
    guardian = get_guardian(request.guardian_id)
    auxiliary_keys = read_json_object(guardian.auxiliary_keys, AuxiliaryKeyPair)
    backup = read_json_object(request.backup, ElectionPartialKeyBackup)
    cohort_keys = read_json_object(
        guardian.cohort_public_keys[backup.owner_id], PublicKeySet
    )
    decrypt = identity if request.override_rsa else rsa_decrypt
    verification = verify_election_partial_key_backup(
        request.guardian_id,
        backup,
        cohort_keys.election,
        auxiliary_keys,
        decrypt,
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Backup verification process failed",
        )

    guardian.cohort_backups[backup.owner_id] = write_json_object(backup)
    guardian.cohort_verifications[backup.owner_id] = write_json_object(verification)
    update_guardian(guardian.guardian_id, guardian)

    return BaseResponse(status=ResponseStatus.SUCCESS)


@router.post("/challenge", tags=[GUARDIAN])
def create_backup_challenge(request: BackupChallengeRequest) -> BaseResponse:
    """Publish election backup challenge of election partial key verification."""
    guardian = get_guardian(request.guardian_id)
    polynomial = read_json_object(
        guardian.election_keys["polynomial"], ElectionPolynomial
    )
    backup = read_json_object(request.backup, ElectionPartialKeyBackup)

    challenge = generate_election_partial_key_challenge(
        backup,
        polynomial,
    )
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup challenge generation failed",
        )

    guardian.cohort_challenges[backup.owner_id] = write_json_object(challenge)
    update_guardian(guardian.guardian_id, guardian)
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
        read_json_object(request.challenge, ElectionPartialKeyChallenge),
    )
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Challenge verification process failed",
        )
    return BackupVerificationResponse(
        status=ResponseStatus.SUCCESS, verification=write_json_object(verification)
    )
