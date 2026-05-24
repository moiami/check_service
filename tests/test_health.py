from fastapi.testclient import TestClient

from fastapi import FastAPI

from src.api.v1.health_router import router as health_router

app = FastAPI()
app.include_router(health_router)


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
