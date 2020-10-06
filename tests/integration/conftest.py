from typing import Generator
import pytest
from app.core.scheduler import get_scheduler


@pytest.yield_fixture(scope="session", autouse=True)
def scheduler_lifespan() -> Generator[None, None, None]:
    """
    Ensure that the global scheduler singleton is
    torn down when tests finish.  Otherwise, the test runner will hang
    waiting for the scheduler to complete.
    """
    yield None
    scheduler = get_scheduler()
    scheduler.close()
