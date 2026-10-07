from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CRITICAL_THRESHOLD,
    CONF_ENABLE_CRITICAL_NOTIFICATION,
    CONF_ENABLE_LOW_BATTERY_NOTIFICATION,
    CONF_LOW_BATTERY_THRESHOLD,
    DEFAULT_CRITICAL_THRESHOLD,
    DEFAULT_ENABLE_CRITICAL,
    DEFAULT_ENABLE_LOW_BATTERY,
    DEFAULT_LOW_BATTERY_THRESHOLD,
    DOMAIN,
)
from .coordinator import BatteryStatusCoordinator

_SENSOR_TYPES = ["monitored", "below_warning", "below_critical", "unavailable"]

_SENSOR_ICONS = {
    "monitored": "mdi:battery-check",
    "below_warning": "mdi:battery-alert",
    "below_critical": "mdi:battery-alert-variant",
    "unavailable": "mdi:battery-off",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: BatteryStatusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BatteryStatusSensor(coordinator, entry, sensor_type)
        for sensor_type in _SENSOR_TYPES
    )


class BatteryStatusSensor(CoordinatorEntity[BatteryStatusCoordinator], SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: BatteryStatusCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_translation_key = sensor_type
        self._attr_icon = _SENSOR_ICONS[sensor_type]

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        data = self.coordinator.data
        config = self.coordinator._get_config()

        if self._sensor_type == "monitored":
            return len(self.coordinator._get_monitored_entity_ids())

        if self._sensor_type == "below_warning":
            if not config.get(CONF_ENABLE_LOW_BATTERY_NOTIFICATION, DEFAULT_ENABLE_LOW_BATTERY):
                return 0
            threshold = config.get(CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD)
            count = 0
            for info in data.values():
                if info.get("binary"):
                    if info.get("low_bat"):
                        count += 1
                elif info.get("level") is not None and info["level"] < threshold:
                    count += 1
            return count

        if self._sensor_type == "below_critical":
            if not config.get(CONF_ENABLE_CRITICAL_NOTIFICATION, DEFAULT_ENABLE_CRITICAL):
                return 0
            threshold = config.get(CONF_CRITICAL_THRESHOLD, DEFAULT_CRITICAL_THRESHOLD)
            return sum(
                1 for info in data.values()
                if not info.get("binary")
                and info.get("level") is not None
                and info["level"] < threshold
            )

        if self._sensor_type == "unavailable":
            return sum(1 for v in self.coordinator._unavailable_notified.values() if v)

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        config = self.coordinator._get_config()

        if self._sensor_type == "monitored":
            return {
                "batteries": [
                    {"name": info["name"], "level": info.get("level")}
                    for info in data.values()
                ]
            }

        if self._sensor_type == "below_warning":
            if not config.get(CONF_ENABLE_LOW_BATTERY_NOTIFICATION, DEFAULT_ENABLE_LOW_BATTERY):
                return {}
            threshold = config.get(CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD)
            affected = []
            for info in data.values():
                if info.get("binary") and info.get("low_bat"):
                    affected.append({"name": info["name"], "level": "LOW_BAT"})
                elif not info.get("binary") and info.get("level") is not None and info["level"] < threshold:
                    affected.append({"name": info["name"], "level": round(info["level"])})
            affected.sort(key=lambda x: (x["level"] == "LOW_BAT", x["level"] if x["level"] != "LOW_BAT" else 0))
            return {"batteries": affected}

        if self._sensor_type == "below_critical":
            if not config.get(CONF_ENABLE_CRITICAL_NOTIFICATION, DEFAULT_ENABLE_CRITICAL):
                return {}
            threshold = config.get(CONF_CRITICAL_THRESHOLD, DEFAULT_CRITICAL_THRESHOLD)
            affected = [
                {"name": info["name"], "level": round(info["level"])}
                for info in data.values()
                if not info.get("binary")
                and info.get("level") is not None
                and info["level"] < threshold
            ]
            affected.sort(key=lambda x: x["level"])
            return {"batteries": affected}

        if self._sensor_type == "unavailable":
            names = []
            for entity_id, ts in self.coordinator._unavailable_notified.items():
                if ts:
                    state = self.coordinator.hass.states.get(entity_id)
                    name = state.attributes.get("friendly_name", entity_id) if state else entity_id
                    names.append(name)
            return {"batteries": names}

        return {}
