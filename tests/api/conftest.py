import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


class FakeDB:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


async def override_get_db():
    yield FakeDB()


@pytest.fixture
def api_client():
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
