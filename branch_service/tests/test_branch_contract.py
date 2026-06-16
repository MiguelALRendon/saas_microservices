"""Contract tests de branch_service tras migrar a galurensoft_core."""


def _cargo(client, clave="C1"):
    return client.post("/cargo/", json={"clave": clave, "nombre": "Gerente", "fkEmpresa": "emp-1"})


def _empleado(client, fkCargo, curp="CURP0001", nombres="Ana"):
    return client.post("/empleado/", json={
        "nombres": nombres, "apellido_paterno": "Pérez", "apellido_materno": "López",
        "curp": curp, "rfc": "RFC1", "fecha_contratacion": "2024-01-15",
        "fkCargo": fkCargo, "fkEmpresa": "emp-1", "fkSistema": "sis-1",
    })


def _turno(client, nombre="Matutino"):
    return client.post("/turno-sucursal/", json={
        "nombre": nombre, "hora_entrada": "08:00:00", "hora_salida": "16:00:00",
        "hora_corte": "15:30:00", "fkEmpresa": "emp-1", "fkSucursal": "suc-1", "fkSistema": "sis-1",
    })


# ── cargo ────────────────────────────────────────────────────────────────────
def test_cargo_create_persists_fkEmpresa(client):
    resp = _cargo(client)
    assert resp.status_code == 201
    assert resp.get_json()["fkEmpresa"] == "emp-1"


def test_cargo_validation_400_and_dup(client):
    assert client.post("/cargo/", json={"clave": "X"}).status_code == 400  # falta nombre/fkEmpresa
    _cargo(client, clave="DUP")
    dup = _cargo(client, clave="DUP")
    assert dup.status_code == 400 and dup.get_json() == {"errors": ["La clave ya existe"]}


def test_cargo_delete_message(client):
    oid = _cargo(client).get_json()["oid"]
    assert client.delete(f"/cargo/{oid}").get_json() == {"message": "Cargo eliminado exitosamente"}


# ── empleado (fecha + cargo existence + CURP) ────────────────────────────────
def test_empleado_create_parses_fecha(client):
    cid = _cargo(client).get_json()["oid"]
    resp = _empleado(client, cid)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["fecha_contratacion"] == "2024-01-15"
    assert body["telefono"] is None  # base_contacto


def test_empleado_requires_existing_cargo(client):
    resp = _empleado(client, "cargo-fantasma")
    assert resp.status_code == 400
    assert resp.get_json() == {"errors": ["El cargo especificado no existe"]}


def test_empleado_curp_unique(client):
    cid = _cargo(client).get_json()["oid"]
    _empleado(client, cid, curp="CURPDUP")
    dup = _empleado(client, cid, curp="CURPDUP", nombres="Otro")
    assert dup.status_code == 400 and dup.get_json() == {"errors": ["El CURP ya está registrado"]}


# ── turno_sucursal (horas) ───────────────────────────────────────────────────
def test_turno_sucursal_parses_horas(client):
    resp = _turno(client)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["hora_entrada"] == "08:00:00"
    assert body["nombre"] == "Matutino"


# ── empleado_sucursal (junction) ─────────────────────────────────────────────
def test_empleado_sucursal_existence_and_unique(client):
    cid = _cargo(client).get_json()["oid"]
    eid = _empleado(client, cid).get_json()["oid"]
    # empleado inexistente
    ghost = client.post("/empleado-sucursal/", json={"fkEmpleado": "ghost", "fkSucursal": "suc-1"})
    assert ghost.status_code == 400 and ghost.get_json() == {"errors": ["El empleado no existe"]}
    # ok + duplicado
    assert client.post("/empleado-sucursal/", json={"fkEmpleado": eid, "fkSucursal": "suc-1"}).status_code == 201
    dup = client.post("/empleado-sucursal/", json={"fkEmpleado": eid, "fkSucursal": "suc-1"})
    assert dup.status_code == 400 and dup.get_json() == {"errors": ["La asignación ya existe"]}


# ── corte_caja (datetime + turno existence) ──────────────────────────────────
def test_corte_caja_create_and_turno_existence(client):
    tid = _turno(client).get_json()["oid"]
    payload = {
        "fecha": "2024-01-15T10:00:00", "monto_inicial": 100.0, "monto_final": 250.5,
        "esperado": 250.5, "diferencia": 0.0, "fkEmpresa": "emp-1", "fkSucursal": "suc-1",
        "fkUsuario": "u-1", "fkTurno": tid, "fkSistema": "sis-1",
    }
    resp = client.post("/corte_caja/", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["monto_final"] == 250.5
    # turno inexistente
    bad = client.post("/corte_caja/", json={**payload, "fkTurno": "ghost"})
    assert bad.status_code == 400 and bad.get_json() == {"errors": ["El turno especificado no existe"]}


# ── turno_empleado (enum + dates + existence + composite unique) ─────────────
def test_turno_empleado_full(client):
    cid = _cargo(client).get_json()["oid"]
    eid = _empleado(client, cid).get_json()["oid"]
    tid = _turno(client).get_json()["oid"]

    base = {"fkTurnoSucursal": tid, "fkEmpleado": eid, "diaSemana": "LUNES", "fechaInicio": "2024-01-01"}
    ok = client.post("/turno-empleado/", json=base)
    assert ok.status_code == 201
    assert ok.get_json()["diaSemana"] == "LUNES"
    assert ok.get_json()["fechaInicio"] == "2024-01-01"

    # diaSemana inválido -> 400 validación
    bad_dia = client.post("/turno-empleado/", json={**base, "diaSemana": "FUNDAY"})
    assert bad_dia.status_code == 400

    # turno inexistente
    assert client.post("/turno-empleado/", json={**base, "fkTurnoSucursal": "ghost"}).get_json() == {
        "errors": ["El turno especificado no existe"]
    }

    # duplicado (misma combinación fecha+día)
    dup = client.post("/turno-empleado/", json=base)
    assert dup.status_code == 400
    assert dup.get_json() == {"errors": ["La asignación ya existe para esa fecha y día"]}
