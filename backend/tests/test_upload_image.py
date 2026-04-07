import io
from fastapi.testclient import TestClient
from backend.main import app, get_db
from PIL import Image
import uuid

client = TestClient(app)


class DummyDB:
    def execute(self, query, params=None):
        class Res:
            def __init__(self, rows):
                self._rows = rows
            def fetchall(self):
                return self._rows
            def fetchone(self):
                return self._rows[0] if self._rows else None
        return Res([])
    def commit(self):
        pass


def test_upload_image():
    """Test del endpoint POST /upload-image."""
    # Generar una imagen pequeña de prueba
    buf = io.BytesIO()
    img = Image.new("RGB", (50, 50), color=(100, 150, 200))
    img.save(buf, format="PNG")
    buf.seek(0)
    
    # Usar nombre único para evitar violación de constraint UNIQUE
    unique_filename = f"test_upload_{uuid.uuid4().hex[:8]}.png"
    
    files = {
        "image": (unique_filename, buf, "image/png"),
    }
    
    response = client.post("/upload-image", files=files)
    
    # Si Cloudinary está configurado, debería retornar 200 y una URL
    if response.status_code == 200:
        json_response = response.json()
        assert "id" in json_response
        assert "nombre" in json_response
        assert "url" in json_response
        assert json_response["url"].startswith("https://")
        assert "cloudinary" in json_response["url"]
        
        print(f"\n✓ POST /upload-image Successful")
        print(f"  • Status Code: {response.status_code}")
        print(f"  • Filename: {json_response['nombre']}")
        print(f"  • Image ID: {json_response['id']}")
        print(f"  • URL: {json_response['url']}")
    else:
        # Si falla, revisar que sea por credenciales de Cloudinary
        print(f"\n✗ POST /upload-image Failed")
        print(f"  • Status: {response.status_code}")
        print(f"  • Response: {response.json()}")
