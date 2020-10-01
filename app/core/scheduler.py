from electionguard.scheduler import Scheduler
from functools import lru_cache

__all__ = ["get_scheduler"]


@lru_cache
def get_scheduler() -> Scheduler:
    return Scheduler()
