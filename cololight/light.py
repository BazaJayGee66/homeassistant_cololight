"""Platform for ColoLight integration."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    PLATFORM_SCHEMA, SUPPORT_COLOR, SUPPORT_BRIGHTNESS, SUPPORT_EFFECT, ATTR_HS_COLOR, ATTR_BRIGHTNESS, ATTR_EFFECT, Light)
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.util.color as color_util

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'ColoLight'

MESSAGE_PREFIX          = "535a30300000000000"
MESSAGE_COMMAND_CONFIG  = "200000000000000000000000000000000001000000000000000000"
MESSAGE_COMMAND_COLOR   = "23000000000000000000000000000000000100000000000000000004010602ff"


COLOLIGHT_EFFECT_LIST = ["80s Club",
            "Cherry Blossom",
            "Cocktail Parade",
            "Savasana",
            "Sunrise",
            "Unicorns",
            "Pensieve",
            "The Circus",
            "Instargrammer"]

COLOLIGHT_EFFECT_MAPPING = {"80s Club": "049a0000",
            "Cherry Blossom": "04940800",
            "Cocktail Parade": "05bd0690",
            "Savasana": "04970400",
            "Sunrise": "01c10a00",
            "Unicorns": "049a0e00",
            "Pensieve": "04c40600",
            "The Circus": "04810130",
            "Instargrammer": "03bc0190"}

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config[CONF_HOST]
    name = config[CONF_NAME]
    add_entities([ColoLight(host, name)])


class ColoLight(Light):

    def __init__(self, host, name):

        import socket
        self._host = host
        self._port = 8900
        self._name = name
        self._sock =  socket.socket(socket.AF_INET, # Internet
                                    socket.SOCK_DGRAM) # UDP
        self._supported_features = SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_EFFECT
        self._effect_list = COLOLIGHT_EFFECT_LIST
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
    def brightness(self) -> int:
        return self._brightness

    @property
    def hs_color(self) -> tuple:
        return self._hs


    def turn_on(self, **kwargs):
        hs_color = kwargs.get(ATTR_HS_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        effect = kwargs.get(ATTR_EFFECT)
        rgb = color_util.color_hs_to_RGB(*hs_color) if hs_color else None
        if rgb:
            self._hs = hs_color
            self._sock.sendto(bytes.fromhex("%s%s00%s" % (MESSAGE_PREFIX, MESSAGE_COMMAND_COLOR, '{:02x}{:02x}{:02x}'.format(*rgb))), (self._host, self._port))
        if effect:
            self._sock.sendto(bytes.fromhex("%s%s%s" % (MESSAGE_PREFIX, MESSAGE_COMMAND_COLOR, COLOLIGHT_EFFECT_MAPPING[effect])), (self._host, self._port))
        if brightness:
            self._brightness = brightness
        brightness = (self._brightness / 255)*100
        self._sock.sendto(bytes.fromhex("%s%s04010301cf%s" % (MESSAGE_PREFIX, MESSAGE_COMMAND_CONFIG, '{:02x}'.format(int(brightness)))), (self._host, self._port))
        self._on = True

    def turn_off(self, **kwargs):
        self._sock.sendto(bytes.fromhex("%s%s04010301ce1e" % (MESSAGE_PREFIX, MESSAGE_COMMAND_CONFIG)), (self._host, self._port))
        self._on = False

