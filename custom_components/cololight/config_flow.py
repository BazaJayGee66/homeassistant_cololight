"""Config flow to configure Cololight component."""
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_MODE


from . import DOMAIN


DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_NAME): str,})


@config_entries.HANDLERS.register(DOMAIN)
class CololightConfigFlow(config_entries.ConfigFlow):
    """Cololight configuration flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return CololightOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CololightOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Cololight options."""

    def __init__(self, config_entry):
        """Initialize Cololight options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the Cololight options."""
        if user_input is not None:
            if user_input["select"] == "Create":
                return await self.async_step_options_add_custom_effect()
            elif user_input["select"] == "Delete":
                return await self.async_step_options_delete_custom_effect()

        options = {
            vol.Optional(
                "select", default=self.config_entry.options.get("select", "Create"),
            ): vol.In(["Create", "Delete"]),
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))

    async def async_step_options_add_custom_effect(self, user_input=None):
        if user_input is not None:
            self.options.update(
                {
                    user_input[CONF_NAME]: {
                        "color_scheme": user_input["color_scheme"],
                        "color": user_input["color"],
                        "cycle_speed": user_input["cycle_speed"],
                        CONF_MODE: user_input[CONF_MODE],
                    }
                }
            )
            return self.async_create_entry(title="", data=self.options)

        options = {
            vol.Required(CONF_NAME): str,
            vol.Required("color_scheme"): str,
            vol.Required("color"): str,
            vol.Required("cycle_speed"): int,
            vol.Required(CONF_MODE): int,
        }

        return self.async_show_form(
            step_id="options_add_custom_effect", data_schema=vol.Schema(options)
        )

    async def async_step_options_delete_custom_effect(self, user_input=None):
        if user_input is not None:
            for effect in user_input[CONF_NAME]:
                del self.options[effect]
            return self.async_create_entry(title="", data=self.options)

        effects = dict(zip(self.options.keys(), self.options.keys()))
        options = {
            vol.Required(
                CONF_NAME, default=self.config_entry.options.get(CONF_NAME),
            ): cv.multi_select(effects),
        }

        return self.async_show_form(
            step_id="options_delete_custom_effect", data_schema=vol.Schema(options)
        )
