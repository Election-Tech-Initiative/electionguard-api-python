from fastapi import APIRouter, Body, HTTPException, Request, status

from electionguard.key_ceremony import (
    PublicKeySet,
    ElectionPartialKeyBackup,
    ElectionPartialKeyVerification,
    ElectionPartialKeyChallenge,
)
from electionguard.serializable import write_json_object, read_json_object

from ....core.key_guardian import get_key_guardian, update_key_guardian
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
from ..tags import KEY_CEREMONY

router = APIRouter()


# ROUND 1: Announce guardians with public keys
@router.post("/guardian/announce", response_model=BaseResponse, tags=[KEY_CEREMONY])
def announce_guardian(
    request: Request,
    data: GuardianAnnounceRequest = Body(...),
) -> BaseResponse:
    """
    Announce the guardian as present and participating in the Key Ceremony.
    """
    keyset = read_json_object(data.public_keys, PublicKeySet)
    guardian_id = keyset.election.owner_id

    ceremony = get_key_ceremony(data.key_name, request.app.state.settings)
    guardian = get_key_guardian(data.key_name, guardian_id, request.app.state.settings)

    _validate_can_participate(ceremony, guardian)

    guardian.public_keys = write_json_object(keyset)
    ceremony.guardian_status[
        guardian_id
    ].public_key_shared = KeyCeremonyGuardianStatus.COMPLETE

    update_key_guardian(
        data.key_name, guardian_id, guardian, request.app.state.settings
    )
    return update_key_ceremony(data.key_name, ceremony, request.app.state.settings)


# ROUND 2: Share Election Partial Key Backups for compensating
@router.post("/guardian/backup", response_model=BaseResponse, tags=[KEY_CEREMONY])
def share_backups(
    request: Request,
    data: GuardianSubmitBackupRequest = Body(...),
) -> BaseResponse:
    """
    Share Election Partial Key Backups to be distributed to the other guardians.
    """
    ceremony = get_key_ceremony(data.key_name, request.app.state.settings)
    guardian = get_key_guardian(
        data.key_name, data.guardian_id, request.app.state.settings
    )

    _validate_can_participate(ceremony, guardian)

    backups = [
        read_json_object(backup, ElectionPartialKeyBackup) for backup in data.backups
    ]

    guardian.backups = [write_json_object(backup) for backup in backups]
    ceremony.guardian_status[
        data.guardian_id
    ].backups_shared = KeyCeremonyGuardianStatus.COMPLETE

    update_key_guardian(
        data.key_name, data.guardian_id, guardian, request.app.state.settings
    )
    return update_key_ceremony(data.key_name, ceremony, request.app.state.settings)


# ROUND 3: Share verifications of backups
@router.post("/guardian/verify", response_model=BaseResponse, tags=[KEY_CEREMONY])
def verify_backups(
    request: Request,
    data: GuardianSubmitVerificationRequest = Body(...),
) -> BaseResponse:
    """
    Share the reulsts of verifying the other guardians' backups.
    """
    ceremony = get_key_ceremony(data.key_name, request.app.state.settings)
    guardian = get_key_guardian(
        data.key_name, data.guardian_id, request.app.state.settings
    )

    _validate_can_participate(ceremony, guardian)

    verifications = [
        read_json_object(verification, ElectionPartialKeyVerification)
        for verification in data.verifications
    ]

    guardian.verifications = [
        write_json_object(verification) for verification in verifications
    ]
    ceremony.guardian_status[data.guardian_id].backups_verified = (
        KeyCeremonyGuardianStatus.COMPLETE
        if all([verification.verified for verification in verifications])
        else KeyCeremonyGuardianStatus.ERROR
    )

    update_key_guardian(
        data.key_name, data.guardian_id, guardian, request.app.state.settings
    )
    return update_key_ceremony(data.key_name, ceremony, request.app.state.settings)


# ROUND 4 (Optional): If a verification fails, guardian must issue challenge
@router.post("/guardian/challenge", response_model=BaseResponse, tags=[KEY_CEREMONY])
def challenge_backups(
    request: Request,
    data: GuardianSubmitChallengeRequest = Body(...),
) -> BaseResponse:
    """
    Submit challenges to the other guardians' backups.
    """
    ceremony = get_key_ceremony(data.key_name, request.app.state.settings)
    guardian = get_key_guardian(
        data.key_name, data.guardian_id, request.app.state.settings
    )

    _validate_can_participate(ceremony, guardian)

    challenges = [
        read_json_object(challenge, ElectionPartialKeyChallenge)
        for challenge in data.challenges
    ]

    guardian.challenges = [write_json_object(challenge) for challenge in challenges]
    ceremony.guardian_status[
        data.guardian_id
    ].backups_verified = KeyCeremonyGuardianStatus.ERROR

    update_key_guardian(
        data.key_name, data.guardian_id, guardian, request.app.state.settings
    )
    return update_key_ceremony(data.key_name, ceremony, request.app.state.settings)


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
