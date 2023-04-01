import pytest

from datetime import timedelta
from unittest.mock import patch

from pycololight import UnavailableException

from tests.conftest import hass, hass_storage, load_registries, hass_fixture_setup
from tests.common import MockConfigEntry, async_fire_time_changed
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ATTR_EFFECT_LIST,
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.setup import async_setup_component
from homeassistant.util.dt import utcnow

LIGHT_1_NAME = "cololight_test"
ENTITY_1_LIGHT = f"light.{LIGHT_1_NAME}"
LIGHT_2_NAME = "cololight_custom_effect"
ENTITY_2_LIGHT = f"light.{LIGHT_2_NAME}"
LIGHT_3_NAME = "cololight_incorrect_custom_effect"
ENTITY_3_LIGHT = f"light.{LIGHT_3_NAME}"
LIGHT_4_NAME = "cololight_exclude_default_efects"
ENTITY_4_LIGHT = f"light.{LIGHT_4_NAME}"
LIGHT_6_NAME = "cololight_test_strip"
ENTITY_6_LIGHT = f"light.{LIGHT_6_NAME}"


@pytest.fixture(autouse=True)
async def setup_comp(hass):
    """Set up cololight component."""
    entry_1 = MockConfigEntry(
        domain="cololight",
        data={
            "platform": "cololight",
            "name": LIGHT_1_NAME,
            "host": "1.1.1.1",
            "device": "hexagon",
            "default_effects": [
                "Pensieve",
                "Savasana",
                "Sunrise",
            ],
        },
        options={},
    )
    entry_1.add_to_hass(hass)
    await hass.config_entries.async_setup(entry_1.entry_id)

    entry_2 = MockConfigEntry(
        domain="cololight",
        data={
            "platform": "cololight",
            "name": LIGHT_2_NAME,
            "host": "1.1.1.2",
            "device": "hexagon",
            "default_effects": [
                "Unicorns",
                "Rainbow Flow",
                "Music Mode",
            ],
        },
        options={
            "Test Effect": {
                "name": "Test Effect",
                "color_scheme": "Mood",
                "color": "Green",
                "cycle_speed": 1,
                "mode": 1,
            }
        },
    )
    entry_2.add_to_hass(hass)
    await hass.config_entries.async_setup(entry_2.entry_id)

    entry_3 = MockConfigEntry(
        domain="cololight",
        data={
            "platform": "cololight",
            "name": LIGHT_3_NAME,
            "host": "1.1.1.3",
            "device": "hexagon",
            "default_effects": [
                "80s Club",
                "Cherry Blossom",
            ],
        },
        options={
            "Bad Effect": {
                "name": "Bad Effect",
                "color_scheme": "Bad",
                "color": "Green",
                "cycle_speed": 1,
                "mode": 1,
            },
            "Good Effect": {
                "name": "Good Effect",
                "color_scheme": "Mood",
                "color": "Green",
                "cycle_speed": 1,
                "mode": 1,
            },
        },
    )
    entry_3.add_to_hass(hass)
    await hass.config_entries.async_setup(entry_3.entry_id)

    entry_4 = MockConfigEntry(
        domain="cololight",
        data={
            "platform": "cololight",
            "name": LIGHT_4_NAME,
            "host": "1.1.1.4",
            "device": "hexagon",
            "default_effects": [
                "80s Club",
            ],
        },
        options={
            "Custom Effect": {
                "name": "Custom Effect",
                "color_scheme": "Mood",
                "color": "Green",
                "cycle_speed": 1,
                "mode": 1,
            },
        },
    )
    entry_4.add_to_hass(hass)
    await hass.config_entries.async_setup(entry_4.entry_id)

    entry_6 = MockConfigEntry(
        domain="cololight",
        data={
            "platform": "cololight",
            "name": LIGHT_6_NAME,
            "host": "1.1.1.6",
            "device": "strip",
            "default_effects": [],
        },
        options={},
    )
    entry_6.add_to_hass(hass)
    await hass.config_entries.async_setup(entry_6.entry_id)

    await hass.async_block_till_done()
    return


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on(mock_send, hass):
    """Test the light turns of successfully."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT},
        blocking=True,
    )

    state = hass.states.get(ENTITY_1_LIGHT)

    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 255


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on_with_brightness(mock_send, hass):
    """Test the light turns on to the specified brightness."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT, ATTR_BRIGHTNESS: 60},
        blocking=True,
    )

    state = hass.states.get(ENTITY_1_LIGHT)

    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on_with_effect(mock_send, hass):
    """Test the light turns on with effect."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT, ATTR_EFFECT: "Sunrise", ATTR_BRIGHTNESS: 60},
        blocking=True,
    )

    state = hass.states.get(ENTITY_1_LIGHT)

    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60
    assert state.attributes.get(ATTR_EFFECT) == "Sunrise"


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on_with_colour(mock_send, hass):
    """Test the light turns on with colour."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT, ATTR_HS_COLOR: (300, 50), ATTR_BRIGHTNESS: 60},
        blocking=True,
    )

    state = hass.states.get(ENTITY_1_LIGHT)

    assert mock_send.call_count == 2

    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60
    assert state.attributes.get(ATTR_HS_COLOR) == (300, 50)


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_off(mock_send, hass):
    """Test the light turns off successfully."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT},
        blocking=True,
    )

    state = hass.states.get(ENTITY_1_LIGHT)

    assert state.state == STATE_OFF


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_availability(mock_send, hass):
    """Test the light becomes unavailable when cant be reached."""

    with patch(
        "homeassistant.components.cololight.light.PyCololight._receive",
        side_effect=UnavailableException(),
    ):
        future = utcnow() + timedelta(minutes=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

        future = utcnow() + timedelta(minutes=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

        state = hass.states.get(ENTITY_1_LIGHT)
        assert state.state == STATE_UNAVAILABLE

    with patch("homeassistant.components.cololight.light.PyCololight._receive"):
        future = utcnow() + timedelta(minutes=1)
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

        state = hass.states.get(ENTITY_1_LIGHT)
        assert state.state != STATE_UNAVAILABLE


async def test_light_has_effects(hass):
    state = hass.states.get(ENTITY_1_LIGHT)

    expected_efects_list = [
        "Pensieve",
        "Savasana",
        "Sunrise",
    ]

    assert state.attributes.get(ATTR_EFFECT_LIST) == expected_efects_list


async def test_light_adds_custom_effect(hass):
    state = hass.states.get(ENTITY_2_LIGHT)

    expected_efects_list = [
        "Unicorns",
        "Rainbow Flow",
        "Music Mode",
        "Test Effect",
    ]

    assert state.attributes.get(ATTR_EFFECT_LIST) == expected_efects_list


async def test_light_handles_incorrect_custom_effect(hass):
    state = hass.states.get(ENTITY_3_LIGHT)

    expected_efects_list = [
        "80s Club",
        "Cherry Blossom",
        "Good Effect",
    ]

    assert state.attributes.get(ATTR_EFFECT_LIST) == expected_efects_list


async def test_light_has_only_specified_default_effects(hass):
    state = hass.states.get(ENTITY_4_LIGHT)

    expected_efects_list = ["80s Club", "Custom Effect"]

    assert state.attributes.get(ATTR_EFFECT_LIST) == expected_efects_list


async def test_icon(hass):
    state_hexagon = hass.states.get(ENTITY_1_LIGHT)
    state_strip = hass.states.get(ENTITY_6_LIGHT)

    assert state_hexagon.attributes.get("icon") == "mdi:hexagon-multiple"
    assert state_strip.attributes.get("icon") == "mdi:led-strip-variant"
