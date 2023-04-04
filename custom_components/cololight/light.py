"""Platform for LifeSmart ColoLight Light integration."""
import logging
from datetime import timedelta

from pycololight import (
    PyCololight,
    ColourSchemeException,
    ColourException,
    CycleSpeedException,
    ModeExecption,
    UnavailableException,
)

# Import the device class from the component that you want to support
# H-A .110 and later
try:
    from homeassistant.components.light import (
        SUPPORT_COLOR,
        SUPPORT_BRIGHTNESS,
        SUPPORT_EFFECT,
        ATTR_HS_COLOR,
        ATTR_BRIGHTNESS,
        ATTR_EFFECT,
        LightEntity as Light,
    )
# Legacy
except ImportError:
    from homeassistant.components.light import (
        SUPPORT_COLOR,
        SUPPORT_BRIGHTNESS,
        SUPPORT_EFFECT,
        ATTR_HS_COLOR,
        ATTR_BRIGHTNESS,
        ATTR_EFFECT,
        Light,
    )

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_MODE, STATE_ON
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.color as color_util

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "ColoLight"

DEFAULT_ICON = "mdi:hexagon-multiple"
HEXAGON_ICON = "mdi:hexagon-multiple"
STRIP_ICON = "mdi:led-strip-variant"

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    device = entry.data["device"] if "device" in entry.data else "hexagon"
    effects = []

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if entry.data.get("default_effects"):
        effects.extend(entry.data["default_effects"])

    if entry.data.get("dynamic_effects"):
        effects.extend(entry.data["dynamic_effects"])

    cololight_light = PyCololight(
        device=device, host=host, default_effects=False, dynamic_effects=False
    )

    if effects:
        cololight_light.restore_effects(effects)

    if entry.options:
        for effect_name, effect_options in entry.options.items():
            if effect_name not in [
                "removed_effects",
                "restored_effects",
                "default_effects",  # legacy options item
            ]:
                try:
                    cololight_light.add_custom_effect(
                        effect_name,
                        effect_options["color_scheme"],
                        effect_options["color"],
                        effect_options["cycle_speed"],
                        effect_options[CONF_MODE],
                    )
                except ColourSchemeException:
                    _LOGGER.error(
                        "Invalid color scheme '%s' given in custom effect '%s'. "
                        "Valid color schemes include: %s",
                        effect_options["color_scheme"],
                        effect_name,
                        cololight_light.custom_effect_colour_schemes(),
                    )
                    continue
                except ColourException:
                    _LOGGER.error(
                        "Invalid color '%s' given for color scheme '%s' in custom effect '%s'. "
                        "Valid colors for color scheme '%s' include: %s",
                        effect_options["color"],
                        effect_options["color_scheme"],
                        effect_name,
                        effect_options["color_scheme"],
                        cololight_light.custom_effect_colour_scheme_colours(
                            effect_options["color_scheme"]
                        ),
                    )
                    continue
                except CycleSpeedException:
                    _LOGGER.error(
                        "Invalid cycle speed '%s' given in custom effect '%s'. "
                        "Cycle speed must be between 1 and 32",
                        effect_options["cycle_speed"],
                        effect_name,
                    )
                    continue
                except ModeExecption:
                    _LOGGER.error(
                        "Invalid mode '%s' given in custom effect '%s'. "
                        "Mode must be between 1 and 27",
                        effect_options[CONF_MODE],
                        effect_name,
                    )
                    continue

    hass.data[DOMAIN][entry.entry_id] = cololight_light
    async_add_entities([coloLight(cololight_light, host, name)])


class coloLight(Light, RestoreEntity):
    def __init__(self, light, host, name):
        self._light = light
        self._host = host
        self._port = 8900
        self._name = name
        self._supported_features = SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_EFFECT
        self._effect_list = light.effects
        self._effect = None
        self._on = False
        self._brightness = 255
        self._hs_color = None
        self._available = True
        self._canUpdate = True

    @property
    def name(self):
        return self._name

    @property
    def available(self):
        return self._available

    @property
    def icon(self):
        icon = DEFAULT_ICON

        if self._light.device == "hexagon":
            icon = HEXAGON_ICON
        if self._light.device == "strip":
            icon = STRIP_ICON

        return icon

    @property
    def unique_id(self):
        """Return a unique id for the sensor."""
        return self._host

    @property
    def is_on(self):
        return self._on

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def supported_features(self) -> int:
        return self._supported_features

    @property
    def effect_list(self):
        return self._effect_list

    @property
    def effect(self):
        return self._effect

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def hs_color(self) -> tuple:
        return self._hs_color

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "LifeSmart",
            "model": "Cololight",
        }

    async def async_turn_on(self, **kwargs):
        hs_color = kwargs.get(ATTR_HS_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        effect = kwargs.get(ATTR_EFFECT)

        rgb = color_util.color_hs_to_RGB(*hs_color) if hs_color else None

        if rgb:
            self._hs_color = hs_color
            self._effect = None
            self._light.colour = rgb

        if effect:
            self._effect = effect
            self._hs_color = None
            self._light.effect = effect

        if brightness:
            self._brightness = brightness

        coverted_brightness = max(1, (int(self._brightness / 2.55)))

        self._light.on = coverted_brightness
        self._on = True
        self._canUpdate = False  # disable next update because light is not switched state to on and will return off state

    async def async_turn_off(self, **kwargs):
        self._light.on = 0
        self._on = False
        self._canUpdate = False  # disable next update because light is not switched state to off and will return on state

    async def async_added_to_hass(self):
        """Handle entity about to be added to hass event."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._on = last_state.state == STATE_ON
            self._effect = last_state.attributes.get("effect")
            self._brightness = last_state.attributes.get("brightness", 255)
            self._hs_color = last_state.attributes.get("hs_color")

    async def async_update(self):
        if self._canUpdate:
            # after setting the light on or off from home assistant. Home assistant will ask directly for a update, but the light has not switched state so the update function will recive the old state and that trows home assistant off. Now if you turn the light on or off. _canUpdate wil be set to False and the first update will be skipped
            await self.hass.async_add_executor_job(self._update_state)
        else:
            self._canUpdate = True

    def _update_state(self):
        try:
            self._light.state
            self._on = self._light.on
            if self._on:
                self._brightness = round(self._light.brightness * 2.55)

            self._available = True

        except UnavailableException:
            self._available = False

        except:
            _LOGGER.error("Error with update status of Cololight: %s", self._name)
