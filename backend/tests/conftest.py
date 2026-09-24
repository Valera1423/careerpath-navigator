import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("ALLOW_INSECURE_INIT_DATA", "true")

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_db() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-Max-User-Id": "test-user-1"}