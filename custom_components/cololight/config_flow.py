"""Config flow to configure Cololight component."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME

from . import DOMAIN


DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_NAME): str,})


@config_entries.HANDLERS.register(DOMAIN)
class CololightConfigFlow(config_entries.ConfigFlow):
    """Cololight configuration flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
