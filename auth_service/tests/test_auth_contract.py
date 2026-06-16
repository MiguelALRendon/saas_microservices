"""Contract tests de auth_service tras migrar a galurensoft_core."""


# ── usuario ──────────────────────────────────────────────────────────────────
def _usuario(u="admin"):
    return {"usuario": u, "contraseña": "S3cr3t!", "fkSistema": "sis-1"}


def test_usuario_create_hashes_and_hides_password(client):
    resp = client.post("/usuario/", json=_usuario())
    assert resp.status_code == 201
    body = resp.get_json()
    assert "contraseña" not in body          # nunca se serializa
    assert body["usuario"] == "admin"
    assert body["estatus"] == "ACTIVO"


def test_usuario_validation_is_422(client):
    resp = client.post("/usuario/", json={"usuario": "x"})  # falta contraseña/fkSistema
    assert resp.status_code == 422


def test_usuario_duplicate_is_400(client):
    client.post("/usuario/", json=_usuario())
    dup = client.post("/usuario/", json=_usuario())
    assert dup.status_code == 400
    assert dup.get_json() == {"errors": ["El usuario ya existe"]}


def test_usuario_not_found_and_delete_message(client):
    assert client.get("/usuario/nope").get_json() == {"errors": ["Usuario no encontrado"]}
    oid = client.post("/usuario/", json=_usuario()).get_json()["oid"]
    assert client.delete(f"/usuario/{oid}").get_json() == {"message": "Usuario eliminado exitosamente"}


# ── login (verify_password con core argon2) ──────────────────────────────────
def test_login_roundtrip(client):
    client.post("/usuario/", json=_usuario(u="jefe"))
    resp = client.post("/auth/login", json={"usuario": "jefe", "contraseña": "S3cr3t!"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["access_token"] and body["refresh_token"]
    assert body["usuario"]["usuario"] == "jefe"
    assert body["roles"] == []


def test_login_wrong_password(client):
    client.post("/usuario/", json=_usuario(u="jefe"))
    resp = client.post("/auth/login", json={"usuario": "jefe", "contraseña": "mala"})
    assert resp.status_code == 401


# ── rol (sin /many, fix fkSistema) ───────────────────────────────────────────
def test_rol_create_persists_fkSistema(client):
    resp = client.post("/rol/", json={"nombre": "Admin", "fkSistema": "sis-1"})
    assert resp.status_code == 201
    assert resp.get_json()["fkSistema"] == "sis-1"


def test_rol_validation_422_and_no_many(client):
    assert client.post("/rol/", json={"nombre": "X"}).status_code == 422  # falta fkSistema
    # POST /rol/many no existe (colisiona con /<oid>) -> 405; GET /rol/many no es ruta -> 404/405
    assert client.post("/rol/many", json=[]).status_code in (404, 405)


def test_rol_duplicate_nombre_400(client):
    client.post("/rol/", json={"nombre": "Admin", "fkSistema": "s"})
    dup = client.post("/rol/", json={"nombre": "Admin", "fkSistema": "s"})
    assert dup.status_code == 400 and dup.get_json() == {"errors": ["El nombre de rol ya existe"]}


# ── permiso (fix fkSistema, validación 422) ──────────────────────────────────
def test_permiso_create_and_dup(client):
    p = {"clave": "P1", "nombre": "Crear", "permiso": "crear", "fkSistema": "s"}
    assert client.post("/permiso/", json=p).status_code == 201
    dup = client.post("/permiso/", json=p)
    assert dup.status_code == 400 and dup.get_json() == {"errors": ["La clave ya existe"]}
    assert client.post("/permiso/", json={"clave": "P2"}).status_code == 422  # validación


# ── permiso_asignado (unicidad compuesta) ────────────────────────────────────
def test_permiso_asignado_composite_unique(client):
    pa = {"fkRol": "r1", "fkPermiso": "p1", "crear": True}
    assert client.post("/permiso_asignado/", json=pa).get_json()["crear"] is True
    dup = client.post("/permiso_asignado/", json=pa)
    assert dup.status_code == 400
    assert dup.get_json() == {"errors": ["El permiso ya está asignado a este rol"]}
    # otro permiso para el mismo rol -> ok
    assert client.post("/permiso_asignado/", json={"fkRol": "r1", "fkPermiso": "p2"}).status_code == 201


# ── usuario_rol (composite, validación 422, sin chequeo de existencia) ───────
def test_usuario_rol_composite_and_422(client):
    assert client.post("/usuario_rol/", json={"fkUsuario": "u1"}).status_code == 422  # falta fkRol
    assert client.post("/usuario_rol/", json={"fkUsuario": "u1", "fkRol": "r1"}).status_code == 201
    dup = client.post("/usuario_rol/", json={"fkUsuario": "u1", "fkRol": "r1"})
    assert dup.status_code == 400
    assert dup.get_json() == {"errors": ["El rol ya está asignado a este usuario"]}


# ── usuario_empleado (existencia de usuario, validación 400, re-add) ─────────
def test_usuario_empleado_requires_existing_usuario(client):
    resp = client.post("/usuario-empleado/", json={"fkUsuario": "ghost", "fkEmpleado": "e1"})
    assert resp.status_code == 400
    assert resp.get_json() == {"errors": ["El usuario no existe"]}


def test_usuario_empleado_assignment_and_duplicate(client):
    uid = client.post("/usuario/", json=_usuario(u="op")).get_json()["oid"]
    a = client.post("/usuario-empleado/", json={"fkUsuario": uid, "fkEmpleado": "e1"})
    assert a.status_code == 201
    # duplicado (visible) -> 400 con el mensaje de junction
    dup = client.post("/usuario-empleado/", json={"fkUsuario": uid, "fkEmpleado": "e1"})
    assert dup.status_code == 400 and dup.get_json() == {"errors": ["La asignación ya existe"]}
    # NOTA: re-crear tras soft-delete lo impide el índice UNIQUE de BD (fkUsuario, fkEmpleado)
    # sin estatus — comportamiento idéntico al original; no se testea aquí.
