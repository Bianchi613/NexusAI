"""Testes das rotas publicas do modulo de clima."""

from contextlib import contextmanager
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.weather.weather_repository as weather_repository_module
import backend.weather.weather_service as weather_service
from backend.main import app
from Engine.app.models import Base


def _configure_in_memory_weather_db(monkeypatch):
    """Redireciona o repositorio de clima para SQLite em memoria."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    @contextmanager
    def fake_get_session():
        with SessionLocal() as session:
            yield session

    monkeypatch.setattr(weather_repository_module, "get_session", fake_get_session)
    return SessionLocal


def test_weather_overview_route_returns_forecasts_and_alerts(monkeypatch) -> None:
    """A rota principal deve combinar previsao cacheavel e alertas ativos."""
    _configure_in_memory_weather_db(monkeypatch)

    monkeypatch.setattr(
        weather_service,
        "_get_monitored_locations",
        lambda: [
            {
                "location_key": "sao-paulo-sp",
                "city": "Sao Paulo",
                "state_code": "SP",
                "state_name": "Sao Paulo",
            },
            {
                "location_key": "rio-de-janeiro-rj",
                "city": "Rio de Janeiro",
                "state_code": "RJ",
                "state_name": "Rio de Janeiro",
            },
        ],
    )

    def fake_forecast(*, city: str, state_code: str) -> dict:
        daily = [
            {
                "date": "2026-04-22",
                "condition_code": "pn",
                "condition": "Parcialmente nublado",
                "min_temp_c": 19,
                "max_temp_c": 28 if state_code == "SP" else 31,
                "uv_index": 6.0,
                "rain_probability": None,
            },
            {
                "date": "2026-04-23",
                "condition_code": "c",
                "condition": "Chuva",
                "min_temp_c": 20,
                "max_temp_c": 26 if state_code == "SP" else 29,
                "uv_index": 5.0,
                "rain_probability": None,
            },
        ]
        return {
            "city": city,
            "state_code": state_code,
            "source_name": "CPTEC/INPE",
            "source_url": f"https://example.com/{state_code.lower()}",
            "updated_at": datetime(2026, 4, 21, 15, 0, tzinfo=timezone.utc),
            "daily": daily,
            "extra_payload": {"provider": "fake"},
        }

    monkeypatch.setattr(weather_service.cptec_client, "fetch_weekly_forecast", fake_forecast)
    monkeypatch.setattr(
        weather_service.openmeteo_client,
        "fetch_weekly_forecast",
        lambda **_: (_ for _ in ()).throw(RuntimeError("nao deveria ser usado")),
    )
    monkeypatch.setattr(
        weather_service.inmet_client,
        "fetch_alerts",
        lambda: [
            {
                "external_id": "alerta-1",
                "title": "Aviso de chuva intensa",
                "summary": "Chuva intensa em municipios do interior.",
                "severity": "perigo",
                "status": "ativo",
                "area": "Interior de SP",
                "areas": ["Interior de SP"],
                "source_url": "https://example.com/alerta-1",
                "published_at": datetime(2026, 4, 21, 14, 0, tzinfo=timezone.utc),
                "effective_at": datetime(2026, 4, 21, 14, 0, tzinfo=timezone.utc),
                "expires_at": datetime(2026, 4, 22, 8, 0, tzinfo=timezone.utc),
                "is_active": True,
                "payload": {},
                "collected_at": datetime(2026, 4, 21, 14, 5, tzinfo=timezone.utc),
            }
        ],
    )

    client = TestClient(app)

    response = client.get("/api/v1/weather/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["location_count"] == 2
    assert payload["summary"]["active_alert_count"] == 1
    assert payload["summary"]["severe_alert_count"] == 1
    assert len(payload["locations"]) == 2
    assert payload["locations"][0]["source_name"] == "CPTEC/INPE"
    assert payload["locations"][0]["daily"][0]["condition"] == "Parcialmente nublado"
    assert payload["alerts"][0]["title"] == "Aviso de chuva intensa"
    assert payload["alerts"][0]["severity"] == "perigo"


def test_weather_overview_route_uses_cached_forecast_when_provider_fails(monkeypatch) -> None:
    """Uma previsao ja persistida deve continuar visivel mesmo se a fonte cair depois."""
    _configure_in_memory_weather_db(monkeypatch)

    monkeypatch.setattr(
        weather_service,
        "_get_monitored_locations",
        lambda: [
            {
                "location_key": "curitiba-pr",
                "city": "Curitiba",
                "state_code": "PR",
                "state_name": "Parana",
            }
        ],
    )

    monkeypatch.setattr(
        weather_service.cptec_client,
        "fetch_weekly_forecast",
        lambda **_: {
            "city": "Curitiba",
            "state_code": "PR",
            "source_name": "CPTEC/INPE",
            "source_url": "https://example.com/pr",
            "updated_at": datetime(2026, 4, 21, 15, 0, tzinfo=timezone.utc),
            "daily": [
                {
                    "date": "2026-04-22",
                    "condition_code": "n",
                    "condition": "Nublado",
                    "min_temp_c": 14,
                    "max_temp_c": 22,
                    "uv_index": 4.0,
                    "rain_probability": None,
                }
            ],
            "extra_payload": {},
        },
    )
    monkeypatch.setattr(weather_service.inmet_client, "fetch_alerts", lambda: [])
    monkeypatch.setattr(
        weather_service.openmeteo_client,
        "fetch_weekly_forecast",
        lambda **_: (_ for _ in ()).throw(RuntimeError("fallback offline")),
    )

    client = TestClient(app)
    first_response = client.get("/api/v1/weather/overview")

    assert first_response.status_code == 200
    assert first_response.json()["locations"][0]["city"] == "Curitiba"

    monkeypatch.setattr(
        weather_service.cptec_client,
        "fetch_weekly_forecast",
        lambda **_: (_ for _ in ()).throw(RuntimeError("fonte offline")),
    )

    second_response = client.get("/api/v1/weather/overview")

    assert second_response.status_code == 200
    payload = second_response.json()
    assert payload["locations"][0]["city"] == "Curitiba"
    assert payload["locations"][0]["daily"][0]["condition"] == "Nublado"


def test_weather_overview_stops_retrying_all_locations_when_provider_is_down(monkeypatch) -> None:
    """Quando a fonte de previsao cai, a API nao deve esperar timeout para todas as capitais."""
    _configure_in_memory_weather_db(monkeypatch)

    monkeypatch.setattr(
        weather_service,
        "_get_monitored_locations",
        lambda: [
            {
                "location_key": "sao-paulo-sp",
                "city": "Sao Paulo",
                "state_code": "SP",
                "state_name": "Sao Paulo",
            },
            {
                "location_key": "rio-de-janeiro-rj",
                "city": "Rio de Janeiro",
                "state_code": "RJ",
                "state_name": "Rio de Janeiro",
            },
            {
                "location_key": "belo-horizonte-mg",
                "city": "Belo Horizonte",
                "state_code": "MG",
                "state_name": "Minas Gerais",
            },
        ],
    )

    calls = {"count": 0}

    def failing_forecast(**_kwargs):
        calls["count"] += 1
        raise RuntimeError("fonte indisponivel")

    monkeypatch.setattr(weather_service.cptec_client, "fetch_weekly_forecast", failing_forecast)
    monkeypatch.setattr(
        weather_service.openmeteo_client,
        "fetch_weekly_forecast",
        lambda **_: (_ for _ in ()).throw(RuntimeError("fallback offline")),
    )
    monkeypatch.setattr(weather_service.inmet_client, "fetch_alerts", lambda: [])

    client = TestClient(app)
    response = client.get("/api/v1/weather/overview")

    assert response.status_code == 200
    assert response.json()["locations"] == []
    assert calls["count"] == 1


def test_weather_overview_uses_openmeteo_when_cptec_fails(monkeypatch) -> None:
    """Quando o CPTEC falhar, o fallback sem chave deve preencher as temperaturas."""
    _configure_in_memory_weather_db(monkeypatch)

    monkeypatch.setattr(
        weather_service,
        "_get_monitored_locations",
        lambda: [
            {
                "location_key": "rio-de-janeiro-rj",
                "city": "Rio de Janeiro",
                "state_code": "RJ",
                "state_name": "Rio de Janeiro",
            }
        ],
    )

    monkeypatch.setattr(
        weather_service.cptec_client,
        "fetch_weekly_forecast",
        lambda **_: (_ for _ in ()).throw(RuntimeError("cptec offline")),
    )
    monkeypatch.setattr(
        weather_service.openmeteo_client,
        "fetch_weekly_forecast",
        lambda **_: {
            "city": "Rio de Janeiro",
            "state_code": "RJ",
            "source_name": "Open-Meteo",
            "source_url": "https://api.open-meteo.com/v1/forecast",
            "updated_at": datetime(2026, 4, 21, 15, 0, tzinfo=timezone.utc),
            "daily": [
                {
                    "date": "2026-04-22",
                    "condition_code": "2",
                    "condition": "Parcialmente nublado",
                    "min_temp_c": 21,
                    "max_temp_c": 30,
                    "uv_index": None,
                    "rain_probability": 15,
                }
            ],
            "extra_payload": {},
        },
    )
    monkeypatch.setattr(weather_service.inmet_client, "fetch_alerts", lambda: [])

    client = TestClient(app)
    response = client.get("/api/v1/weather/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["location_count"] == 1
    assert payload["locations"][0]["source_name"] == "Open-Meteo"
    assert payload["locations"][0]["daily"][0]["max_temp_c"] == 30
