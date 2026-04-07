import io
import hashlib
from fastapi.testclient import TestClient
from backend.main import app, get_db
from backend import models
from PIL import Image
from unittest.mock import patch

client = TestClient(app)

def get_pdf_sha256_hash(pdf_bytes: bytes) -> str:
    """Helper to calculate SHA256 hash of PDF"""
    return hashlib.sha256(pdf_bytes).hexdigest()

def generate_sha256_hash(data: str) -> str:
    """Helper to generate SHA256 hash of string data"""
    return hashlib.sha256(data.encode()).hexdigest()

def create_test_image() -> bytes:
    """Crear una imagen PNG pequeña de prueba"""
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 50), color=(100, 150, 200))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

class MockQuery:
    def __init__(self, items):
        self._items = items
    
    def filter(self, *args, **kwargs):
        return self
    
    def first(self):
        return self._items[0] if self._items else None

class DummyDB:
    def __init__(self, existing_hash=None, hash_final=None):
        self.existing_hash = existing_hash
        self.existing_hash_final = hash_final
        self._stored_items = []
        self._verificaciones = []
    
    def query(self, model):
        if model == models.Documento:
            if self.existing_hash:
                doc = models.Documento()
                doc.id = 1
                doc.hash_pdf = self.existing_hash
                doc.nombre = "test.pdf"
                doc.imagen_id = 1
                doc.hash_final = self.existing_hash_final
                return MockQuery([doc])
            return MockQuery([])
        elif model == models.Verificacion:
            return MockQuery(self._verificaciones)
        return MockQuery([])
    
    def add(self, obj):
        self._stored_items.append(obj)
        if isinstance(obj, models.Verificacion):
            self._verificaciones.append(obj)
    
    def refresh(self, obj):
        pass
    
    def commit(self):
        pass


def test_verificar_pdf_valid_with_salt():
    """Test que el PDF verificado con imagen coincida correctamente"""
    from unittest.mock import patch
    
    pdf_bytes = b"dummy pdf content"
    pdf_hash = get_pdf_sha256_hash(pdf_bytes)
    imagen_bytes = create_test_image()
    
    # Simular que el salt extraído es conocido
    mock_salt = "a1b2c3d4e5f6g7h8"
    hash_final = generate_sha256_hash(pdf_hash + mock_salt)

    # Mock get_deterministic_salt para retornar salt conocido
    with patch("backend.main.get_deterministic_salt", return_value=mock_salt):
        # Caso válido: PDF que existe con hash_final correcto
        app.dependency_overrides[get_db] = lambda: DummyDB(
            existing_hash=pdf_hash,
            hash_final=hash_final
        )
        
        files = {
            "pdf": ("a.pdf", io.BytesIO(pdf_bytes), "application/pdf"),
            "imagen": ("img.png", io.BytesIO(imagen_bytes), "image/png")
        }
        response = client.post("/verificar_pdf/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("valido") is True
        assert data.get("hash") == pdf_hash
        
        print(f"\n✓ POST /verificar_pdf/ - Document Valid (Found & Hash Matches)")
        print(f"  • Status: Valid ✓")
        print(f"  • PDF Hash: {pdf_hash[:16]}...")
        print(f"  • Salt: {mock_salt[:20]}...")
        print(f"  • Hash Final: {hash_final[:16]}...")


def test_verificar_pdf_invalid_document_not_found():
    """Test que PDF no existe en BD"""
    pdf_bytes = b"other pdf content"
    imagen_bytes = create_test_image()
    
    # Caso inválido: PDF no existe
    app.dependency_overrides[get_db] = lambda: DummyDB(existing_hash=None)
    files = {
        "pdf": ("b.pdf", io.BytesIO(pdf_bytes), "application/pdf"),
        "imagen": ("img.png", io.BytesIO(imagen_bytes), "image/png")
    }
    response = client.post("/verificar_pdf/", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data.get("valido") is False
    assert data.get("hash_final_guardado") is None
    
    print(f"\n✓ POST /verificar_pdf/ - Document Not Found")
    print(f"  • Status: Invalid ✗ (Documento no registrado)")
    print(f"  • PDF Hash: {data.get('hash')[:16]}...")
    print(f"  • Document Found: No")


def test_verificar_pdf_invalid_hash_mismatch():
    """Test que hash_final no coincide (documento alterado)"""
    from unittest.mock import patch
    
    pdf_bytes = b"dummy pdf content"
    pdf_hash = get_pdf_sha256_hash(pdf_bytes)
    imagen_bytes = create_test_image()
    mock_salt = "a1b2c3d4e5f6g7h8"
    wrong_hash_final = "wrong_hash_value"  # Hash incorrecto deliberadamente

    # Mock get_deterministic_salt para retornar salt conocido
    with patch("backend.main.get_deterministic_salt", return_value=mock_salt):
        # Caso inválido: hash_final no coincide
        app.dependency_overrides[get_db] = lambda: DummyDB(
            existing_hash=pdf_hash,
            hash_final=wrong_hash_final
        )
        files = {
            "pdf": ("c.pdf", io.BytesIO(pdf_bytes), "application/pdf"),
            "imagen": ("img.png", io.BytesIO(imagen_bytes), "image/png")
        }
        response = client.post("/verificar_pdf/", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("valido") is False

        print(f"\n✓ POST /verificar_pdf/ - Document Altered (Hash Mismatch)")
        print(f"  • Status: Invalid ✗ (Documento alterado)")
        print(f"  • Document Found: Yes")
        print(f"  • Hash Final Stored: {wrong_hash_final}")
        print(f"  • Expected Hash: (no coincide)")

        app.dependency_overrides.clear()
