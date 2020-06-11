""" cololight """
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.const import CONF_MODE

DOMAIN = "cololight"


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Load the saved entities."""

    entry.add_update_listener(update_listener)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, LIGHT_DOMAIN)
    )
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, LIGHT_DOMAIN)


async def update_listener(hass, entry):
    """Handle options update."""
    for effect_name, effect_options in entry.options.items():
        hass.data[DOMAIN][entry.entry_id].add_custom_effect(
            effect_name,
            effect_options["color_scheme"],
            effect_options["color"],
            effect_options["cycle_speed"],
            effect_options[CONF_MODE],
        )
