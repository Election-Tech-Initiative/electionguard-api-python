from fastapi import APIRouter, Body, HTTPException, status

from electionguard.key_ceremony import (
    PublicKeySet,
    ElectionPartialKeyBackup,
    ElectionPartialKeyVerification,
    ElectionPartialKeyChallenge,
)
from electionguard.serializable import write_json_object, read_json_object

from ....core.guardian import get_guardian, update_guardian
from ....core.key_ceremony import get_key_ceremony, update_key_ceremony
from ..models import (
    BaseResponse,
    GuardianAnnounceRequest,
    GuardianSubmitBackupRequest,
    GuardianSubmitVerificationRequest,
    GuardianSubmitChallengeRequest,
    KeyCeremony,
    KeyCeremonyState,
    KeyCeremonyGuardian,
    KeyCeremonyGuardianStatus,
)
from ..tags import KEY_GUARDIAN

router = APIRouter()


# ROUND 1: Announce guardians with public keys
@router.post("/guardian/announce", tags=[KEY_GUARDIAN])
def announce_guardian(
    request: GuardianAnnounceRequest = Body(...),
) -> BaseResponse:
    """
    Announce the guardian as present and participating in the Key Ceremony.
    """
    keyset = read_json_object(request.public_keys, PublicKeySet)
    guardian_id = keyset.election.owner_id

    ceremony = get_key_ceremony(request.key_name)
    guardian = get_guardian(guardian_id)

    _validate_can_participate(ceremony, guardian)

    guardian.public_keys = write_json_object(keyset)
    ceremony.guardian_status[
        guardian_id
    ].public_key_shared = KeyCeremonyGuardianStatus.COMPLETE

    update_guardian(guardian_id, guardian)
    return update_key_ceremony(request.key_name, ceremony)


# ROUND 2: Share Election Partial Key Backups for compensating
@router.post("/guardian/backup", tags=[KEY_GUARDIAN])
def share_backups(
    request: GuardianSubmitBackupRequest = Body(...),
) -> BaseResponse:
    """
    Share Election Partial Key Backups to be distributed to the other guardians.
    """
    ceremony = get_key_ceremony(request.key_name)
    guardian = get_guardian(request.guardian_id)

    _validate_can_participate(ceremony, guardian)

    backups = [
        read_json_object(backup, ElectionPartialKeyBackup) for backup in request.backups
    ]

    guardian.backups = [write_json_object(backup) for backup in backups]
    ceremony.guardian_status[
        request.guardian_id
    ].backups_shared = KeyCeremonyGuardianStatus.COMPLETE

    update_guardian(request.guardian_id, guardian)
    return update_key_ceremony(request.key_name, ceremony)


# ROUND 3: Share verifications of backups
@router.post("/guardian/verify", tags=[KEY_GUARDIAN])
def verify_backups(
    request: GuardianSubmitVerificationRequest = Body(...),
) -> BaseResponse:
    """
    Share the reulsts of verifying the other guardians' backups
    """
    ceremony = get_key_ceremony(request.key_name)
    guardian = get_guardian(request.guardian_id)

    _validate_can_participate(ceremony, guardian)

    verifications = [
        read_json_object(verification, ElectionPartialKeyVerification)
        for verification in request.verifications
    ]

    guardian.verifications = [
        write_json_object(verification) for verification in verifications
    ]
    ceremony.guardian_status[
        request.guardian_id
    ].backups_verified = KeyCeremonyGuardianStatus.COMPLETE

    update_guardian(request.guardian_id, guardian)
    return update_key_ceremony(request.key_name, ceremony)


# ROUND 4 (Optional): If a verification fails, guardian must issue challenge
@router.post("/guardian/challenge", tags=[KEY_GUARDIAN])
def challenge_backups(
    request: GuardianSubmitChallengeRequest = Body(...),
) -> BaseResponse:
    """
    Submit challenges to the other guardians' backups
    """
    ceremony = get_key_ceremony(request.key_name)
    guardian = get_guardian(request.guardian_id)

    _validate_can_participate(ceremony, guardian)

    challenges = [
        read_json_object(challenge, ElectionPartialKeyChallenge)
        for challenge in request.challenges
    ]

    guardian.challenges = [write_json_object(challenge) for challenge in challenges]
    ceremony.guardian_status[
        request.guardian_id
    ].backups_verified = KeyCeremonyGuardianStatus.ERROR

    update_guardian(request.guardian_id, guardian)
    return update_key_ceremony(request.key_name, ceremony)


def _validate_can_participate(
    ceremony: KeyCeremony, guardian: KeyCeremonyGuardian
) -> None:
    # TODO: better validation
    if ceremony.state != KeyCeremonyState.OPEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot announce for key ceremony state {ceremony.state}",
        )

    if guardian.guardian_id not in ceremony.guardian_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Guardian {guardian.guardian_id} not in ceremony",
        )
