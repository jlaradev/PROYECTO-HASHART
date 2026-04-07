import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app, get_db
from backend import models
import zipfile

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
        self._documentos = []
        # Create mock imagen
        img = models.Imagen()
        img.id = 1
        img.nombre = "img1"
        img.url = "https://test.com/img1.png"
        self._imagenes.append(img)
    
    def query(self, model):
        if model == models.Imagen:
            return MockQuery(self._imagenes)
        elif model == models.Documento:
            return MockQuery(self._documentos)
        return MockQuery([])
    
    def add(self, obj):
        self._stored_items.append(obj)
        if isinstance(obj, models.Documento):
            self._documentos.append(obj)
    
    def refresh(self, obj):
        pass
    
    def commit(self):
        pass


def test_registrar_pdf_returns_pdf():
    # Leer imagen real de fixtures
    fixture_image_path = "backend/tests/fixtures/sample_image.png"
    with open(fixture_image_path, "rb") as f:
        real_image_bytes = f.read()
    
    # Mock requests.get para retornar la imagen real de fixtures
    mock_response = MagicMock()
    mock_response.content = real_image_bytes
    mock_response.raise_for_status = MagicMock()
    
    with patch("backend.main.requests.get", return_value=mock_response):
        app.dependency_overrides[get_db] = lambda: DummyDB()
        
        # Usar PDF de fixtures si existe, si no usar uno válido
        fixture_pdf_path = "backend/tests/fixtures/sample.pdf"
        try:
            with open(fixture_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            pdf_source = "sample.pdf (fixtures)"
        except FileNotFoundError:
            # Fallback a un PDF mínimo válido
            pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< >>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<< /Size 1 >>\nstartxref\n0\n%%EOF"
            pdf_source = "PDF mínimo (fallback)"
        
        files = {"pdf": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

        response = client.post("/registrar_pdf/", files=files)

        assert response.status_code == 200
        assert "zip" in response.headers.get("content-type", "")
        
        # Verificar que el ZIP contiene PDF + imagen
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            # Debe contener archivo PDF y archivo imagen
            has_pdf = any(f.endswith('.pdf') for f in file_list)
            has_image = any(f.endswith(('.png', '.jpg', '.jpeg')) for f in file_list)
            assert has_pdf, f"ZIP no contiene PDF. Archivos: {file_list}"
            assert has_image, f"ZIP no contiene imagen. Archivos: {file_list}"
        
        print(f"\n✓ POST /registrar_pdf/ Successful")
        print(f"  • Status Code: {response.status_code}")
        print(f"  • Content-Type: {response.headers.get('content-type')}")
        print(f"  • PDF Source: {pdf_source}")
        print(f"  • Image Source: sample_image.png (fixtures) - {len(real_image_bytes)} bytes")
        print(f"  • ZIP Files: {zip_file.namelist()}")
        print(f"  • Data Size: {len(response.content)} bytes")
        
        app.dependency_overrides.clear()
