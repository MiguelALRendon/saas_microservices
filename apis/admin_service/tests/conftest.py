"""Setup de tests del BFF admin: env + import path + cliente Flask."""

import os
import sys

_SERVICE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

os.environ["JWT_SECRET_KEY"] = "admin-test-secret-of-sufficient-length-123456"
os.environ["INTERNAL_SERVICE_SECRET"] = "test-internal-secret"
os.environ["AUTH_SERVICE_URL"] = "http://auth.test"
os.environ["CATALOGUES_SERVICE_URL"] = "http://catalogues.test"
os.environ["BRANCH_SERVICE_URL"] = "http://branch.test"

import pytest  # noqa: E402


@pytest.fixture()
def app():
    from app import create_app
    from app.utils import session_store

    session_store._store.clear()
    return create_app()


@pytest.fixture()
def client(app):
    return app.test_client()
