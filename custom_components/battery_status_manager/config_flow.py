from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    TimeSelector,
)

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
    DEFAULT_TIME_WINDOW_END,
    DEFAULT_TIME_WINDOW_START,
    DEFAULT_UNAVAILABLE_HOURS,
    DEFAULT_WEEKLY_REPORT_DAY,
    DEFAULT_WEEKLY_REPORT_TIME,
    DOMAIN,
    SCOPE_ALL,
    SCOPE_BY_DEVICE,
    SCOPE_BY_ENTITY,
)

_LOGGER = logging.getLogger(__name__)

_DAY_OPTIONS = [
    {"value": "mon", "label": "Monday"},
    {"value": "tue", "label": "Tuesday"},
    {"value": "wed", "label": "Wednesday"},
    {"value": "thu", "label": "Thursday"},
    {"value": "fri", "label": "Friday"},
    {"value": "sat", "label": "Saturday"},
    {"value": "sun", "label": "Sunday"},
]

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _get_battery_entities(hass: HomeAssistant) -> list[dict[str, str]]:
    entity_reg = er.async_get(hass)
    options: list[dict[str, str]] = []
    for entry in entity_reg.entities.values():
        if (
            entry.device_class == SensorDeviceClass.BATTERY
            or entry.original_device_class == SensorDeviceClass.BATTERY
        ) and not entry.disabled_by:
            state = hass.states.get(entry.entity_id)
            label = entry.name or entry.original_name or entry.entity_id
            if state:
                label = state.attributes.get("friendly_name", label)
                if state.state not in ("unavailable", "unknown", ""):
                    try:
                        float(state.state)
                        label = f"{label} ({state.state}%)"
                    except (ValueError, TypeError):
                        if state.state == "on":
                            label = f"{label} (LOW_BAT)"
            options.append({"value": entry.entity_id, "label": label})
    return sorted(options, key=lambda x: x["label"].lower())


def _get_battery_devices(hass: HomeAssistant) -> list[dict[str, str]]:
    entity_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)
    device_ids: set[str] = set()
    for entry in entity_reg.entities.values():
        if (
            entry.device_class == SensorDeviceClass.BATTERY
            or entry.original_device_class == SensorDeviceClass.BATTERY
        ) and not entry.disabled_by and entry.device_id:
            device_ids.add(entry.device_id)
    options: list[dict[str, str]] = []
    for device_id in device_ids:
        device = device_reg.async_get(device_id)
        if device:
            name = device.name_by_user or device.name or device_id
            options.append({"value": device_id, "label": name})
    return sorted(options, key=lambda x: x["label"].lower())


def _get_notification_services(hass: HomeAssistant) -> list[dict[str, str]]:
    services = hass.services.async_services().get("notify", {})
    return [{"value": name, "label": name} for name in sorted(services.keys())]


# ---------------------------------------------------------------------------
# Schema builders
# ---------------------------------------------------------------------------

def _scope_schema(current: str = SCOPE_ALL) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_SCOPE, default=current): SelectSelector(
            SelectSelectorConfig(
                options=[
                    {"value": SCOPE_ALL, "label": "Alle Batterieentitäten"},
                    {"value": SCOPE_BY_DEVICE, "label": "Auswahl nach Gerät"},
                    {"value": SCOPE_BY_ENTITY, "label": "Auswahl nach Entität"},
                ],
                mode=SelectSelectorMode.LIST,
            )
        ),
    })


def _exclude_schema(
    entity_options: list[dict[str, str]],
    current: list[str] | None = None,
) -> vol.Schema:
    valid_ids = {o["value"] for o in entity_options}
    current = [eid for eid in (current or []) if eid in valid_ids]
    return vol.Schema({
        vol.Optional(CONF_EXCLUDED_ENTITIES, default=current): SelectSelector(
            SelectSelectorConfig(
                options=entity_options,
                multiple=True,
                mode=SelectSelectorMode.LIST,
            )
        ),
    })


