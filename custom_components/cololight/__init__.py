""" cololight """
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

DOMAIN = "cololight"


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Load the saved entities."""

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light")
    )
    return True
