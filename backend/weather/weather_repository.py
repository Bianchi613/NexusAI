"""Persistencia do modulo de clima."""

from __future__ import annotations

from datetime import datetime

from Engine.app.db import get_session
from Engine.app.models import WeatherAlert, WeatherForecastSnapshot
from sqlalchemy import select


class WeatherRepository:
    """Consulta e atualiza snapshots de previsao e alertas meteorologicos."""

    def list_forecasts(self) -> list[WeatherForecastSnapshot]:
        """Lista todos os snapshots de previsao ordenados por chave."""
        with get_session() as session:
            statement = select(WeatherForecastSnapshot).order_by(WeatherForecastSnapshot.location_key.asc())
            return list(session.scalars(statement).all())

    def get_forecast_by_location_key(self, location_key: str) -> WeatherForecastSnapshot | None:
        """Busca o snapshot de uma localidade."""
        with get_session() as session:
            statement = select(WeatherForecastSnapshot).where(WeatherForecastSnapshot.location_key == location_key)
            return session.scalar(statement)

    def upsert_forecast(
        self,
        *,
        location_key: str,
        city_name: str,
        state_code: str,
        state_name: str | None,
        source_name: str,
        source_url: str | None,
        headline: str,
        summary: str,
        daily_forecast: list[dict],
        advisory_items: list[str],
        extra_payload: dict,
        collected_at: datetime,
        expires_at: datetime | None,
    ) -> WeatherForecastSnapshot:
        """Cria ou atualiza o snapshot de uma localidade."""
        with get_session() as session:
            statement = select(WeatherForecastSnapshot).where(WeatherForecastSnapshot.location_key == location_key)
            snapshot = session.scalar(statement)
            if snapshot is None:
                snapshot = WeatherForecastSnapshot(location_key=location_key)
                session.add(snapshot)

            snapshot.city_name = city_name
            snapshot.state_code = state_code
            snapshot.state_name = state_name
            snapshot.source_name = source_name
            snapshot.source_url = source_url
            snapshot.headline = headline
            snapshot.summary = summary
            snapshot.daily_forecast = daily_forecast
            snapshot.advisory_items = advisory_items
            snapshot.extra_payload = extra_payload
            snapshot.collected_at = collected_at
            snapshot.expires_at = expires_at

            session.commit()
            session.refresh(snapshot)
            return snapshot

    def list_active_alerts(self, *, limit: int | None = None) -> list[WeatherAlert]:
        """Lista alertas ativos, mais recentes primeiro."""
        with get_session() as session:
            statement = (
                select(WeatherAlert)
                .where(WeatherAlert.is_active.is_(True))
                .order_by(WeatherAlert.published_at.desc(), WeatherAlert.collected_at.desc(), WeatherAlert.id.desc())
            )
            if limit is not None:
                statement = statement.limit(limit)
            return list(session.scalars(statement).all())

    def upsert_alerts(self, *, source_name: str, alerts: list[dict]) -> list[WeatherAlert]:
        """Atualiza a lista de alertas ativos de uma fonte."""
        external_ids = {str(alert["external_id"]) for alert in alerts}

        with get_session() as session:
            existing_alerts = session.scalars(
                select(WeatherAlert).where(WeatherAlert.source_name == source_name)
            ).all()
            existing_by_external_id = {alert.external_id: alert for alert in existing_alerts}

            for existing_alert in existing_alerts:
                if existing_alert.external_id not in external_ids:
                    existing_alert.is_active = False
                    existing_alert.status = "encerrado"

            for payload in alerts:
                external_id = str(payload["external_id"])
                alert = existing_by_external_id.get(external_id)
                if alert is None:
                    alert = WeatherAlert(external_id=external_id, source_name=source_name)
                    session.add(alert)

                alert.title = str(payload["title"])
                alert.summary = payload.get("summary")
                alert.severity = str(payload.get("severity") or "informativo")
                alert.status = str(payload.get("status") or "ativo")
                alert.area = payload.get("area")
                alert.areas = list(payload.get("areas") or [])
                alert.source_url = payload.get("source_url")
                alert.published_at = payload.get("published_at")
                alert.effective_at = payload.get("effective_at")
                alert.expires_at = payload.get("expires_at")
                alert.is_active = bool(payload.get("is_active", True))
                alert.payload = dict(payload.get("payload") or {})
                alert.collected_at = payload.get("collected_at") or alert.collected_at

            session.commit()

            statement = (
                select(WeatherAlert)
                .where(WeatherAlert.source_name == source_name, WeatherAlert.is_active.is_(True))
                .order_by(WeatherAlert.published_at.desc(), WeatherAlert.collected_at.desc(), WeatherAlert.id.desc())
            )
            return list(session.scalars(statement).all())