def _devices_schema(
    device_options: list[dict[str, str]],
    current: list[str] | None = None,
) -> vol.Schema:
    valid_ids = {o["value"] for o in device_options}
    current = [did for did in (current or []) if did in valid_ids]
    return vol.Schema({
        vol.Required(CONF_MONITORED_DEVICES, default=current): SelectSelector(
            SelectSelectorConfig(
                options=device_options,
                multiple=True,
                mode=SelectSelectorMode.LIST,
            )
        ),
    })


def _entities_schema(
    entity_options: list[dict[str, str]],
    current: list[str] | None = None,
) -> vol.Schema:
    valid_ids = {o["value"] for o in entity_options}
    if current is not None:
        current = [eid for eid in current if eid in valid_ids]
    default = current if current is not None else [o["value"] for o in entity_options]
    return vol.Schema({
        vol.Required(CONF_MONITORED_ENTITIES, default=default): SelectSelector(
            SelectSelectorConfig(
                options=entity_options,
                multiple=True,
                mode=SelectSelectorMode.LIST,
            )
        ),
    })


def _thresholds_schema(data: dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(
            CONF_ENABLE_LOW_BATTERY_NOTIFICATION,
            default=data.get(CONF_ENABLE_LOW_BATTERY_NOTIFICATION, DEFAULT_ENABLE_LOW_BATTERY),
        ): BooleanSelector(),
        vol.Required(
            CONF_LOW_BATTERY_THRESHOLD,
            default=data.get(CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD),
        ): NumberSelector(NumberSelectorConfig(
            min=1, max=99, step=1,
            mode=NumberSelectorMode.SLIDER,
            unit_of_measurement="%",
        )),
        vol.Required(
            CONF_ENABLE_CRITICAL_NOTIFICATION,
            default=data.get(CONF_ENABLE_CRITICAL_NOTIFICATION, DEFAULT_ENABLE_CRITICAL),
        ): BooleanSelector(),
        vol.Optional(
            CONF_CRITICAL_THRESHOLD,
            default=data.get(CONF_CRITICAL_THRESHOLD, DEFAULT_CRITICAL_THRESHOLD),
        ): NumberSelector(NumberSelectorConfig(
            min=1, max=99, step=1,
            mode=NumberSelectorMode.SLIDER,
            unit_of_measurement="%",
        )),
        vol.Required(
            CONF_ENABLE_DROP_NOTIFICATION,
            default=data.get(CONF_ENABLE_DROP_NOTIFICATION, DEFAULT_ENABLE_DROP),
        ): BooleanSelector(),
        vol.Optional(
            CONF_DROP_THRESHOLD,
            default=data.get(CONF_DROP_THRESHOLD, DEFAULT_DROP_THRESHOLD),
        ): NumberSelector(NumberSelectorConfig(
            min=1, max=99, step=1,
            mode=NumberSelectorMode.SLIDER,
            unit_of_measurement="%",
        )),
        vol.Optional(
            CONF_DROP_TIMEFRAME,
            default=data.get(CONF_DROP_TIMEFRAME, DEFAULT_DROP_TIMEFRAME),
        ): NumberSelector(NumberSelectorConfig(
            min=1, max=168, step=1,
            mode=NumberSelectorMode.BOX,
            unit_of_measurement="h",
        )),
        vol.Required(
            CONF_ENABLE_UNAVAILABLE_NOTIFICATION,
            default=data.get(CONF_ENABLE_UNAVAILABLE_NOTIFICATION, DEFAULT_ENABLE_UNAVAILABLE),
        ): BooleanSelector(),
        vol.Optional(
            CONF_UNAVAILABLE_HOURS,
            default=data.get(CONF_UNAVAILABLE_HOURS, DEFAULT_UNAVAILABLE_HOURS),
        ): SelectSelector(SelectSelectorConfig(
            options=[
                {"value": "12", "label": "12 Stunden"},
                {"value": "24", "label": "24 Stunden"},
            ],
            mode=SelectSelectorMode.LIST,
        )),
    })


