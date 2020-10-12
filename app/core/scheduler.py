from functools import lru_cache
from electionguard.scheduler import Scheduler

__all__ = ["get_scheduler"]


@lru_cache
def get_scheduler() -> Scheduler:
    return Scheduler()
