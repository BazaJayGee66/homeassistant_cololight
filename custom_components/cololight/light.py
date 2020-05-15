"""Platform for LifeSmart ColoLight Light integration."""
import logging
import voluptuous as vol
import socket

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
from homeassistant.components.light import (
    PLATFORM_SCHEMA,
    SUPPORT_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_EFFECT,
    ATTR_HS_COLOR,
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    Light,
)
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.util.color as color_util

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "ColoLight"

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the cololight light platform."""
    host = config[CONF_HOST]
    name = config[CONF_NAME]

    cololight_light = PyCololight(host)

    async_add_entities([coloLight(cololight_light, host, name)])


class coloLight(Light):
    def __init__(self, light, host, name):
        self._light = light
        self._host = host
        self._port = 8900
        self._name = name
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._supported_features = SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_EFFECT
        self._effect_list = light.effects
        self._effect = None
        self._on = False
        self._brightness = 255
        self._hs_color = None

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._on

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

    async def async_turn_on(self, **kwargs):
        hs_color = kwargs.get(ATTR_HS_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        effect = kwargs.get(ATTR_EFFECT)

        rgb = color_util.color_hs_to_RGB(*hs_color) if hs_color else None

        if rgb:
            self._hs_color = hs_color
            self._light.colour = rgb

        if effect:
            self._effect = effect
            self._light.effect = effect

        if brightness:
            self._brightness = brightness

        self._light.on = int(self._brightness / 2.55)
        self._on = True

    async def async_turn_off(self, **kwargs):
        self._light.on = 0
        self._on = False


class PyCololight:
    COMMAND_PREFIX = "535a30300000000000"
    COMMAND_CONFIG = "20000000000000000000000000000000000100000000000000000004010301c"
    COMMAND_EFFECT = "23000000000000000000000000000000000100000000000000000004010602ff"

    def __init__(self, host, port=8900):
        self.host = host
        self.port = port
        self._on = False
        self._brightness = None
        self._colour = None
        self._effect = None
        self._effects = {
            "80s Club": "049a0000",
            "Cherry Blossom": "04940800",
            "Cocktail Parade": "05bd0690",
            "Instagrammer": "03bc0190",
            "Pensieve": "04c40600",
            "Savasana": "04970400",
            "Sunrise": "01c10a00",
            "The Circus": "04810130",
            "Unicorns": "049a0e00",
            "Christmas": "068b0900",
            "Rainbow Flow": "03810690",
            "Music Mode": "07bd0990",
        }
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, command):
        self._sock.sendto(command, (self.host, self.port))

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, brightness):
        if brightness:
            self._on = True
            self.brightness = brightness
        else:
            self._on = False
            command = bytes.fromhex(
                "{}{}{}".format(self.COMMAND_PREFIX, self.COMMAND_CONFIG, "e1e")
            )
            self._send(command)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        brightness_prefix = "f"
        command = bytes.fromhex(
            "{}{}{}{:02x}".format(
                self.COMMAND_PREFIX,
                self.COMMAND_CONFIG,
                brightness_prefix,
                int(brightness),
            )
        )
        self._brightness = brightness
        self._send(command)

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, colour):
        colour_prefix = "00"
        command = bytes.fromhex(
            "{}{}{}{:02x}{:02x}{:02x}".format(
                self.COMMAND_PREFIX, self.COMMAND_EFFECT, colour_prefix, *colour
            )
        )
        self._colour = colour
        self._send(command)

    @property
    def effect(self):
        return self._effect

    @effect.setter
    def effect(self, effect):
        command = bytes.fromhex(
            "{}{}{}".format(
                self.COMMAND_PREFIX, self.COMMAND_EFFECT, self._effects[effect],
            )
        )
        self._effect = effect
        self._send(command)

    @property
    def effects(self):
        return list(self._effects.keys())