def _notifications_schema(
    service_options: list[dict[str, str]],
    data: dict[str, Any],
) -> vol.Schema:
    return vol.Schema({
        vol.Required(
            CONF_NOTIFICATION_SERVICES,
            default=data.get(CONF_NOTIFICATION_SERVICES, []),
        ): SelectSelector(SelectSelectorConfig(
            options=service_options,
            multiple=True,
            mode=SelectSelectorMode.LIST,
        )),
        vol.Optional(
            CONF_NOTIFICATION_TITLE,
            default=data.get(CONF_NOTIFICATION_TITLE, DEFAULT_NOTIFICATION_TITLE),
        ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
        vol.Required(
            CONF_ENABLE_TIME_WINDOW,
            default=data.get(CONF_ENABLE_TIME_WINDOW, DEFAULT_ENABLE_TIME_WINDOW),
        ): BooleanSelector(),
        vol.Optional(
            CONF_TIME_WINDOW_START,
            default=data.get(CONF_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START),
        ): TimeSelector(),
        vol.Optional(
            CONF_TIME_WINDOW_END,
            default=data.get(CONF_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END),
        ): TimeSelector(),
        vol.Required(
            CONF_ACTIVE_DAYS,
            default=data.get(CONF_ACTIVE_DAYS, DEFAULT_ACTIVE_DAYS),
        ): SelectSelector(SelectSelectorConfig(
            options=_DAY_OPTIONS,
            multiple=True,
            mode=SelectSelectorMode.LIST,
        )),
        vol.Required(
            CONF_ENABLE_REMINDER,
            default=data.get(CONF_ENABLE_REMINDER, DEFAULT_ENABLE_REMINDER),
        ): BooleanSelector(),
        vol.Optional(
            CONF_REMINDER_INTERVAL,
            default=data.get(CONF_REMINDER_INTERVAL, DEFAULT_REMINDER_INTERVAL),
        ): NumberSelector(NumberSelectorConfig(
            min=1, max=168, step=1,
            mode=NumberSelectorMode.BOX,
            unit_of_measurement="h",
        )),
        vol.Required(
            CONF_ENABLE_WEEKLY_REPORT,
            default=data.get(CONF_ENABLE_WEEKLY_REPORT, DEFAULT_ENABLE_WEEKLY_REPORT),
        ): BooleanSelector(),
        vol.Optional(
            CONF_WEEKLY_REPORT_DAY,
            default=data.get(CONF_WEEKLY_REPORT_DAY, DEFAULT_WEEKLY_REPORT_DAY),
        ): SelectSelector(SelectSelectorConfig(
            options=_DAY_OPTIONS,
            mode=SelectSelectorMode.LIST,
        )),
        vol.Optional(
            CONF_WEEKLY_REPORT_TIME,
            default=data.get(CONF_WEEKLY_REPORT_TIME, DEFAULT_WEEKLY_REPORT_TIME),
        ): TimeSelector(),
    })


# ---------------------------------------------------------------------------
# Config Flow
# ---------------------------------------------------------------------------

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            scope = user_input[CONF_SCOPE]
            if scope == SCOPE_ALL:
                return await self.async_step_exclude_entities()
            if scope == SCOPE_BY_DEVICE:
                return await self.async_step_select_devices()
            return await self.async_step_select_entities()

        return self.async_show_form(
            step_id="user",
            data_schema=_scope_schema(self._data.get(CONF_SCOPE, SCOPE_ALL)),
        )

    async def async_step_exclude_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entity_options = _get_battery_entities(self.hass)
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_thresholds()

        return self.async_show_form(
            step_id="exclude_entities",
            data_schema=_exclude_schema(
                entity_options, self._data.get(CONF_EXCLUDED_ENTITIES)
            ),
        )

    async def async_step_select_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        device_options = _get_battery_devices(self.hass)
        if not device_options:
            return self.async_abort(reason="no_battery_devices")
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_MONITORED_DEVICES):
                errors[CONF_MONITORED_DEVICES] = "no_selection"
            else:
                self._data.update(user_input)
                return await self.async_step_thresholds()
        return self.async_show_form(
            step_id="select_devices",
            data_schema=_devices_schema(device_options, self._data.get(CONF_MONITORED_DEVICES)),
            errors=errors,
        )

    async def async_step_select_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entity_options = _get_battery_entities(self.hass)
        if not entity_options:
            return self.async_abort(reason="no_battery_entities")
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_MONITORED_ENTITIES):
                errors[CONF_MONITORED_ENTITIES] = "no_selection"
            else:
                self._data.update(user_input)
                return await self.async_step_thresholds()
        return self.async_show_form(
            step_id="select_entities",
            data_schema=_entities_schema(entity_options, self._data.get(CONF_MONITORED_ENTITIES)),
            errors=errors,
        )

    async def async_step_thresholds(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifications()
        return self.async_show_form(
            step_id="thresholds",
            data_schema=_thresholds_schema(self._data),
        )

    async def async_step_notifications(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        service_options = _get_notification_services(self.hass)
        if not service_options:
            return self.async_abort(reason="no_notification_services")
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="Battery Status Manager", data=self._data)
        return self.async_show_form(
            step_id="notifications",
            data_schema=_notifications_schema(service_options, self._data),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return OptionsFlowHandler(config_entry)


# ---------------------------------------------------------------------------
# Options Flow (reconfiguration)
# ---------------------------------------------------------------------------

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._data: dict[str, Any] = dict(
            config_entry.options if config_entry.options else config_entry.data
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            scope = user_input[CONF_SCOPE]
            if scope == SCOPE_ALL:
                return await self.async_step_exclude_entities()
            if scope == SCOPE_BY_DEVICE:
                return await self.async_step_select_devices()
            return await self.async_step_select_entities()
        return self.async_show_form(
            step_id="init",
            data_schema=_scope_schema(self._data.get(CONF_SCOPE, SCOPE_ALL)),
        )

    async def async_step_exclude_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entity_options = _get_battery_entities(self.hass)
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_thresholds()
        return self.async_show_form(
            step_id="exclude_entities",
            data_schema=_exclude_schema(entity_options, self._data.get(CONF_EXCLUDED_ENTITIES)),
        )

    async def async_step_select_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        device_options = _get_battery_devices(self.hass)
        if not device_options:
            return self.async_abort(reason="no_battery_devices")
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_MONITORED_DEVICES):
                errors[CONF_MONITORED_DEVICES] = "no_selection"
            else:
                self._data.update(user_input)
                return await self.async_step_thresholds()
        return self.async_show_form(
            step_id="select_devices",
            data_schema=_devices_schema(device_options, self._data.get(CONF_MONITORED_DEVICES)),
            errors=errors,
        )

    async def async_step_select_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entity_options = _get_battery_entities(self.hass)
        if not entity_options:
            return self.async_abort(reason="no_battery_entities")
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_MONITORED_ENTITIES):
                errors[CONF_MONITORED_ENTITIES] = "no_selection"
            else:
                self._data.update(user_input)
                return await self.async_step_thresholds()
        return self.async_show_form(
            step_id="select_entities",
            data_schema=_entities_schema(entity_options, self._data.get(CONF_MONITORED_ENTITIES)),
            errors=errors,
        )

    async def async_step_thresholds(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifications()
        return self.async_show_form(
            step_id="thresholds",
            data_schema=_thresholds_schema(self._data),
        )

    async def async_step_notifications(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        service_options = _get_notification_services(self.hass)
        if not service_options:
            return self.async_abort(reason="no_notification_services")
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(data=self._data)
        return self.async_show_form(
            step_id="notifications",
            data_schema=_notifications_schema(service_options, self._data),
        )
