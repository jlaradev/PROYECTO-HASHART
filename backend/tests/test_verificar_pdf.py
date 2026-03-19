import io
from fastapi.testclient import TestClient
from backend.main import app, get_db
from backend.utils import generate_pdf_hash

client = TestClient(app)

class DummyDB:
    def __init__(self, existing_hash=None):
        self.existing_hash = existing_hash
    def execute(self, query, params=None):
        class Res:
            def __init__(self, rows):
                self._rows = rows
            def fetchone(self):
                return self._rows[0] if self._rows else None
            def fetchall(self):
                return self._rows
        q = str(query).lower()
        if "select id from documentos" in q:
            if params and params.get("hash_pdf") == self.existing_hash:
                return Res([(1,)])
            return Res([])
        return Res([])
    def commit(self):
        pass


def test_verificar_pdf_valid_and_invalid():
    pdf_bytes = b"dummy pdf"
    h = generate_pdf_hash(pdf_bytes)

    # valid case
    app.dependency_overrides[get_db] = lambda: DummyDB(existing_hash=h)
    response = client.post("/verificar_pdf/", files={"pdf": ("a.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
    assert response.status_code == 200
    assert response.json().get("valido") is True

    # invalid case
    app.dependency_overrides[get_db] = lambda: DummyDB(existing_hash=None)
    response2 = client.post("/verificar_pdf/", files={"pdf": ("b.pdf", io.BytesIO(b"other"), "application/pdf")})
    assert response2.status_code == 200
    assert response2.json().get("valido") is False

    app.dependency_overrides.clear()
