from __future__ import annotations

import logging
from datetime import datetime, time, timedelta, timezone
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.util.dt as dt_util

from .const import (
    CONF_ACTIVE_DAYS,
    CONF_CRITICAL_THRESHOLD,
    CONF_DROP_THRESHOLD,
    CONF_DROP_TIMEFRAME,
    CONF_ENABLE_CRITICAL_NOTIFICATION,
    CONF_ENABLE_DROP_NOTIFICATION,
    CONF_ENABLE_LOW_BATTERY_NOTIFICATION,
    CONF_ENABLE_REMINDER,
    CONF_ENABLE_TIME_WINDOW,
    CONF_ENABLE_UNAVAILABLE_NOTIFICATION,
    CONF_ENABLE_WEEKLY_REPORT,
    CONF_EXCLUDED_ENTITIES,
    CONF_LOW_BATTERY_THRESHOLD,
    CONF_MONITORED_DEVICES,
    CONF_MONITORED_ENTITIES,
    CONF_NOTIFICATION_SERVICES,
    CONF_NOTIFICATION_TITLE,
    CONF_REMINDER_INTERVAL,
    CONF_SCOPE,
    CONF_TIME_WINDOW_END,
    CONF_TIME_WINDOW_START,
    CONF_UNAVAILABLE_HOURS,
    CONF_WEEKLY_REPORT_DAY,
    CONF_WEEKLY_REPORT_TIME,
    CRITICAL_HYSTERESIS,
    DAY_KEYS,
    DEFAULT_ACTIVE_DAYS,
    DEFAULT_CRITICAL_THRESHOLD,
    DEFAULT_DROP_THRESHOLD,
    DEFAULT_DROP_TIMEFRAME,
    DEFAULT_ENABLE_CRITICAL,
    DEFAULT_ENABLE_DROP,
    DEFAULT_ENABLE_LOW_BATTERY,
    DEFAULT_ENABLE_REMINDER,
    DEFAULT_ENABLE_TIME_WINDOW,
    DEFAULT_ENABLE_UNAVAILABLE,
    DEFAULT_ENABLE_WEEKLY_REPORT,
    DEFAULT_LOW_BATTERY_THRESHOLD,
    DEFAULT_NOTIFICATION_TITLE,
    DEFAULT_REMINDER_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIME_WINDOW_END,
    DEFAULT_TIME_WINDOW_START,
    DEFAULT_UNAVAILABLE_HOURS,
    DEFAULT_WEEKLY_REPORT_DAY,
    DEFAULT_WEEKLY_REPORT_TIME,
    DOMAIN,
    LOW_BATTERY_HYSTERESIS,
    MAX_FORECAST_DAYS,
    MIN_FORECAST_HOURS,
    MIN_FORECAST_POINTS,
    SCOPE_ALL,
    SCOPE_BY_DEVICE,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)
UTC = timezone.utc
_EPOCH = "1970-01-01T00:00:00+00:00"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _is_within_time_window(start_str: str, end_str: str) -> bool:
    now: time = dt_util.now().time().replace(second=0, microsecond=0)
    start = time.fromisoformat(start_str)
    end = time.fromisoformat(end_str)
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end


def _is_active_day(active_days: list[str]) -> bool:
    return DAY_KEYS[dt_util.now().weekday()] in active_days


def _estimate_days_remaining(
    history: list[tuple[str, float]],
    current_level: float,
    target_level: float = 0.0,
) -> int | None:
    """Estimate days until battery reaches target_level using linear drain rate.

    Returns None when there is insufficient or non-draining data.
    """
    if len(history) < MIN_FORECAST_POINTS:
        return None

    oldest_ts, oldest_level = history[0]
    newest_ts, _ = history[-1]

    try:
        oldest_dt = datetime.fromisoformat(oldest_ts)
        newest_dt = datetime.fromisoformat(newest_ts)
    except (ValueError, TypeError):
        return None

    hours_span = (newest_dt - oldest_dt).total_seconds() / 3600
    if hours_span < MIN_FORECAST_HOURS:
        return None

    drain = oldest_level - current_level
    if drain <= 0:
        return None  # Battery is stable or charging

    drain_per_hour = drain / hours_span
    hours_left = (current_level - target_level) / drain_per_hour

    if hours_left <= 0:
        return 0

    days_left = hours_left / 24
    if days_left > MAX_FORECAST_DAYS:
        return None

    return max(0, round(days_left))


