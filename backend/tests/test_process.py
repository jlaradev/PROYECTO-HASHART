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


def make_png_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def test_process_returns_pdf(tmp_path):
    app.dependency_overrides[get_db] = lambda: DummyDB()
    # Usar PDF de fixtures subido por el usuario
    fixture_path = "backend/tests/fixtures/sample.pdf"
    with open(fixture_path, "rb") as f:
        pdf_bytes = f.read()
    png = make_png_bytes()
    print("TEST LOG: fixture_path=", fixture_path)
    print("TEST LOG: pdf_bytes_len=", len(pdf_bytes))
    print("TEST LOG: image_bytes_len=", len(png))

    files = {
        "pdf": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf"),
        "image": ("img.png", io.BytesIO(png), "image/png"),
    }
    print("TEST LOG: sending files keys=", list(files.keys()))
    response = client.post("/process", files=files)
    print("TEST LOG: status_code=", response.status_code)
    print("TEST LOG: headers=", dict(response.headers))
    try:
        print("TEST LOG: json=", response.json())
    except Exception:
        # print up to 1000 chars of text if not json
        print("TEST LOG: text=", response.text[:1000])
    print("TEST LOG: content_len=", len(response.content))

    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"

    app.dependency_overrides.clear()

