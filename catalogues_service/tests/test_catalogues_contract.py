"""Contract tests para empresa / sistema / producto tras migrar a galurensoft_core.

Reusa la fixture `client` de conftest.py (SQLite en archivo temporal + header de confianza).
"""


# ── empresa ────────────────────────────────────────────────────────────────────
def _empresa(clave="E1"):
    return {
        "clave": clave, "nombre": "Acme", "folio": "F1", "urlLogo": "http://x/logo.png",
        "direccion": "Calle 1", "telefono": "555", "email": "a@b.com", "fkSistema": "sis-1",
    }


def test_empresa_create_persists_fkSistema(client):
    # Bug fix: la creación ahora funciona (antes fallaba por no persistir fkSistema NOT NULL).
    resp = client.post("/empresa/", json=_empresa())
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["fkSistema"] == "sis-1"
    assert body["estatus"] == "ACTIVO"
    assert set(body.keys()) == {
        "oid", "createdAt", "updatedAt", "creado_por", "editado_por", "estatus",
        "clave", "nombre", "folio", "urlLogo", "direccion", "telefono", "email", "fkSistema",
    }


def test_empresa_validation_requires_fkSistema(client):
    payload = _empresa()
    del payload["fkSistema"]
    resp = client.post("/empresa/", json=payload)
    assert resp.status_code == 400
    assert resp.get_json() == {"errors": ["fkSistema es requerido"]}


def test_empresa_duplicate_clave(client):
    client.post("/empresa/", json=_empresa())
    assert client.post("/empresa/", json=_empresa()).get_json() == {"errors": ["La clave ya existe"]}


def test_empresa_detail_has_local_and_external_envelopes(client):
    oid = client.post("/empresa/", json=_empresa()).get_json()["oid"]
    # una sucursal local bajo la empresa
    client.post("/sucursal/", json={
        "clave": "S1", "nombre": "Suc", "folio": "f", "direccion": "d", "fkEmpresa": oid,
    })
    body = client.get(f"/empresa/{oid}").get_json()
    assert body["sucursales"]["total"] == 1
    assert body["sucursales"]["data"][0]["clave"] == "S1"
    # cargos es externo (branch inalcanzable) -> envelope vacío
    assert body["cargos"]["total"] == 0
    assert body["cargos"]["has_more"] is False


def test_empresa_not_found_message(client):
    assert client.get("/empresa/nope").get_json() == {"errors": ["Empresa no encontrada"]}


def test_empresa_delete_message(client):
    oid = client.post("/empresa/", json=_empresa()).get_json()["oid"]
    assert client.delete(f"/empresa/{oid}").get_json() == {"message": "Empresa eliminada exitosamente"}


# ── sistema ────────────────────────────────────────────────────────────────────
def _sistema(clave="SIS1", api_key="k1"):
    return {"clave": clave, "nombre": "Sis", "descripcion": "d", "api_key": api_key}


def test_sistema_dual_uniqueness(client):
    client.post("/sistema/", json=_sistema())
    # misma clave -> error de clave
    assert client.post("/sistema/", json=_sistema(clave="SIS1", api_key="k2")).get_json() == {"errors": ["La clave ya existe"]}
    # mismo api_key -> error de api_key
    assert client.post("/sistema/", json=_sistema(clave="SIS2", api_key="k1")).get_json() == {"errors": ["El api_key ya existe"]}


def test_sistema_detail_lists_empresas(client):
    sid = client.post("/sistema/", json=_sistema()).get_json()["oid"]
    client.post("/empresa/", json=_empresa() | {"fkSistema": sid})
    body = client.get(f"/sistema/{sid}").get_json()
    assert body["empresas"]["total"] == 1


def test_sistema_messages(client):
    assert client.get("/sistema/nope").get_json() == {"errors": ["Sistema no encontrado"]}
    sid = client.post("/sistema/", json=_sistema()).get_json()["oid"]
    assert client.delete(f"/sistema/{sid}").get_json() == {"message": "Sistema eliminado exitosamente"}


# ── producto ───────────────────────────────────────────────────────────────────
def _producto(clave="P1", codigo="C1"):
    return {
        "clave": clave, "nombre": "Prod", "codigo_barras": codigo,
        "unidadMedida": "PIEZA", "is_especial": True, "fkProveedorMarca": "pm-1",
    }


def test_producto_create_coerces_unidad(client):
    resp = client.post("/producto/", json=_producto())
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["unidadMedida"] == "PIEZA"
    assert body["is_especial"] is True


def test_producto_invalid_unidad(client):
    payload = _producto()
    payload["unidadMedida"] = "GALAXIA"
    resp = client.post("/producto/", json=payload)
    assert resp.status_code == 400
    assert "unidadMedida inválida" in resp.get_json()["errors"][0]


def test_producto_dual_unique(client):
    client.post("/producto/", json=_producto())
    assert client.post("/producto/", json=_producto(clave="P1", codigo="C2")).get_json() == {"errors": ["La clave ya existe"]}
    assert client.post("/producto/", json=_producto(clave="P2", codigo="C1")).get_json() == {"errors": ["El código de barras ya existe"]}


def test_producto_bool_filter(client):
    client.post("/producto/", json=_producto(clave="A", codigo="CA") | {"is_especial": True})
    client.post("/producto/", json=_producto(clave="B", codigo="CB") | {"is_especial": False})
    especiales = client.get("/producto/?is_especial=true").get_json()
    assert especiales["total"] == 1 and especiales["data"][0]["clave"] == "A"
    normales = client.get("/producto/?is_especial=false").get_json()
    assert normales["total"] == 1 and normales["data"][0]["clave"] == "B"


def test_producto_update_coerces_unidad(client):
    oid = client.post("/producto/", json=_producto()).get_json()["oid"]
    resp = client.put(f"/producto/{oid}", json={"unidadMedida": "KILOGRAMO"})
    assert resp.status_code == 200 and resp.get_json()["unidadMedida"] == "KILOGRAMO"


def test_producto_messages(client):
    assert client.get("/producto/nope").get_json() == {"errors": ["Producto no encontrado"]}
    oid = client.post("/producto/", json=_producto()).get_json()["oid"]
    assert client.delete(f"/producto/{oid}").get_json() == {"message": "Producto eliminado exitosamente"}
