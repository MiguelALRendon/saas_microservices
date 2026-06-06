"""Configura entorno e import path para los tests del servicio.

Debe ejecutarse ANTES de importar `config`/`app` (config lee DATABASE_URL en import-time).
Usa un SQLite en archivo temporal para que todas las conexiones compartan la misma DB.
"""

import os
import sys
import tempfile

# Raíz del servicio en sys.path para `import config` / `import app`.
_SERVICE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# Entorno de test (antes de importar config).
_DB_DIR = tempfile.mkdtemp(prefix="catalogues_test_")
_DB_PATH = os.path.join(_DB_DIR, "test.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"
os.environ["INTERNAL_SERVICE_SECRET"] = "test-internal-secret"
os.environ.setdefault("BRANCH_SERVICE_URL", "http://localhost:59999")  # inalcanzable a propósito

import pytest  # noqa: E402


@pytest.fixture()
def client():
    from app import create_app, db

    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

    test_client = app.test_client()
    # Inyecta el header de confianza inter-servicio en cada request.
    secret = os.environ["INTERNAL_SERVICE_SECRET"]

    class TrustedClient:
        def _headers(self, extra):
            h = {"X-Internal-Service-Secret": secret}
            if extra:
                h.update(extra)
            return h

        def get(self, path, **kw):
            return test_client.get(path, headers=self._headers(kw.pop("headers", None)), **kw)

        def post(self, path, **kw):
            return test_client.post(path, headers=self._headers(kw.pop("headers", None)), **kw)

        def put(self, path, **kw):
            return test_client.put(path, headers=self._headers(kw.pop("headers", None)), **kw)

        def delete(self, path, **kw):
            return test_client.delete(path, headers=self._headers(kw.pop("headers", None)), **kw)

    return TrustedClient()
