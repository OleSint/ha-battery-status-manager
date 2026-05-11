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
    CONF_DROP_THRESHOLD,
    CONF_DROP_TIMEFRAME,
    CONF_ENABLE_DROP_NOTIFICATION,
    CONF_ENABLE_LOW_BATTERY_NOTIFICATION,
    CONF_ENABLE_REMINDER,
    CONF_ENABLE_TIME_WINDOW,
    CONF_LOW_BATTERY_THRESHOLD,
    CONF_MONITORED_DEVICES,
    CONF_MONITORED_ENTITIES,
    CONF_NOTIFICATION_SERVICES,
    CONF_NOTIFICATION_TITLE,
    CONF_REMINDER_INTERVAL,
    CONF_SCOPE,
    CONF_TIME_WINDOW_END,
    CONF_TIME_WINDOW_START,
    DAY_KEYS,
    DEFAULT_ACTIVE_DAYS,
    DEFAULT_DROP_THRESHOLD,
    DEFAULT_DROP_TIMEFRAME,
    DEFAULT_ENABLE_DROP,
    DEFAULT_ENABLE_LOW_BATTERY,
    DEFAULT_ENABLE_REMINDER,
    DEFAULT_ENABLE_TIME_WINDOW,
    DEFAULT_LOW_BATTERY_THRESHOLD,
    DEFAULT_NOTIFICATION_TITLE,
    DEFAULT_REMINDER_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIME_WINDOW_END,
    DEFAULT_TIME_WINDOW_START,
    DOMAIN,
    LOW_BATTERY_HYSTERESIS,
    SCOPE_ALL,
    SCOPE_BY_DEVICE,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)
UTC = timezone.utc

# Sentinel used during migration of old boolean storage values
_EPOCH = "1970-01-01T00:00:00+00:00"


def _is_within_time_window(start_str: str, end_str: str) -> bool:
    """Return True if the current local HA time is within [start, end].

    Handles overnight windows (e.g. 22:00–06:00) correctly.
    """
    now: time = dt_util.now().time().replace(second=0, microsecond=0)
    start = time.fromisoformat(start_str)
    end = time.fromisoformat(end_str)
    if start <= end:
        return start <= now <= end
    # Overnight: e.g. 22:00–06:00
    return now >= start or now <= end


def _is_active_day(active_days: list[str]) -> bool:
    """Return True if today's weekday is in the allowed days list."""
    return DAY_KEYS[dt_util.now().weekday()] in active_days


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
        # entity_id -> list of (iso_timestamp, level)
        self._history: dict[str, list[tuple[str, float]]] = {}
        # entity_id -> ISO timestamp of last sent low-battery notification, "" = not yet notified
        self._low_notified_at: dict[str, str] = {}
        # entity_id -> ISO timestamp of last sent drop notification
        self._drop_notified: dict[str, str] = {}
        self._store_loaded = False

    def update_config(self, entry: ConfigEntry) -> None:
        self._entry = entry

    def _get_config(self) -> dict[str, Any]:
        return dict(self._entry.options or self._entry.data)

    async def _async_load_store(self) -> None:
        data = await self._store.async_load() or {}
        self._history = data.get("history", {})
        self._drop_notified = data.get("drop_notified", {})

        # Migrate from old boolean format (v1) to timestamp format (v2)
        raw = data.get("low_notified_at", data.get("low_notified", {}))
        self._low_notified_at = {
            k: (_EPOCH if v is True else ("" if v is False else v))
            for k, v in raw.items()
        }
        self._store_loaded = True

    async def _async_save_store(self) -> None:
        await self._store.async_save({
            "history": self._history,
            "low_notified_at": self._low_notified_at,
            "drop_notified": self._drop_notified,
        })

    def _get_monitored_entity_ids(self) -> list[str]:
        config = self._get_config()
        scope = config.get(CONF_SCOPE, SCOPE_ALL)
        entity_reg = er.async_get(self.hass)

        def _is_battery(entry: er.RegistryEntry) -> bool:
            return (
                entry.device_class == SensorDeviceClass.BATTERY
                or entry.original_device_class == SensorDeviceClass.BATTERY
            ) and not entry.disabled_by

        if scope == SCOPE_ALL:
            return [e.entity_id for e in entity_reg.entities.values() if _is_battery(e)]

        if scope == SCOPE_BY_DEVICE:
            device_ids = set(config.get(CONF_MONITORED_DEVICES, []))
            return [
                e.entity_id for e in entity_reg.entities.values()
                if _is_battery(e) and e.device_id in device_ids
            ]

        return list(config.get(CONF_MONITORED_ENTITIES, []))

    async def _async_update_data(self) -> dict[str, Any]:
        if not self._store_loaded:
            await self._async_load_store()

        config = self._get_config()
        entity_ids = self._get_monitored_entity_ids()

        low_threshold: int = config.get(CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD)
        enable_low: bool = config.get(CONF_ENABLE_LOW_BATTERY_NOTIFICATION, DEFAULT_ENABLE_LOW_BATTERY)
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

            # Append to history and trim entries older than the window
            history = self._history.setdefault(entity_id, [])
            history.append((now.isoformat(), level))
            cutoff = (now - timedelta(hours=drop_timeframe + 1)).isoformat()
            self._history[entity_id] = [(ts, lvl) for ts, lvl in history if ts > cutoff]

            if not notification_services:
                continue

            # --- Low battery check (with optional daily reminder) ---
            if enable_low:
                last_notified_at = self._low_notified_at.get(entity_id, "")

                if level < low_threshold:
                    should_notify = False

                    if not last_notified_at:
                        # First time we detect this entity below threshold
                        should_notify = True
                    elif enable_reminder:
                        hours_since = (
                            now - datetime.fromisoformat(last_notified_at)
                        ).total_seconds() / 3600
                        if hours_since >= reminder_interval:
                            should_notify = True

                    if should_notify and notifications_allowed:
                        self._low_notified_at[entity_id] = now.isoformat()
                        await self._send_notifications(
                            notification_services,
                            notification_title,
                            f"⚠️ {name}: Batteriestand bei {level:.0f}% (Schwelle: {low_threshold}%)",
                        )

                elif level >= (low_threshold + LOW_BATTERY_HYSTERESIS) and last_notified_at:
                    # Battery recovered — reset so the next drop triggers a fresh notification
                    self._low_notified_at[entity_id] = ""

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
                                (
                                    f"📉 {name}: Batteriestand um {drop:.0f}% innerhalb von"
                                    f" {drop_timeframe}h gesunken (aktuell: {level:.0f}%)"
                                ),
                            )

        await self._async_save_store()
        return result

    async def _send_notifications(
        self, services: list[str], title: str, message: str
    ) -> None:
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
