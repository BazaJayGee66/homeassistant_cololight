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

MESSAGE_PREFIX = "535a30300000000000"
MESSAGE_COMMAND_CONFIG = "200000000000000000000000000000000001000000000000000000"
MESSAGE_COMMAND_COLOR = (
    "23000000000000000000000000000000000100000000000000000004010602ff00"
)
MESSAGE_COMMAND_EFFECT = (
    "23000000000000000000000000000000000100000000000000000004010602ff"
)
MESSAGE_BRIGHTNESS = "04010301cf"
MESSAGE_OFF = "04010301ce1e"

COLOLIGHT_EFFECT_LIST = [
    "80s Club",
    "Cherry Blossom",
    "Cocktail Parade",
    "Instagrammer",
    "Pensieve",
    "Savasana",
    "Sunrise",
    "The Circus",
    "Unicorns",
    "Christmas",
    "Rainbow Flow",
    "Music Mode",
]

COLOLIGHT_EFFECT_MAPPING = {
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
        self._effect_list = COLOLIGHT_EFFECT_LIST
        self._effect = None
        self._on = False
        self._brightness = 255
        self._hs = None

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
        return self._hs

    def send_message(self, message):
        self._sock.sendto(message, (self._host, self._port))

    async def async_turn_on(self, **kwargs):
        hs_color = kwargs.get(ATTR_HS_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        effect = kwargs.get(ATTR_EFFECT)

        rgb = color_util.color_hs_to_RGB(*hs_color) if hs_color else None

        if rgb:
            self._hs = hs_color
            self.send_message(
                bytes.fromhex(
                    "{}{}{:02x}{:02x}{:02x}".format(
                        MESSAGE_PREFIX, MESSAGE_COMMAND_COLOR, *rgb
                    )
                )
            )

        if effect:
            self._effect = effect
            self._light.effect = effect

        if brightness:
            self._brightness = brightness

        brightness = (self._brightness / 255) * 100

        self.send_message(
            bytes.fromhex(
                "{}{}{}{:02x}".format(
                    MESSAGE_PREFIX,
                    MESSAGE_COMMAND_CONFIG,
                    MESSAGE_BRIGHTNESS,
                    int(brightness),
                )
            )
        )
        self._on = True

    async def async_turn_off(self, **kwargs):
        self.send_message(
            bytes.fromhex(
                "{}{}{}".format(MESSAGE_PREFIX, MESSAGE_COMMAND_CONFIG, MESSAGE_OFF)
            )
        )
        self._on = False


class PyCololight:
    def __init__(self, host, port=8900):
        self.host = host
        self.port = port
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
    def effect(self):
        return self._effect

    @effect.setter
    def effect(self, effect):
        command = bytes.fromhex(
            "{}{}{}".format(
                MESSAGE_PREFIX, MESSAGE_COMMAND_EFFECT, self._effects[effect],
            )
        )
        self._effect = effect
        self._send(command)

    @property
    def effects(self):
        return list(self._effects.keys())
