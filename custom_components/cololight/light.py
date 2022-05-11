"""Platform for LifeSmart ColoLight Light integration."""
import logging
import voluptuous as vol
import socket
from datetime import timedelta

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
# H-A .110 and later
try:
    from homeassistant.components.light import (
        PLATFORM_SCHEMA,
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
        PLATFORM_SCHEMA,
        SUPPORT_COLOR,
        SUPPORT_BRIGHTNESS,
        SUPPORT_EFFECT,
        ATTR_HS_COLOR,
        ATTR_BRIGHTNESS,
        ATTR_EFFECT,
        Light,
    )

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_MODE, STATE_ON
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.color as color_util

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "ColoLight"

ICON = "mdi:hexagon-multiple"

SCAN_INTERVAL = timedelta(seconds=30)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional("custom_effects", default=[]): vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_NAME): cv.string,
                        vol.Required("color_scheme"): cv.string,
                        vol.Required("color"): cv.string,
                        vol.Required("cycle_speed"): cv.positive_int,
                        vol.Required(CONF_MODE): cv.positive_int,
                    }
                )
            ],
        ),
        vol.Optional("default_effects"): cv.ensure_list,
    }
)


async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if entry.data.get("default_effects"):
        cololight_light = PyCololight(host, default_effects=False)
        try:
            cololight_light.include_default_effects(entry.data["default_effects"])
        except DefaultEffectExecption:
            _LOGGER.error(
                "Invalid default effect given in default effects '%s'. "
                "Valid default effects include: %s",
                entry.data["default_effects"],
                cololight_light.default_effects,
            )
    else:
        cololight_light = PyCololight(host)

    if entry.options:
        for effect_name, effect_options in entry.options.items():
            if effect_name not in ["default_effects", "restored_effects"]:
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


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    current_entries = hass.config_entries.async_entries(DOMAIN)
    entries_by_name = {entry.data[CONF_NAME]: entry for entry in current_entries}
    name = config[CONF_NAME]
    if name in entries_by_name and entries_by_name[name].source == SOURCE_IMPORT:
        entry = entries_by_name[name]
        data = config.copy()
        options = dict(entry.options)
        for custom_effect in data["custom_effects"]:
            options[custom_effect[CONF_NAME]] = custom_effect

        hass.config_entries.async_update_entry(entry, data=data, options=options)

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config)
        )
    )


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
        self._canUpdate = True

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return ICON

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
            try:
                self._light.state
                self._on = self._light.on
                if self._on:
                    self._brightness = round(self._light.brightness * 2.55)

            except:
                _LOGGER.error("Error with update status of Cololight")
        else:
            self._canUpdate = True


class ColourSchemeException(Exception):
    pass


class ColourException(Exception):
    pass


class CycleSpeedException(Exception):
    pass


class ModeExecption(Exception):
    pass


class DefaultEffectExecption(Exception):
    pass


