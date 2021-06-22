from typing import Dict, List, Optional
from fastapi.testclient import TestClient

from app.core.settings import ApiMode, Settings
from app.main import get_app

from . import api_utils

_api_client = TestClient(get_app(Settings(API_MODE=ApiMode.MEDIATOR)))


def combine_election_keys(key_name: str, election_public_keys: List[Dict]) -> Dict:
    """
    Combine the public keys of all guardians into a single ElGamal public key
    for use throughout the election
    """
    request = {"key_name": key_name, "election_public_keys": election_public_keys}
    return api_utils.send_post_request(_api_client, "key/ceremony/combine", request)


def get_election(election_id: str) -> Dict:
    return api_utils.send_get_request(
        _api_client, f"election?election_id={election_id}"
    )


def submit_election(
    election_id: str,
    context: Dict,
    manifest: Dict,
) -> Dict:
    """
    Construct an encryption context for use throughout the election to encrypt and decrypt data
    """
    request = {"election_id": election_id, "context": context, "manifest": manifest}
    return api_utils.send_put_request(_api_client, "election", request)


def open_election(election_id: str) -> Dict:
    return api_utils.send_post_request(
        _api_client, f"election/open?election_id={election_id}"
    )


def close_election(election_id: str) -> Dict:
    return api_utils.send_post_request(
        _api_client, f"election/close?election_id={election_id}"
    )


def publish_election(election_id: str) -> Dict:
    return api_utils.send_post_request(
        _api_client, f"election/publish?election_id={election_id}"
    )


def build_election_context(
    manifest: Dict,
    elgamal_public_key: str,
    commitment_hash: str,
    number_of_guardians: int,
    quorum: int,
) -> Dict:
    """
    Construct an encryption context for use throughout the election to encrypt and decrypt data
    """
    request = {
        "manifest": manifest,
        "elgamal_public_key": elgamal_public_key,
        "commitment_hash": commitment_hash,
        "number_of_guardians": number_of_guardians,
        "quorum": quorum,
    }
    return api_utils.send_post_request(_api_client, "election/context", request)


def get_manifest(manifest_hash: str) -> Dict:
    return api_utils.send_get_request(
        _api_client, f"manifest?manifest_hash={manifest_hash}"
    )


def submit_manifest(
    manifest: Dict,
) -> Dict:
    request = {
        "manifest": manifest,
    }
    return api_utils.send_put_request(_api_client, "manifest", request)


def validate_manifest(
    manifest: Dict,
) -> Dict:
    request = {
        "manifest": manifest,
    }
    return api_utils.send_post_request(_api_client, "manifest/validate", request)


def cast_ballot(election_id: str, ballot: Dict, manifest: Dict, context: Dict) -> Dict:
    request = {
        "election_id": election_id,
        "ballots": [ballot],
        "manifest": manifest,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/cast", request)


def spoil_ballot(election_id: str, ballot: Dict, manifest: Dict, context: Dict) -> Dict:
    request = {
        "election_id": election_id,
        "ballots": [ballot],
        "manifest": manifest,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/spoil", request)


def submit_ballot(
    election_id: str, ballot: Dict, manifest: Dict, context: Dict
) -> Dict:
    request = {
        "election_id": election_id,
        "ballots": [ballot],
        "manifest": manifest,
        "context": context,
    }
    return api_utils.send_put_request(_api_client, "ballot/submit", request)


def validate_ballot(ballot: Dict, manifest: Dict, context: Dict) -> Dict:
    request = {
        "ballots": ballot,
        "manifest": manifest,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/validate", request)


def encrypt_ballots(
    ballots: List[Dict],
    seed_hash: str,
    nonce: Optional[str],
    manifest: Dict,
    context: Dict,
) -> Dict:

    request = {
        "ballots": ballots,
        "seed_hash": seed_hash,
        "nonce": nonce,
        "manifest": manifest,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/encrypt", request)


def start_tally(ballots: List[Dict], description: Dict, context: Dict) -> Dict:
    request = {
        "ballots": ballots,
        "description": description,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "tally", request)


def append_tally(
    ballots: List[Dict], encrypted_tally: Dict, description: Dict, context: Dict
) -> Dict:
    request = {
        "ballots": ballots,
        "encrypted_tally": encrypted_tally,
        "description": description,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "tally/append", request)


def decrypt_tally(
    encrypted_tally: Dict, shares: Dict[str, Dict], description: Dict, context: Dict
) -> Dict:
    request = {
        "encrypted_tally": encrypted_tally,
        "shares": shares,
        "description": description,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "tally/decrypt", request)


def decrypt_ballots(
    encrypted_ballots: List[Dict],
    shares: Dict[str, List[Dict]],
    context: Dict,
) -> Dict:
    request = {
        "encrypted_ballots": encrypted_ballots,
        "shares": shares,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/decrypt", request)
