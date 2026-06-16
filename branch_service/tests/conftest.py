"""Setup de tests de branch_service: env + import path + cliente con header de confianza."""

import os
import sys
import tempfile

_SERVICE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

_DB_DIR = tempfile.mkdtemp(prefix="branch_test_")
_DB_PATH = os.path.join(_DB_DIR, "test.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"
os.environ["INTERNAL_SERVICE_SECRET"] = "test-internal-secret"
os.environ.setdefault("CATALOGUES_SERVICE_URL", "http://localhost:59996")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:59995")

import pytest  # noqa: E402


@pytest.fixture()
def client():
    from app import create_app, db

    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

    inner = app.test_client()
    secret = os.environ["INTERNAL_SERVICE_SECRET"]

    class TrustedClient:
        def _h(self, extra):
            h = {"X-Internal-Service-Secret": secret}
            if extra:
                h.update(extra)
            return h

        def get(self, p, **kw):
            return inner.get(p, headers=self._h(kw.pop("headers", None)), **kw)

        def post(self, p, **kw):
            return inner.post(p, headers=self._h(kw.pop("headers", None)), **kw)

        def put(self, p, **kw):
            return inner.put(p, headers=self._h(kw.pop("headers", None)), **kw)

        def delete(self, p, **kw):
            return inner.delete(p, headers=self._h(kw.pop("headers", None)), **kw)

    return TrustedClient()
