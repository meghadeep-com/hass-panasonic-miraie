"""Shared helpers for Panasonic MirAIe platforms."""

from __future__ import annotations

import asyncio
import logging

from .const import API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


async def async_get_device_list(api) -> list[dict]:
    """Return the account's devices, or an empty list if they can't be fetched.

    Args:
        api: The PanasonicMirAIeAPI instance.

    """
    try:
        async with asyncio.timeout(API_TIMEOUT):
            return await api.get_devices()
    except TimeoutError:
        _LOGGER.error("Timeout retrieving devices from Panasonic MirAIe API")
    except Exception as err:  # noqa: BLE001
        _LOGGER.error("Error retrieving devices: %s", err)
    return []
