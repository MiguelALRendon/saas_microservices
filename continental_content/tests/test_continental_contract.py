"""Contract tests de continental_content tras migrar a galurensoft_core (convención CONTINENTAL)."""


def _obra(client, nombre="One Piece"):
    return client.post("/obra/", json={"nombre": nombre, "descripcion": "d", "orden": 1})


# ── ContinentalBase: convención id/Integer/url_busqueda + slug + soft-delete ─────
def test_obra_create_convention_and_slug(client):
    resp = _obra(client)
    assert resp.status_code == 201
    body = resp.get_json()
    # convención CONTINENTAL
    assert "id" in body and len(body["id"]) == 36
    assert "created_at" in body and "updated_at" in body
    assert body["estatus"] == 1                       # Integer, no Enum
    assert body["url_busqueda"] == "one-piece"        # slug generado de nombre
    assert "oid" not in body and "createdAt" not in body


def test_obra_slug_uniqueness(client):
    a = _obra(client).get_json()["url_busqueda"]
    b = _obra(client).get_json()["url_busqueda"]    # mismo nombre
    assert a == "one-piece" and b == "one-piece-1"  # único


def test_obra_list_no_has_more(client):
    _obra(client)
    body = client.get("/obra/").get_json()
    assert "has_more" not in body
    assert set(body) == {"data", "total", "page", "per_page", "pages"}


def test_obra_soft_delete_estatus_minus1(client):
    oid = _obra(client).get_json()["id"]
    resp = client.delete(f"/obra/{oid}")
    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Obra desactivada exitosamente"}
    # soft-delete: ya no visible (estatus != 1)
    assert client.get(f"/obra/{oid}").status_code == 404
    assert client.get(f"/obra/{oid}").get_json() == {"errors": ["Obra no encontrada"]}


# ── capitulo: SEO + FK obra existence ────────────────────────────────────────
def test_capitulo_requires_obra(client):
    resp = client.post("/capitulo/", json={"titulo": "Cap 1", "numero_capitulo": 1, "obra_id": "ghost"})
    assert resp.status_code == 400
    assert resp.get_json() == {"errors": ["La obra especificada no existe"]}


def test_capitulo_create_with_seo(client):
    oid = _obra(client).get_json()["id"]
    resp = client.post("/capitulo/", json={
        "titulo": "Romance Dawn", "numero_capitulo": 1, "obra_id": oid,
        "titulo_seo": "SEO", "no_index": True,
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["titulo_seo"] == "SEO"
    assert body["no_index"] is True
    assert body["url_busqueda"] == "romance-dawn"
    assert body["estatus"] == 1


# ── arco: filtro booleano es_subarco ─────────────────────────────────────────
def test_arco_bool_filter(client):
    client.post("/arco/", json={"nombre": "Saga Mayor", "es_subarco": False})
    client.post("/arco/", json={"nombre": "Sub Saga", "es_subarco": True})
    subs = client.get("/arco/?es_subarco=true").get_json()
    assert subs["total"] == 1 and subs["data"][0]["nombre"] == "Sub Saga"


# ── nota: ConceptBase (sin estatus/url_busqueda) + FK obra + HARD delete ─────
def test_nota_concept_base_and_hard_delete(client):
    oid = _obra(client).get_json()["id"]
    resp = client.post("/nota/", json={"titulo_nota": "N1", "texto_nota": "t", "fk_obra": oid})
    assert resp.status_code == 201
    body = resp.get_json()
    assert "estatus" not in body and "url_busqueda" not in body   # ConceptBase
    assert "id" in body and "created_at" in body
    nid = body["id"]
    # borrado físico
    d = client.delete(f"/nota/{nid}")
    assert d.status_code == 200 and d.get_json() == {"message": "Nota eliminada exitosamente"}
    assert client.get(f"/nota/{nid}").status_code == 404


def test_nota_requires_obra(client):
    resp = client.post("/nota/", json={"titulo_nota": "N", "texto_nota": "t", "fk_obra": "ghost"})
    assert resp.status_code == 400
    assert resp.get_json() == {"errors": ["La obra especificada no existe"]}


# ── fecha: ConceptBase + parseo de fecha + HARD delete ───────────────────────
def test_fecha_parse_and_bad_format(client):
    ok = client.post("/fecha/", json={"fecha": "2024-12-25", "evento": "Navidad"})
    assert ok.status_code == 201
    assert ok.get_json()["fecha"] == "2024-12-25"
    bad = client.post("/fecha/", json={"fecha": "25/12/2024", "evento": "x"})
    assert bad.status_code == 400
    assert bad.get_json() == {"errors": ["fecha debe tener formato YYYY-MM-DD"]}


def test_fecha_hard_delete(client):
    fid = client.post("/fecha/", json={"fecha": "2024-01-01", "evento": "AñoNuevo"}).get_json()["id"]
    assert client.delete(f"/fecha/{fid}").get_json() == {"message": "Fecha eliminada exitosamente"}
    assert client.get(f"/fecha/{fid}").status_code == 404
