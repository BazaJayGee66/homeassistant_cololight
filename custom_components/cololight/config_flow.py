"""Config flow to configure Cololight component."""
import voluptuous as vol

from pycololight import PyCololight

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_MODE


from . import DOMAIN

light = PyCololight(device="hexagon", host=None)
DEFAULT_EFFECTS = light.default_effects

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME): str,
        vol.Optional(
            "default_effects",
            default=DEFAULT_EFFECTS,
        ): cv.multi_select(DEFAULT_EFFECTS),
    }
)


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

    async def async_step_import(self, import_config):
        return await self.async_step_user(user_input=import_config)


class CololightOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Cololight options."""

    def __init__(self, config_entry):
        """Initialize Cololight options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self._errors = {}

    def _get_color_schemes(self):
        cololight = self.hass.data["cololight"][self.config_entry.entry_id]
        color_schemes = []
        for color_scheme in cololight.custom_effect_colour_schemes():
            for color in cololight.custom_effect_colour_scheme_colours(color_scheme):
                color_schemes.append(f"{color_scheme} | {color}")

        return color_schemes

    def _split_color_scheme(self, color_scheme):
        split_color_scheme = color_scheme.split(" | ")
        color_scheme = split_color_scheme[0]
        color = split_color_scheme[1]
        return color_scheme, color

    def _get_effects(self):
        cololight = self.hass.data["cololight"][self.config_entry.entry_id]
        return dict(zip(cololight.effects, cololight.effects))

    def _get_removed_effects(self):
        cololight = self.hass.data["cololight"][self.config_entry.entry_id]
        effects = cololight.effects
        default_effects = DEFAULT_EFFECTS
        removed_effects = list(set(default_effects) - set(effects))
        return dict(zip(removed_effects, removed_effects))

    async def _is_valid(self, user_input):
        if not 1 <= user_input["cycle_speed"] <= 32:
            self._errors["cycle_speed"] = "invalid_cycle_speed"
        if not 1 <= user_input[CONF_MODE] <= 27:
            self._errors[CONF_MODE] = "invalid_mode"

        return not self._errors

    async def async_step_init(self, user_input=None):
        """Manage the Cololight options."""
        if user_input is not None:
            if user_input["select"] == "Create":
                return await self.async_step_options_add_custom_effect()
            elif user_input["select"] == "Delete":
                return await self.async_step_options_delete_effect()
            elif user_input["select"] == "Restore":
                return await self.async_step_options_restore_effect()

        options = {
            vol.Optional(
                "select",
                default=self.config_entry.options.get("select", "Create"),
            ): vol.In(["Create", "Delete", "Restore"]),
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))

    async def async_step_options_add_custom_effect(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            if await self._is_valid(user_input):
                color_scheme, color = self._split_color_scheme(
                    user_input["color_scheme"]
                )
                self.options.update(
                    {
                        user_input[CONF_NAME]: {
                            "color_scheme": color_scheme,
                            "color": color,
                            "cycle_speed": user_input["cycle_speed"],
                            CONF_MODE: user_input[CONF_MODE],
                        }
                    }
                )
                return self.async_create_entry(title="", data=self.options)
        else:
            user_input = {}

        color_schemes = self._get_color_schemes()

        options = {
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME)): str,
            vol.Required(
                "color_scheme", default=user_input.get("color_scheme")
            ): vol.In(color_schemes),
            vol.Required("cycle_speed", default=user_input.get("cycle_speed", 1)): int,
            vol.Required(CONF_MODE, default=user_input.get(CONF_MODE, 1)): int,
        }

        return self.async_show_form(
            step_id="options_add_custom_effect",
            data_schema=vol.Schema(options),
            errors=self._errors,
        )

    async def async_step_options_delete_effect(self, user_input=None):
        if user_input is not None:
            for effect in user_input[CONF_NAME]:
                if self.options.get(effect):
                    del self.options[effect]
                else:
                    self.config_entry.data["default_effects"].remove(effect)
                    self.options["default_effects"] = self.config_entry.data[
                        "default_effects"
                    ]
            return self.async_create_entry(title="", data=self.options)

        effects = self._get_effects()
        options = {
            vol.Required(
                CONF_NAME,
                default=self.config_entry.options.get(CONF_NAME),
            ): cv.multi_select(effects),
        }

        return self.async_show_form(
            step_id="options_delete_effect", data_schema=vol.Schema(options)
        )

    async def async_step_options_restore_effect(self, user_input=None):
        if user_input is not None:
            for effect in user_input[CONF_NAME]:
                self.config_entry.data["default_effects"].append(effect)

            self.options["restored_effects"] = self.config_entry.data["default_effects"]

            return self.async_create_entry(title="", data=self.options)

        effects = self._get_removed_effects()
        options = {
            vol.Required(
                CONF_NAME,
                default=self.config_entry.options.get(CONF_NAME),
            ): cv.multi_select(effects),
        }

        return self.async_show_form(
            step_id="options_restore_effect", data_schema=vol.Schema(options)
        )