class PyCololight:
    COMMAND_PREFIX = "535a30300000000000"
    CUSTOM_EFFECT_COLOURS = {
        "Breath": {
            "decimal": 128,
            "colours": (
                "Red, Green, Blue",
                "Rainbow",
                "Green",
                "Azure",
                "Blue",
                "Purple",
                "Red",
                "Orange",
                "Yellow",
                "White",
                "Green, Blue",
            ),
        },
        "Shadow": {
            "decimal": 138,
            "colours": (
                "Red, Yellow",
                "Red, Green",
                "Red, Purple",
                "Red, Blue",
                "Green, Yellow",
                "Green, Azure",
                "Green, Blue",
                "Blue, Azure",
                "Blue, Purple",
                "Yellow, White",
                "Red, White",
                "Green, White",
                "Azure, White",
                "Blue, White",
                "Purple, White",
            ),
        },
        "Flash": {
            "decimal": 153,
            "colours": (
                "Red, Green, Blue",
                "Rainbow",
                "Green",
                "Azure",
                "Blue",
                "Purple",
                "Red",
                "Orange",
                "Yellow",
                "White",
            ),
        },
        "Flicker": {
            "decimal": 163,
            "colours": (
                "Red, Green, Blue",
                "Rainbow",
                "Green",
                "Azure",
                "Blue",
                "Purple",
                "Red",
                "Orange",
                "Yellow",
                "White",
            ),
        },
        "Scene": {
            "decimal": 173,
            "colours": (
                "Birthday",
                "Girlfriends",
                "Friends",
                "Workmates",
                "Family",
                "Lover",
            ),
        },
        "Mood": {
            "decimal": 179,
            "colours": (
                "Red",
                "Orange",
                "Yellow",
                "Green",
                "Grass",
                "Azure",
                "Blue",
                "Pink",
                "Gold",
                "Color",
                "True Color",
            ),
        },
        "Selected": {
            "decimal": 191,
            "colours": ("Savasana", "", "Sunrise", "", "Unicorns"),
        },
    }
    CUSTOM_EFFECT_MODES = [
        ("01", "00"),
        ("02", "00"),
        ("05", "10"),
        ("05", "30"),
        ("05", "40"),
        ("05", "50"),
        ("05", "70"),
        ("05", "80"),
        ("05", "90"),
        ("05", "a0"),
        ("05", "b0"),
        ("05", "c0"),
        ("05", "00"),
        ("05", "20"),
        ("05", "30"),
        ("06", "00"),
        ("06", "10"),
        ("06", "20"),
        ("06", "30"),
        ("06", "50"),
        ("05", "f0"),
        ("05", "10"),
        ("05", "40"),
        ("05", "50"),
        ("06", "60"),
        ("06", "70"),
        ("06", "80"),
    ]

    DEFAULT_EFFECTS = {
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

    def __init__(self, host, port=8900, default_effects=True):
        self.host = host
        self.port = port
        self._count = 1
        self._on = False
        self._brightness = None
        self._colour = None
        self._effect = None
        self._effects = self.DEFAULT_EFFECTS.copy() if default_effects else {}
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _switch_count(self):
        if self._count == 1:
            self._count = 2
        else:
            self._count = 1

    def _send(self, command):
        self._sock.sendto(command, (self.host, self.port))

    def _receive(self):
        data = self._sock.recvfrom(4096)[0]
        return data

    def _get_config(self, config_type):
        if config_type == "command":
            command_config = f"20000000000000000000000000000000000{self.count}00000000000000000004010301c"
            return command_config
        elif config_type == "effect":
            effect_config = f"23000000000000000000000000000000000{self.count}00000000000000000004010602ff"
            return effect_config

    def _cycle_speed_hex(self, cycle_speed, mode):
        if not 1 <= cycle_speed <= 32:
            raise CycleSpeedException
        if mode in [2]:
            # Mode 2 only has speeds 1, 2, 3, which are mapped differently to other modes
            cycle_speed_values = [3, 11, 19]
            cycle_speed_value = cycle_speed_values[min(3, cycle_speed) - 1]
        else:
            cycle_speed_value = list(reversed(range(33)))[cycle_speed - 1]

        cycle_speed_hex = "{:02x}".format(cycle_speed_value)
        return cycle_speed_hex

    def _colour_hex(self, colour_scheme, colour, mode):
        if colour_scheme not in self.custom_effect_colour_schemes():
            raise ColourSchemeException
        if colour not in self.custom_effect_colour_scheme_colours(colour_scheme):
            raise ColourException

        starting_decimal = self.CUSTOM_EFFECT_COLOURS[colour_scheme]["decimal"]
        colour_key = self.CUSTOM_EFFECT_COLOURS[colour_scheme]["colours"].index(colour)
        if mode in [13, 14, 15, 22, 23, 24]:
            # These modes have a lower starting decimal of 128
            starting_decimal = starting_decimal - 128
        colour_decimal = starting_decimal + colour_key
        colour_hex = "{:02x}".format(colour_decimal)
        return colour_hex

    def _mode_hex(self, mode):
        if not 1 <= mode <= len(self.CUSTOM_EFFECT_MODES):
            raise ModeExecption

        return self.CUSTOM_EFFECT_MODES[mode - 1]

    @property
    def count(self):
        count = self._count
        self._switch_count()
        return count

    @property
    def state(self):
        self._send(
            bytes.fromhex(
                "535a303000000000001e000000000000000000000000000000000200000000000000000003020101"
            )
        )
        data = self._receive()
        if not data:
            return  # return if timeout occurs
        if data[40] == 207:  # 0xcf
            self._on = True
            self._brightness = data[41]
        elif data[40] == 206:  # 0xce
            self._on = False
        else:
            return  # if value is not 0xcf(on) or 0xce(off) stop the update then dont change anything. Because cololight will sometimes return a random data.

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
                "{}{}{}".format(self.COMMAND_PREFIX, self._get_config("command"), "e1e")
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
                self._get_config("command"),
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
                self.COMMAND_PREFIX, self._get_config("effect"), colour_prefix, *colour
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
                self.COMMAND_PREFIX,
                self._get_config("effect"),
                self._effects[effect],
            )
        )
        self._effect = effect
        self._send(command)

    @property
    def default_effects(self):
        return list(self.DEFAULT_EFFECTS.keys())

    @property
    def effects(self):
        return list(self._effects.keys())

    def include_default_effects(self, effects):
        for effect in effects:
            if effect not in self.DEFAULT_EFFECTS:
                raise DefaultEffectExecption

            self._effects[effect] = self.DEFAULT_EFFECTS[effect]

    def add_custom_effect(self, name, colour_scheme, colour, cycle_speed, mode):
        cycle_speed_hex = self._cycle_speed_hex(int(cycle_speed), int(mode))
        colour_hex = self._colour_hex(colour_scheme, colour, int(mode))
        mode_hex = self._mode_hex(int(mode))

        if mode in [2]:
            # Mode 2 has bytes arranged differently to other modes
            custom_effect_hex = (
                f"{mode_hex[0]}{cycle_speed_hex}{colour_hex}{mode_hex[1]}"
            )
        else:
            custom_effect_hex = (
                f"{mode_hex[0]}{colour_hex}{cycle_speed_hex}{mode_hex[1]}"
            )

        self._effects[name] = custom_effect_hex

    def custom_effect_colour_schemes(self):
        return list(self.CUSTOM_EFFECT_COLOURS.keys())

    def custom_effect_colour_scheme_colours(self, colour_scheme):
        return list(filter(None, self.CUSTOM_EFFECT_COLOURS[colour_scheme]["colours"]))
