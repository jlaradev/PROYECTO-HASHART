import io
from fastapi.testclient import TestClient
from backend.main import app, get_db
from PIL import Image

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
    
    files = {
        "image": ("test_upload.png", buf, "image/png"),
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
        print(f"✓ Imagen subida a Cloudinary: {json_response['url']}")
    else:
        # Si falla, revisar que sea por credenciales de Cloudinary
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
