""" cololight """
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

DOMAIN = "cololight"
PLATFORMS = [Platform.LIGHT]


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Load the saved entities."""

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_forward_entry_unload(
        entry, LIGHT_DOMAIN
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
