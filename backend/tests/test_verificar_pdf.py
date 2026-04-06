import io
from fastapi.testclient import TestClient
from backend.main import app, get_db
from backend.utils import generate_pdf_hash
from backend import models

client = TestClient(app)

class MockQuery:
    def __init__(self, items):
        self._items = items
    
    def filter(self, *args, **kwargs):
        # For mock purposes, assume filtering by hash_pdf
        return self
    
    def first(self):
        return self._items[0] if self._items else None

class DummyDB:
    def __init__(self, existing_hash=None):
        self.existing_hash = existing_hash
        self._stored_items = []
    
    def query(self, model):
        if model == models.Documento:
            # Return matching documento by hash if it exists
            if self.existing_hash:
                doc = models.Documento()
                doc.id = 1
                doc.hash_pdf = self.existing_hash
                doc.nombre = "test.pdf"
                doc.imagen_asociada = "img1"
                return MockQuery([doc])
            return MockQuery([])
        return MockQuery([])
    
    def add(self, obj):
        self._stored_items.append(obj)
    
    def refresh(self, obj):
        pass
    
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
