""" cololight """
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.core import callback
from homeassistant.const import CONF_NAME

DOMAIN = "cololight"


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Load the saved entities."""
    import_options_from_config(hass, entry)

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
    await hass.config_entries.async_forward_entry_unload(entry, LIGHT_DOMAIN)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, LIGHT_DOMAIN)
    )


@callback
def import_options_from_config(hass, entry):
    options = dict(entry.options)
    modified = False
    if entry.data.get("custom_effects"):
        for custom_effect in entry.data["custom_effects"]:
            options[custom_effect[CONF_NAME]] = custom_effect
            modified = True

    if modified:
        hass.config_entries.async_update_entry(entry, options=options)
