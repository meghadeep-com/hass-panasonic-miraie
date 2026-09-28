"""Sensor platform for Panasonic MirAIe devices.

Diagnostics the cloud already reports but the climate entity never surfaced.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import PanasonicMirAIeEntity
from .helpers import async_get_device_list

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MirAIeSensor:
    """Description of a MirAIe read-only field."""

    key: str
    name: str
    icon: str | None = None
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    entity_category: EntityCategory | None = None
    enabled_default: bool = True


SENSORS: tuple[MirAIeSensor, ...] = (
    MirAIeSensor(
        key="rmtmp",
        name="Room temperature",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MirAIeSensor(
        key="rssi",
        name="WiFi signal",
        unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        enabled_default=False,
    ),
    MirAIeSensor(
        key="filterDustLevel",
        name="Filter dust level",
        icon="mdi:air-filter",
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MirAIeSensor(
        key="totalOperatingHours",
        name="Total operating hours",
        icon="mdi:timer-outline",
        unit=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Panasonic MirAIe sensor platform."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    devices = await async_get_device_list(api)

    entities = []
    for device in devices:
        topic = device["topic"][0] if device["topic"] else None
        if not topic:
            continue
        try:
            state = await api.get_device_state(device["deviceId"])
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Could not read %s while adding sensors: %s", device["deviceId"], err
            )
            state = {}
        for desc in SENSORS:
            # Fields like totalOperatingHours only exist on some models.
            if state and state.get(desc.key) is None:
                continue
            entities.append(
                PanasonicMirAIeSensor(
                    api, topic, device["deviceName"], device["deviceId"], desc
                )
            )

    if entities:
        async_add_entities(entities)


class PanasonicMirAIeSensor(PanasonicMirAIeEntity, SensorEntity):
    """A read-only MirAIe field exposed as a sensor."""

    def __init__(
        self, api, device_topic, device_name, device_id, description: MirAIeSensor
    ):
        """Initialize the sensor."""
        super().__init__(api, device_topic, device_name, device_id)
        self._description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_category = description.entity_category
        self._attr_entity_registry_enabled_default = description.enabled_default
        self._attr_unique_id = f"panasonic_miraie_{device_id}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value = self._state.get(self._description.key)
        if value is None or value == "":
            return None
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None
