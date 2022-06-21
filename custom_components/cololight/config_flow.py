"""Config flow to configure Cololight component."""
import voluptuous as vol

from pycololight import PyCololight

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_MODE


from . import DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class CololightConfigFlow(config_entries.ConfigFlow):
    """Cololight configuration flow."""

    VERSION = 1

    def __init__(self):
        self.device_data = None

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
            self.device_data = user_input
            return await self.async_step_device_effects()

        options = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_NAME): str,
                vol.Required(
                    "device",
                    default="hexagon",
                ): vol.In(["hexagon", "strip"]),
            }
        )

        return self.async_show_form(step_id="user", data_schema=options, errors=errors)

    async def async_step_device_effects(self, user_input=None):
        """Set which effects to add to device"""
        if user_input is not None:
            data = self.device_data
            data.update(user_input)
            return self.async_create_entry(title=data[CONF_NAME], data=data)

        device = self.device_data["device"]
        light = PyCololight(device=device, host=None)
        default_effects = light.default_effects
        dynamic_effects = light.dynamic_effects

        options = {
            vol.Optional(
                "default_effects",
                default=default_effects,
            ): cv.multi_select(default_effects),
        }

        if dynamic_effects:
            options.update(
                {
                    vol.Optional(
                        "dynamic_effects",
                    ): cv.multi_select(dynamic_effects),
                }
            )

        return self.async_show_form(
            step_id="device_effects", data_schema=vol.Schema(options)
        )


class CololightOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Cololight options."""

    def __init__(self, config_entry):
        """Initialize Cololight options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self.cololight = None
        self._errors = {}

    def _get_cololight(self):
        self.cololight = self.hass.data["cololight"][self.config_entry.entry_id]

    def _get_color_schemes(self):
        color_schemes = []
        for color_scheme in self.cololight.custom_effect_colour_schemes():
            for color in self.cololight.custom_effect_colour_scheme_colours(
                color_scheme
            ):
                color_schemes.append(f"{color_scheme} | {color}")

        return color_schemes

    def _split_color_scheme(self, color_scheme):
        split_color_scheme = color_scheme.split(" | ")
        color_scheme = split_color_scheme[0]
        color = split_color_scheme[1]
        return color_scheme, color

    def _get_effects(self):
        return dict(zip(self.cololight.effects, self.cololight.effects))

    def _get_removed_effects(self, effects_type):
        effects = self.cololight.effects
        device_effects = []
        if effects_type == "default":
            device_effects = self.cololight.default_effects
        if effects_type == "dynamic":
            device_effects = self.cololight.dynamic_effects
        removed_effects = list(set(device_effects) - set(effects))
        return dict(zip(removed_effects, removed_effects))

    async def _is_valid(self, user_input):
        if not 1 <= user_input["cycle_speed"] <= 32:
            self._errors["cycle_speed"] = "invalid_cycle_speed"
        if not 1 <= user_input[CONF_MODE] <= 27:
            self._errors[CONF_MODE] = "invalid_mode"

        return not self._errors

    async def async_step_init(self, user_input=None):
        """Manage the Cololight options."""
        self._get_cololight()
        return self.async_show_menu(
            step_id="init",
            menu_options=["create_effect", "remove_effect", "restore_effect"],
        )

    async def async_step_create_effect(self, user_input=None):
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
            step_id="create_effect",
            data_schema=vol.Schema(options),
            errors=self._errors,
        )

    async def async_step_remove_effect(self, user_input=None):
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
            step_id="remove_effect", data_schema=vol.Schema(options)
        )

    async def async_step_restore_effect(self, user_input=None):
        if user_input is not None:
            for effect in user_input["default_effects"]:
                self.config_entry.data["default_effects"].append(effect)

            for effect in user_input["dynamic_effects"]:
                self.config_entry.data["dynamic_effects"].append(effect)

            self.options["restored_effects"] = self.config_entry.data["default_effects"]

            return self.async_create_entry(title="", data=self.options)

        default_effects = self._get_removed_effects("default")
        dynamic_effects = self._get_removed_effects("dynamic")

        options = {
            vol.Optional(
                "default_effects",
                default=[],
            ): cv.multi_select(default_effects),
            vol.Optional(
                "dynamic_effects",
                default=[],
            ): cv.multi_select(dynamic_effects),
        }

        return self.async_show_form(
            step_id="restore_effect", data_schema=vol.Schema(options)
        )
