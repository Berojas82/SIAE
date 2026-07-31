import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ONLINE"
    assert "artifacts_loaded" in json_data

def test_predict_endpoint_valid_payload():
    payload = {
        "sector": "Tecnología",
        "tamano_empresa": "Micro",
        "porcentaje_procesos_documentados": 0.05,
        "presupuesto_anual_tecnología": 3000000.0,
        "respuesta_texto": "El trabajo es muy empírico, no hay documentación."
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] in ["SUCCESS", "MOCK_RESPONSE"]
    assert json_data["nivel_madurez"] in ["Inicial", "En Desarrollo", "Definido", "Optimizado"]
    assert 0.0 <= json_data["confidence_score"] <= 1.0
    assert "recomendacion_principal" in json_data
