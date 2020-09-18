from copy import deepcopy
from typing import Dict, List
from fastapi.testclient import TestClient

from app.core.config import ApiMode, Settings
from app.main import get_app

from . import api_utils

_api_client = TestClient(get_app(Settings(API_MODE=ApiMode.guardian)))


def create_guardian(
    guardian_id: str, sequence_order: int, number_of_guardians: int, quorum: int
) -> Dict:
    request = {
        "id": guardian_id,
        "sequence_order": sequence_order,
        "number_of_guardians": number_of_guardians,
        "quorum": quorum,
    }
    return api_utils.send_post_request(_api_client, "guardian", request)


def create_guardian_backup(guardian: Dict) -> Dict:
    auxiliary_public_key = {
        "owner_id": guardian["id"],
        "sequence_order": guardian["sequence_order"],
        "key": guardian["auxiliary_key_pair"]["public_key"],
    }
    request = {
        "guardian_id": guardian["id"],
        "quorum": guardian["quorum"],
        "election_polynomial": deepcopy(guardian["election_key_pair"]["polynomial"]),
        "auxiliary_public_keys": [auxiliary_public_key],
        "override_rsa": True,
    }
    return api_utils.send_post_request(_api_client, "guardian/backup", request)


def decrypt_tally_share(
    guardian: Dict, encrypted_tally: Dict, description: Dict, context: Dict
) -> Dict:
    request = {
        "guardian": guardian,
        "encrypted_tally": encrypted_tally,
        "description": description,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "tally/decrypt-share", request)


def decrypt_ballot_shares(
    encrypted_ballots: List[Dict], guardian: Dict, context: Dict
) -> Dict:
    request = {
        "encrypted_ballots": encrypted_ballots,
        "guardian": guardian,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/decrypt-shares", request)
