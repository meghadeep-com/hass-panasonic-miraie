"""Shared base entity for Panasonic MirAIe platforms."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PanasonicMirAIeEntity(Entity):
    """Base entity that mirrors one device's MQTT state stream.

    Every platform shares a single `<topic>/state` subscription per device; the
    MQTT handler fans each message out to all registered callbacks.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, api, device_topic: str, device_name: str, device_id: str):
        """Initialize the entity.

        Args:
            api: The API instance for communicating with the device.
            device_topic: The MQTT topic for the device.
            device_name: The name of the device.
            device_id: The unique identifier of the device.

        """
        self._api = api
        self._device_topic = device_topic
        self._device_name = device_name
        self._device_id = device_id
        self._state: dict[str, Any] = {}

    @property
    def device_info(self):
        """Return device information, matching the climate entity's device."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Panasonic",
            "model": "MirAIe AC",
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to the device state topic and seed the initial state."""
        await super().async_added_to_hass()
        await self._api.mqtt_handler.subscribe(
            f"{self._device_topic}/state", self._handle_state_update
        )
        try:
            state = await self._api.get_device_state(self._device_id)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Initial state fetch failed for %s: %s", self._device_id, err)
            return
        if state:
            self._state.update(state)
            self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Drop only this entity's callback, leaving other entities subscribed."""
        await self._api.mqtt_handler.unsubscribe(
            f"{self._device_topic}/state", self._handle_state_update
        )
        await super().async_will_remove_from_hass()

    async def _handle_state_update(self, topic: str, payload: dict[str, Any]) -> None:
        """Merge an incoming state payload and refresh the entity."""
        self._state.update(payload)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return whether the device last reported itself as online."""
        return str(self._state.get("onlineStatus", "true")).lower() == "true"
