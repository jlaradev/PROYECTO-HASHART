import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app, get_db
from backend import models

client = TestClient(app)

class MockQuery:
    def __init__(self, items):
        self._items = items
    
    def filter(self, *args, **kwargs):
        return self
    
    def first(self):
        return self._items[0] if self._items else None
    
    def offset(self, skip):
        return self
    
    def limit(self, limit):
        return self
    
    def all(self):
        return self._items

class DummyDB:
    def __init__(self):
        self._stored_items = []
        self._imagenes = []
        # Create mock imagen
        img = models.Imagen()
        img.id = 1
        img.nombre = "img1"
        img.url = "https://test.com/img1.png"
        img.salt = None
        self._imagenes.append(img)
    
    def query(self, model):
        if model == models.Imagen:
            return MockQuery(self._imagenes)
        return MockQuery([])
    
    def add(self, obj):
        self._stored_items.append(obj)
    
    def refresh(self, obj):
        pass
    
    def commit(self):
        pass


def test_registrar_pdf_returns_pdf():
    # Mock requests.get para que no intente descargar imágenes reales
    mock_response = MagicMock()
    mock_response.content = b"fake image bytes"
    mock_response.raise_for_status = MagicMock()
    
    with patch("backend.main.requests.get", return_value=mock_response):
        app.dependency_overrides[get_db] = lambda: DummyDB()
        pdf_bytes = b"%PDF-1.4 test"
        files = {"pdf": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

        response = client.post("/registrar_pdf/", files=files)

        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        app.dependency_overrides.clear()
