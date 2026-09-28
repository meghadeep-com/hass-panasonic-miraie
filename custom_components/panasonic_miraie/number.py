"""Number platform for Panasonic MirAIe devices.

Converti (marketed as Converti7 or Converti8 depending on model) caps the unit's
cooling capacity. It is a continuous percentage, not a fixed set of steps, so it
is exposed as a number rather than as climate presets.
"""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import PanasonicMirAIeEntity
from .helpers import async_get_device_list

_LOGGER = logging.getLogger(__name__)

CONVERTI_KEY = "cnv"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Panasonic MirAIe number platform."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    devices = await async_get_device_list(api)

    entities = [
        PanasonicMirAIeConverti(api, topic, device["deviceName"], device["deviceId"])
        for device in devices
        for topic in [device["topic"][0] if device["topic"] else None]
        if topic
    ]

    if entities:
        async_add_entities(entities)


class PanasonicMirAIeConverti(PanasonicMirAIeEntity, NumberEntity):
    """Converti capacity limit, as a percentage."""

    _attr_name = "Converti capacity"
    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_min_value = 0
    _attr_native_max_value = 110
    _attr_native_step = 5
    _attr_mode = NumberMode.SLIDER

    def __init__(self, api, device_topic, device_name, device_id):
        """Initialize the Converti number."""
        super().__init__(api, device_topic, device_name, device_id)
        self._attr_unique_id = f"panasonic_miraie_{device_id}_converti"

    @property
    def native_value(self) -> float | None:
        """Return the current capacity limit, where 0 means Converti is off."""
        value = self._state.get(CONVERTI_KEY)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the capacity limit."""
        # The device ignores cnv writes unless it is in cool mode.
        if str(self._state.get("acmd", "")).lower() != "cool":
            _LOGGER.warning(
                "Converti was not applied to %s: the device only accepts it in cool "
                "mode (current mode: %s)",
                self._device_name,
                self._state.get("acmd"),
            )
            return

        self._state[CONVERTI_KEY] = int(value)
        self.async_write_ha_state()
        await self._api.set_feature(self._device_topic, CONVERTI_KEY, int(value))
