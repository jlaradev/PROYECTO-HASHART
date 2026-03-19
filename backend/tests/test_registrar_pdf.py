import io
from fastapi.testclient import TestClient
from backend.main import app, get_db

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
        q = str(query).lower()
        if "from imagenes" in q:
            # Leer imagen real subida por el usuario
            try:
                with open("backend/tests/fixtures/sample_image.png", "rb") as imgf:
                    png = imgf.read()
                return Res([("img1", png)])
            except Exception:
                # fallback: return empty list so caller vea que no hay imagenes
                return Res([])
        return Res([])
    def commit(self):
        pass


def test_registrar_pdf_returns_pdf():
    app.dependency_overrides[get_db] = lambda: DummyDB()
    pdf_bytes = b"%PDF-1.4 test"
    files = {"pdf": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    # Logs para depuración
    # Ver qué devuelve DummyDB para la imagen asociada
    db = app.dependency_overrides[get_db]()
    res = db.execute("SELECT nombre, datos FROM imagenes")
    rows = res.fetchall()
    print("TEST LOG: imagenes_rows=", rows)
    if rows:
        nombre, datos = rows[0]
        print("TEST LOG: imagen_bytes_len=", len(datos))

    response = client.post("/registrar_pdf/", files=files)
    print("TEST LOG: status_code=", response.status_code)
    try:
        print("TEST LOG: json=", response.json())
    except Exception:
        print("TEST LOG: text=", response.text[:1000])
    print("TEST LOG: headers=", dict(response.headers))
    print("TEST LOG: content_len=", len(response.content))

    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    app.dependency_overrides.clear()
