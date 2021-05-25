from typing import Dict, List, Optional
from fastapi.testclient import TestClient

from app.core.config import ApiMode, Settings
from app.main import get_app

from . import api_utils

_api_client = TestClient(get_app(Settings(API_MODE=ApiMode.MEDIATOR)))


def combine_election_keys(election_public_keys: List[Dict]) -> Dict:
    """
    Combine the public keys of all guardians into a single ElGamal public key
    for use throughout the election
    """
    request = {"election_public_keys": election_public_keys}
    return api_utils.send_post_request(_api_client, "key/election/combine", request)


def create_election_context(
    description: Dict, elgamal_public_key: str, number_of_guardians: int, quorum: int
) -> Dict:
    """
    Construct an encryption context for use throughout the election to encrypt and decrypt data
    """
    request = {
        "description": description,
        "elgamal_public_key": elgamal_public_key,
        "number_of_guardians": number_of_guardians,
        "quorum": quorum,
    }
    return api_utils.send_post_request(_api_client, "election/context", request)


def cast_ballot(ballot: Dict, description: Dict, context: Dict) -> Dict:
    request = {
        "ballot": ballot,
        "description": description,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/cast", request)


def spoil_ballot(ballot: Dict, description: Dict, context: Dict) -> Dict:
    request = {
        "ballot": ballot,
        "description": description,
        "context": context,
    }
    return api_utils.send_post_request(_api_client, "ballot/spoil", request)


def encrypt_ballots(
    ballots: List[Dict],
    seed_hash: str,
    nonce: Optional[str],
    description: Dict,
    context: Dict,
) -> Dict:

    request = {
        "ballots": ballots,
        "seed_hash": seed_hash,
        "nonce": nonce,
        "description": description,
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
