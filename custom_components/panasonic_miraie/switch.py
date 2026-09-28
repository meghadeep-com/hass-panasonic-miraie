"""Switch platform for Panasonic MirAIe devices.

The MirAIe app exposes these as independent toggles, so they are switches here
rather than mutually exclusive climate presets.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import PanasonicMirAIeEntity
from .helpers import async_get_device_list

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MirAIeSwitch:
    """Description of a MirAIe on/off field."""

    key: str
    name: str
    icon: str
    entity_category: EntityCategory | None = None


SWITCHES: tuple[MirAIeSwitch, ...] = (
    MirAIeSwitch(key="acpm", name="Powerful", icon="mdi:rocket-launch"),
    MirAIeSwitch(key="acem", name="Eco mode", icon="mdi:leaf"),
    MirAIeSwitch(key="acec", name="Clean", icon="mdi:broom"),
    MirAIeSwitch(
        key="acdc",
        name="Display",
        icon="mdi:television-ambient-light",
        entity_category=EntityCategory.CONFIG,
    ),
    MirAIeSwitch(
        key="bzr",
        name="Buzzer",
        icon="mdi:volume-high",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Panasonic MirAIe switch platform."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    devices = await async_get_device_list(api)

    entities = [
        PanasonicMirAIeSwitch(api, topic, device["deviceName"], device["deviceId"], desc)
        for device in devices
        for topic in [device["topic"][0] if device["topic"] else None]
        if topic
        for desc in SWITCHES
    ]

    if entities:
        async_add_entities(entities)


class PanasonicMirAIeSwitch(PanasonicMirAIeEntity, SwitchEntity):
    """An on/off MirAIe field exposed as a switch."""

    def __init__(
        self, api, device_topic, device_name, device_id, description: MirAIeSwitch
    ):
        """Initialize the switch."""
        super().__init__(api, device_topic, device_name, device_id)
        self._description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_entity_category = description.entity_category
        self._attr_unique_id = f"panasonic_miraie_{device_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the field is on."""
        value = self._state.get(self._description.key)
        if value is None:
            return None
        return str(value).lower() == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the field on."""
        await self._async_set("on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the field off."""
        await self._async_set("off")

    async def _async_set(self, value: str) -> None:
        self._state[self._description.key] = value
        self.async_write_ha_state()
        await self._api.set_feature(self._device_topic, self._description.key, value)
