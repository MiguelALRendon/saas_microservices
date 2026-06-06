"""Test de contrato del recurso `sucursal` tras migrar a galurensoft_core.

Verifica que los 8 endpoints producen el JSON esperado (status + claves + mensajes
específicos de entidad), preservando el contrato observable por el frontend.
"""


def _payload(clave="S1", nombre="Centro"):
    return {
        "clave": clave,
        "nombre": nombre,
        "folio": "F-001",
        "direccion": "Av. Siempre Viva 742",
        "telefono": "555-1234",
        "fkEmpresa": "empresa-oid-x",
    }


def _create(client, **over):
    data = _payload(**over)
    return client.post("/sucursal/", json=data)


def test_trust_middleware_blocks_without_secret(client):
    # Petición sin el header de confianza -> 403 (el TrustedClient inyecta el header;
    # aquí usamos el cliente Flask crudo para comprobar el bloqueo).
    from app import create_app

    raw = create_app().test_client()
    resp = raw.get("/sucursal/")
    assert resp.status_code == 403
    assert resp.get_json() == {"errors": ["Acceso no autorizado"]}


def test_create_sucursal(client):
    resp = _create(client)
    assert resp.status_code == 201
    body = resp.get_json()
    # El conjunto de claves debe coincidir exactamente (Flask jsonify ordena alfabéticamente
    # tanto en el código original como en el migrado -> el orden de bytes se preserva).
    assert set(body.keys()) == {
        "oid", "createdAt", "updatedAt", "creado_por", "editado_por", "estatus",
        "clave", "nombre", "folio", "direccion", "telefono", "fkEmpresa", "empresa",
    }
    assert body["estatus"] == "ACTIVO"
    assert body["clave"] == "S1"
    assert body["empresa"] is None
    assert len(body["oid"]) == 36


def test_create_validation_messages(client):
    resp = client.post("/sucursal/", json={"clave": "X"})
    assert resp.status_code == 400
    assert resp.get_json() == {
        "errors": ["nombre es requerido", "folio es requerido",
                   "direccion es requerida", "fkEmpresa es requerido"]
    }


def test_create_duplicate_clave(client):
    _create(client)
    resp = _create(client)
    assert resp.status_code == 400  # contrato original: duplicado -> 400 (no 409)
    assert resp.get_json() == {"errors": ["La clave ya existe"]}


def test_get_detail_includes_empleados_envelope(client):
    oid = _create(client).get_json()["oid"]
    resp = client.get(f"/sucursal/{oid}")
    assert resp.status_code == 200
    body = resp.get_json()
    # serialize_detail añade 'empleados' (servicio branch inalcanzable -> envelope vacío)
    assert "empleados" in body
    assert body["empleados"] == {
        "data": [], "total": 0, "page": 1, "per_page": 25, "pages": 0, "has_more": False
    }


def test_get_not_found_message(client):
    resp = client.get("/sucursal/no-existe")
    assert resp.status_code == 404
    assert resp.get_json() == {"errors": ["Sucursal no encontrada"]}


def test_list_envelope_has_no_has_more(client):
    for i in range(3):
        _create(client, clave=f"S{i}", nombre="Centro" if i % 2 == 0 else "Norte")
    resp = client.get("/sucursal/?page=1&per_page=10")
    body = resp.get_json()
    assert set(body.keys()) == {"data", "total", "page", "per_page", "pages"}
    assert "has_more" not in body
    assert body["total"] == 3


def test_list_ilike_filter(client):
    _create(client, clave="A", nombre="Centro Norte")
    _create(client, clave="B", nombre="Sur")
    body = client.get("/sucursal/?nombre=norte").get_json()
    assert body["total"] == 1 and body["data"][0]["clave"] == "A"


def test_update_sucursal(client):
    oid = _create(client).get_json()["oid"]
    resp = client.put(f"/sucursal/{oid}", json={"nombre": "Renombrada", "editado_por": "u1"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["nombre"] == "Renombrada"
    assert body["editado_por"] == "u1"


def test_update_duplicate_clave(client):
    _create(client, clave="A")
    oid_b = _create(client, clave="B").get_json()["oid"]
    resp = client.put(f"/sucursal/{oid_b}", json={"clave": "A"})
    assert resp.get_json() == {"errors": ["La clave ya existe"]}


def test_soft_delete_message_and_hidden(client):
    oid = _create(client).get_json()["oid"]
    resp = client.delete(f"/sucursal/{oid}", json={"editado_por": "u9"})
    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Sucursal eliminada exitosamente"}
    assert client.get(f"/sucursal/{oid}").status_code == 404
    assert client.get("/sucursal/").get_json()["total"] == 0


def test_post_list_by_oids(client):
    a = _create(client, clave="A").get_json()["oid"]
    b = _create(client, clave="B").get_json()["oid"]
    resp = client.post("/sucursal/list", json={"oid_list": [a, b, "missing"]})
    assert resp.status_code == 200
    assert {s["clave"] for s in resp.get_json()} == {"A", "B"}


def test_post_list_requires_oid_list(client):
    assert client.post("/sucursal/list", json={}).get_json() == {"errors": ["oid_list es requerido"]}


def test_create_many_specific_not_a_list_message(client):
    resp = client.post("/sucursal/many", json={"not": "a list"})
    assert resp.status_code == 400
    assert resp.get_json() == {"errors": ["Se esperaba una lista de sucursales"]}


def test_update_many_mixed(client):
    oid = _create(client, clave="U1").get_json()["oid"]
    payload = [
        {"oid": oid, "nombre": "actualizada"},
        {"nombre": "sin oid"},
        {"oid": "missing", "nombre": "y"},
    ]
    body = client.put("/sucursal/many", json=payload).get_json()
    assert body["updated"] == 1
    errors_by_index = {e["index"]: e["errors"] for e in body["errors"]}
    assert set(errors_by_index) == {1, 2}
    assert errors_by_index[2] == ["Sucursal no encontrada"]
