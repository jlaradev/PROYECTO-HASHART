from fastapi.testclient import TestClient
from backend.main import app, get_db
import backend.routes.files as files_mod

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

def test_records_returns_list():
    # Patch get_all_records to avoid DB
    files_mod.crud.get_all_records = lambda db: [{"id": 1, "nombre": "a.pdf"}]
    app.dependency_overrides[get_db] = lambda: DummyDB()

    response = client.get("/records")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    app.dependency_overrides.clear()