def _forecast_suffix(days: int | None) -> str:
    if days is None:
        return ""
    if days == 0:
        return " – Prognose: heute leer"
    if days == 1:
        return " – Prognose: noch ~1 Tag"
    return f" – Prognose: noch ~{days} Tage"


# ---------------------------------------------------------------------------
# Coordinator
# ---------------------------------------------------------------------------

class BatteryStatusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._entry = entry
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}")

        self._history: dict[str, list[tuple[str, float]]] = {}
        # ISO timestamp of last sent warning notification ("" = not notified)
        self._warning_notified_at: dict[str, str] = {}
        # ISO timestamp of last sent critical notification ("" = not notified)
        self._critical_notified_at: dict[str, str] = {}
        # ISO timestamp of last sent drop notification
        self._drop_notified: dict[str, str] = {}
        # Recovery events: entity_id → list of ISO timestamps
        self._recoveries: dict[str, list[str]] = {}
        # ISO timestamp of last weekly report
        self._last_weekly_report: str = ""
        # ISO timestamp of last valid numeric reading per entity
        self._last_seen: dict[str, str] = {}
        # ISO timestamp of last sent unavailable notification ("" = not notified)
        self._unavailable_notified: dict[str, str] = {}

        self._store_loaded = False

    def update_config(self, entry: ConfigEntry) -> None:
        self._entry = entry

    def _get_config(self) -> dict[str, Any]:
        return dict(self._entry.options or self._entry.data)

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def _async_load_store(self) -> None:
        data = await self._store.async_load() or {}
        self._history = data.get("history", {})
        self._drop_notified = data.get("drop_notified", {})
        self._recoveries = data.get("recoveries", {})
        self._last_weekly_report = data.get("last_weekly_report", "")
        self._critical_notified_at = data.get("critical_notified_at", {})
        self._last_seen = data.get("last_seen", {})
        self._unavailable_notified = data.get("unavailable_notified", {})

        # Migrate old boolean format → timestamp format
        raw = data.get("warning_notified_at", data.get("low_notified_at", data.get("low_notified", {})))
        self._warning_notified_at = {
            k: (_EPOCH if v is True else ("" if v is False else str(v)))
            for k, v in raw.items()
        }
        self._store_loaded = True

    async def _async_save_store(self) -> None:
        await self._store.async_save({
            "history": self._history,
            "warning_notified_at": self._warning_notified_at,
            "critical_notified_at": self._critical_notified_at,
            "drop_notified": self._drop_notified,
            "recoveries": self._recoveries,
            "last_weekly_report": self._last_weekly_report,
            "last_seen": self._last_seen,
            "unavailable_notified": self._unavailable_notified,
        })

    # ------------------------------------------------------------------
    # Entity discovery
    # ------------------------------------------------------------------

    def _get_monitored_entity_ids(self) -> list[str]:
        config = self._get_config()
        scope = config.get(CONF_SCOPE, SCOPE_ALL)
        entity_reg = er.async_get(self.hass)

        def _is_battery(e: er.RegistryEntry) -> bool:
            return (
                e.device_class == SensorDeviceClass.BATTERY
                or e.original_device_class == SensorDeviceClass.BATTERY
            ) and not e.disabled_by

        if scope == SCOPE_ALL:
            excluded = set(config.get(CONF_EXCLUDED_ENTITIES, []))
            return [
                e.entity_id for e in entity_reg.entities.values()
                if _is_battery(e) and e.entity_id not in excluded
            ]

        if scope == SCOPE_BY_DEVICE:
            device_ids = set(config.get(CONF_MONITORED_DEVICES, []))
            return [
                e.entity_id for e in entity_reg.entities.values()
                if _is_battery(e) and e.device_id in device_ids
            ]

        return list(config.get(CONF_MONITORED_ENTITIES, []))

    # ------------------------------------------------------------------
    # Recovery tracking
    # ------------------------------------------------------------------

    def _record_recovery(self, entity_id: str, now: datetime) -> None:
        events = self._recoveries.setdefault(entity_id, [])
        events.append(now.isoformat())
        cutoff = (now - timedelta(days=14)).isoformat()
        self._recoveries[entity_id] = [ts for ts in events if ts > cutoff]

    def _count_weekly_recoveries(self, now: datetime) -> int:
        week_ago = (now - timedelta(days=7)).isoformat()
        return sum(
            1
            for events in self._recoveries.values()
            for ts in events
            if ts > week_ago
        )

    # ------------------------------------------------------------------
    # Main update loop
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        if not self._store_loaded:
            await self._async_load_store()

        config = self._get_config()
        entity_ids = self._get_monitored_entity_ids()

        low_threshold: int = config.get(CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD)
        enable_low: bool = config.get(CONF_ENABLE_LOW_BATTERY_NOTIFICATION, DEFAULT_ENABLE_LOW_BATTERY)
        enable_critical: bool = config.get(CONF_ENABLE_CRITICAL_NOTIFICATION, DEFAULT_ENABLE_CRITICAL)
        critical_threshold: int = config.get(CONF_CRITICAL_THRESHOLD, DEFAULT_CRITICAL_THRESHOLD)
        enable_reminder: bool = config.get(CONF_ENABLE_REMINDER, DEFAULT_ENABLE_REMINDER)
        reminder_interval: int = int(config.get(CONF_REMINDER_INTERVAL, DEFAULT_REMINDER_INTERVAL))
        enable_drop: bool = config.get(CONF_ENABLE_DROP_NOTIFICATION, DEFAULT_ENABLE_DROP)
        drop_threshold: int = config.get(CONF_DROP_THRESHOLD, DEFAULT_DROP_THRESHOLD)
        drop_timeframe: int = int(config.get(CONF_DROP_TIMEFRAME, DEFAULT_DROP_TIMEFRAME))
        notification_services: list[str] = config.get(CONF_NOTIFICATION_SERVICES, [])
        notification_title: str = config.get(CONF_NOTIFICATION_TITLE, DEFAULT_NOTIFICATION_TITLE)
        enable_time_window: bool = config.get(CONF_ENABLE_TIME_WINDOW, DEFAULT_ENABLE_TIME_WINDOW)
        time_window_start: str = config.get(CONF_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
        time_window_end: str = config.get(CONF_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
        active_days: list[str] = config.get(CONF_ACTIVE_DAYS, DEFAULT_ACTIVE_DAYS)

        now = datetime.now(UTC)

        notifications_allowed = (
            (not enable_time_window or _is_within_time_window(time_window_start, time_window_end))
            and _is_active_day(active_days)
        )

        result: dict[str, Any] = {}

        enable_unavailable: bool = config.get(CONF_ENABLE_UNAVAILABLE_NOTIFICATION, DEFAULT_ENABLE_UNAVAILABLE)
        unavailable_hours: int = int(config.get(CONF_UNAVAILABLE_HOURS, DEFAULT_UNAVAILABLE_HOURS))

        for entity_id in entity_ids:
            state = self.hass.states.get(entity_id)
            if not state or state.state in ("unavailable", "unknown", ""):
                continue
            try:
                level = float(state.state)
            except (ValueError, TypeError):
                continue

            name: str = state.attributes.get("friendly_name", entity_id)
            result[entity_id] = {"level": level, "name": name}

            # Track last valid reading and clear any pending unavailable notification
            self._last_seen[entity_id] = now.isoformat()
            if self._unavailable_notified.get(entity_id):
                self._unavailable_notified[entity_id] = ""

            # Update history
            history = self._history.setdefault(entity_id, [])
            history.append((now.isoformat(), level))
            cutoff = (now - timedelta(hours=max(drop_timeframe, 48) + 1)).isoformat()
            self._history[entity_id] = [(ts, lvl) for ts, lvl in history if ts > cutoff]

            if not notification_services:
                continue

            forecast_days = _estimate_days_remaining(self._history[entity_id], level)

            # --- Warning threshold ---
            if enable_low:
                last_warned_at = self._warning_notified_at.get(entity_id, "")
                if level < low_threshold:
                    # If critical is active and the battery is already in critical
                    # territory, suppress the warning — the critical alert covers it.
                    in_critical_zone = enable_critical and level < critical_threshold
                    if not in_critical_zone:
                        should_notify = False
                        if not last_warned_at:
                            should_notify = True
                        elif enable_reminder:
                            hours_since = (now - datetime.fromisoformat(last_warned_at)).total_seconds() / 3600
                            if hours_since >= reminder_interval:
                                should_notify = True
                        if should_notify and notifications_allowed:
                            self._warning_notified_at[entity_id] = now.isoformat()
                            await self._send_notifications(
                                notification_services,
                                notification_title,
                                f"⚠️ {name}: Batteriestand bei {level:.0f}%"
                                f" (Schwelle: {low_threshold}%)"
                                f"{_forecast_suffix(forecast_days)}",
                            )
                elif level >= (low_threshold + LOW_BATTERY_HYSTERESIS) and last_warned_at:
                    self._warning_notified_at[entity_id] = ""
                    self._record_recovery(entity_id, now)

            # --- Critical threshold ---
            if enable_critical:
                last_critical_at = self._critical_notified_at.get(entity_id, "")
                if level < critical_threshold:
                    should_notify = False
                    if not last_critical_at:
                        should_notify = True
                    elif enable_reminder:
                        hours_since = (now - datetime.fromisoformat(last_critical_at)).total_seconds() / 3600
                        if hours_since >= reminder_interval:
                            should_notify = True
                    if should_notify and notifications_allowed:
                        self._critical_notified_at[entity_id] = now.isoformat()
                        await self._send_notifications(
                            notification_services,
                            notification_title,
                            f"🚨 {name}: Batteriestand KRITISCH bei {level:.0f}%"
                            f" (Schwelle: {critical_threshold}%)"
                            f"{_forecast_suffix(forecast_days)}",
                        )
                elif level >= (critical_threshold + CRITICAL_HYSTERESIS) and last_critical_at:
                    self._critical_notified_at[entity_id] = ""

            # --- Drop detection ---
            if enable_drop:
                window_start = (now - timedelta(hours=drop_timeframe)).isoformat()
                window_entries = [
                    (ts, lvl) for ts, lvl in self._history[entity_id]
                    if ts >= window_start
                ]
                if len(window_entries) >= 2:
                    max_historical = max(lvl for _, lvl in window_entries[:-1])
                    drop = max_historical - level
                    if drop >= drop_threshold:
                        last_drop = self._drop_notified.get(entity_id, "")
                        cooldown_expired = (
                            not last_drop
                            or (now - datetime.fromisoformat(last_drop)).total_seconds()
                            >= drop_timeframe * 3600
                        )
                        if cooldown_expired and notifications_allowed:
                            self._drop_notified[entity_id] = now.isoformat()
                            await self._send_notifications(
                                notification_services,
                                notification_title,
                                f"📉 {name}: Batteriestand um {drop:.0f}% innerhalb von"
                                f" {drop_timeframe}h gesunken (aktuell: {level:.0f}%)",
                            )

        # --- Unavailable detection ---
        if enable_unavailable and notification_services:
            for entity_id in entity_ids:
                last_seen_ts = self._last_seen.get(entity_id)
                if not last_seen_ts:
                    continue  # Never seen a valid reading — skip
                state = self.hass.states.get(entity_id)
                if not state or state.state not in ("unavailable", "unknown"):
                    continue  # Currently reporting fine
                hours_gone = (now - datetime.fromisoformat(last_seen_ts)).total_seconds() / 3600
                if hours_gone < unavailable_hours:
                    continue  # Not gone long enough yet
                if self._unavailable_notified.get(entity_id):
                    continue  # Already notified
                if not notifications_allowed:
                    continue
                name = state.attributes.get("friendly_name", entity_id)
                self._unavailable_notified[entity_id] = now.isoformat()
                await self._send_notifications(
                    notification_services,
                    notification_title,
                    f"📵 {name}: Keine Rückmeldung seit {hours_gone:.0f} Stunden"
                    f" – Batterie möglicherweise leer",
                )

        # --- Weekly report ---
        await self._maybe_send_weekly_report(now, config, entity_ids, notification_services, notification_title)

        await self._async_save_store()
        return result

    # ------------------------------------------------------------------
    # Weekly report
    # ------------------------------------------------------------------

    async def _maybe_send_weekly_report(
        self,
        now: datetime,
        config: dict[str, Any],
        entity_ids: list[str],
        services: list[str],
        title: str,
    ) -> None:
        if not config.get(CONF_ENABLE_WEEKLY_REPORT, DEFAULT_ENABLE_WEEKLY_REPORT):
            return
        if not services:
            return

        report_day: str = config.get(CONF_WEEKLY_REPORT_DAY, DEFAULT_WEEKLY_REPORT_DAY)
        report_time_str: str = config.get(CONF_WEEKLY_REPORT_TIME, DEFAULT_WEEKLY_REPORT_TIME)

        now_local = dt_util.now()
        if DAY_KEYS[now_local.weekday()] != report_day:
            return

        report_time = time.fromisoformat(report_time_str)
        if now_local.hour != report_time.hour:
            return

        if self._last_weekly_report:
            hours_since = (now - datetime.fromisoformat(self._last_weekly_report)).total_seconds() / 3600
            if hours_since < 6 * 24:
                return

        self._last_weekly_report = now.isoformat()

        low_threshold: int = config.get(CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD)
        critical_threshold: int = config.get(CONF_CRITICAL_THRESHOLD, DEFAULT_CRITICAL_THRESHOLD)
        enable_critical: bool = config.get(CONF_ENABLE_CRITICAL_NOTIFICATION, DEFAULT_ENABLE_CRITICAL)

        total = 0
        below_warning = 0
        below_critical = 0
        forecast_list: list[tuple[int, str, float]] = []  # (days, name, level)

        for entity_id in entity_ids:
            state = self.hass.states.get(entity_id)
            if not state or state.state in ("unavailable", "unknown", ""):
                continue
            try:
                level = float(state.state)
            except (ValueError, TypeError):
                continue

            total += 1
            name: str = state.attributes.get("friendly_name", entity_id)

            if level < low_threshold:
                below_warning += 1
            if enable_critical and level < critical_threshold:
                below_critical += 1

            days = _estimate_days_remaining(
                self._history.get(entity_id, []), level, target_level=low_threshold
            )
            if days is not None and days <= 7 and level >= low_threshold:
                forecast_list.append((days, name, level))

        forecast_list.sort(key=lambda x: x[0])
        recoveries = self._count_weekly_recoveries(now)

        lines = [
            "📊 Wöchentlicher Batteriebericht",
            "━━━━━━━━━━━━━━━━━━━━━━",
            f"Überwachte Batterien: {total}",
            f"Unter Warnschwelle ({low_threshold}%): {below_warning}",
        ]
        if enable_critical:
            lines.append(f"Unter kritischer Schwelle ({critical_threshold}%): {below_critical}")
        lines.append(f"Diese Woche geladen/gewechselt: {recoveries}")

        if forecast_list:
            lines.append("")
            lines.append("Prognose – benötigt Aufmerksamkeit in den nächsten 7 Tagen:")
            for days, name, level in forecast_list:
                tag = "heute" if days == 0 else (f"~{days} Tag" if days == 1 else f"~{days} Tagen")
                lines.append(f"• {name}: in {tag} (aktuell {level:.0f}%)")
        else:
            lines.append("Prognose: keine Batterien in den nächsten 7 Tagen kritisch")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━")

        await self._send_notifications(services, title, "\n".join(lines))

    # ------------------------------------------------------------------
    # Notification dispatch
    # ------------------------------------------------------------------

    async def _send_notifications(self, services: list[str], title: str, message: str) -> None:
        for service in services:
            try:
                await self.hass.services.async_call(
                    "notify",
                    service,
                    {"title": title, "message": message},
                    blocking=False,
                )
            except Exception as err:
                _LOGGER.error("Failed to send notification via notify.%s: %s", service, err)
