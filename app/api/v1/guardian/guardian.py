from typing import Dict
import sys

from fastapi import APIRouter, Body, status, HTTPException, Request

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


@router.get("", response_model=Guardian, tags=[GUARDIAN])
def fetch_guardian(request: Request, guardian_id: str) -> Guardian:
    """
    Fetch a guardian.  The response includes the private key information of the guardian.
    """
    return get_guardian(guardian_id, request.app.state.settings)


@router.get("/public-keys", response_model=GuardianPublicKeysResponse, tags=[GUARDIAN])
def fetch_public_keys(request: Request, guardian_id: str) -> GuardianPublicKeysResponse:
    """
    Fetch the public key information for a guardian.
    """
    guardian = get_guardian(guardian_id, request.app.state.settings)
    sdk_guardian = to_sdk_guardian(guardian)

    return GuardianPublicKeysResponse(
        public_keys=write_json_object(sdk_guardian.share_public_keys()),
    )


@router.post("", response_model=GuardianPublicKeysResponse, tags=[GUARDIAN])
def create_guardian(
    request: Request,
    data: CreateGuardianRequest = Body(...),
) -> GuardianPublicKeysResponse:
    """
    Create a guardian for the election process with the associated keys.
    """
    election_keys = generate_election_key_pair(
        data.guardian_id,
        data.sequence_order,
        data.quorum,
        hex_to_q_unchecked(data.nonce) if data.nonce is not None else None,
    )
    if data.auxiliary_key_pair is None:
        auxiliary_keys = generate_rsa_auxiliary_key_pair(
            data.guardian_id, data.sequence_order
        )
    else:
        auxiliary_keys = read_json_object(data.auxiliary_key_pair, AuxiliaryKeyPair)
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
        guardian_id=data.guardian_id,
        sequence_order=data.sequence_order,
        number_of_guardians=data.number_of_guardians,
        quorum=data.quorum,
        election_keys=write_json_object(election_keys),
        auxiliary_keys=write_json_object(auxiliary_keys),
    )
    sdk_guardian = to_sdk_guardian(guardian)

    try:
        with get_repository(
            get_client_id(), DataCollection.GUARDIAN, request.app.state.settings
        ) as repository:
            query_result = repository.get({"guardian_id": data.guardian_id})
            if not query_result:
                repository.set(guardian.dict())
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Already exists {data.guardian_id}",
                )
    except Exception as error:
        print(sys.exc_info())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submit ballots failed",
        ) from error

    return GuardianPublicKeysResponse(
        public_keys=write_json_object(sdk_guardian.share_public_keys()),
    )


@router.post("/backup", response_model=GuardianBackupResponse, tags=[GUARDIAN])
def create_guardian_backup(
    request: Request, data: GuardianBackupRequest
) -> GuardianBackupResponse:
    """
    Generate election partial key backups by using the public keys included in the request.
    """
    guardian = get_guardian(data.guardian_id, request.app.state.settings)
    polynomial = read_json_object(
        guardian.election_keys["polynomial"], ElectionPolynomial
    )

    encrypt = identity if data.override_rsa else rsa_encrypt
    backups: Dict[GUARDIAN_ID, ElectionPartialKeyBackup] = {}
    cohort_public_keys: Dict[GUARDIAN_ID, PublicKeySet] = {}
    for key_set in data.public_keys:
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
    update_guardian(guardian.guardian_id, guardian, request.app.state.settings)

    return GuardianBackupResponse(
        guardian_id=data.guardian_id,
        backups=[write_json_object(backup) for (id, backup) in backups.items()],
    )


@router.post("/backup/verify", response_model=BaseResponse, tags=[GUARDIAN])
def verify_backup(request: Request, data: BackupVerificationRequest) -> BaseResponse:
    """Receive and verify election partial key backup value is in polynomial."""
    guardian = get_guardian(data.guardian_id, request.app.state.settings)
    auxiliary_keys = read_json_object(guardian.auxiliary_keys, AuxiliaryKeyPair)
    backup = read_json_object(data.backup, ElectionPartialKeyBackup)
    cohort_keys = read_json_object(
        guardian.cohort_public_keys[backup.owner_id], PublicKeySet
    )
    decrypt = identity if data.override_rsa else rsa_decrypt
    verification = verify_election_partial_key_backup(
        data.guardian_id,
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
    update_guardian(guardian.guardian_id, guardian, request.app.state.settings)

    return BaseResponse()


@router.post("/challenge", response_model=BaseResponse, tags=[GUARDIAN])
def create_backup_challenge(
    request: Request, data: BackupChallengeRequest
) -> BaseResponse:
    """Publish election backup challenge of election partial key verification."""
    guardian = get_guardian(data.guardian_id, request.app.state.settings)
    polynomial = read_json_object(
        guardian.election_keys["polynomial"], ElectionPolynomial
    )
    backup = read_json_object(data.backup, ElectionPartialKeyBackup)

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
    update_guardian(guardian.guardian_id, guardian, request.app.state.settings)
    return BackupChallengeResponse(challenge=write_json_object(challenge))


@router.post(
    "/challenge/verify", response_model=BackupVerificationResponse, tags=[GUARDIAN]
)
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
    return BackupVerificationResponse(verification=write_json_object(verification))
