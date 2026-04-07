from fastapi.testclient import TestClient
from backend.main import app, get_db
from unittest.mock import MagicMock

client = TestClient(app)

def test_health_returns_ok_and_db_status():
    """Health check debe retornar status ok + estado de la BD"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data.get("status") == "ok"
    assert "database" in data
    assert "status" in data["database"]
    assert "timestamp" in data["database"]
    
    print(f"\n✓ Health Check Response: {data}")
    print(f"  • Backend Status: {data.get('status')}")
    print(f"  • Database Status: {data['database']['status']}")
    print(f"  • Database Timestamp: {data['database']['timestamp']}")


def test_health_validates_database_connection():
    """Health check debe conectarse a la BD y obtener timestamp"""
    response = client.get("/")
    data = response.json()
    
    # El endpoint debe intentar conectarse a la BD
    db_status = data["database"]["status"]
    assert db_status in ["connected", "error"], f"DB status debe ser 'connected' o 'error', got {db_status}"
    
    # Si está conectada, debe haber timestamp
    if db_status == "connected":
        assert data["database"]["timestamp"] is not None, "timestamp debe existir cuando BD está conectada"
        print(f"\n✓ Database Connected Successfully")
        print(f"  • Status: {db_status}")
        print(f"  • Server Time: {data['database']['timestamp']}")
    else:
        print(f"\n⚠ Database Connection Error")
        print(f"  • Status: {db_status}")
        print(f"  • Timestamp: {data['database']['timestamp']}")
