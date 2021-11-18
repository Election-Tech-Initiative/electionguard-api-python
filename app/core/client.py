# TODO: multi-tenancy
DEFAULT_CLIENT_ID = "electionguard-default-client-id"

__all__ = [
    "get_client_id",
]


def get_client_id() -> str:
    return DEFAULT_CLIENT_ID
