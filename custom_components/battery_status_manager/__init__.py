from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import BatteryStatusCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = BatteryStatusCoordinator(hass, entry)

    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # DataUpdateCoordinator only auto-reschedules when listeners are registered.
    # Since this integration has no HA entities, there are no listeners, so the
    # coordinator would never run again on its own. Schedule it explicitly.
    entry.async_on_unload(
        async_track_time_interval(
            hass,
            coordinator.async_request_refresh,
            timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
    )

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    coordinator: BatteryStatusCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.update_config(entry)
    await coordinator.async_request_refresh()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
