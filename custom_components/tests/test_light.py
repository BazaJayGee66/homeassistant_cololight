import pytest
import socket
import sys

import cololight

from unittest.mock import patch, call

# Link to homeassistant module
sys.path.insert(1, "/homeassistant/core")
from tests.conftest import hass, hass_storage
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.setup import async_setup_component

CONF_NAME = "cololight_test"
ENTITY_LIGHT = f"light.{CONF_NAME}"


@pytest.fixture(autouse=True)
@patch("socket.socket")
def setup_comp(mock_socket, hass):
    """Set up cololight component."""
    hass.loop.run_until_complete(
        async_setup_component(
            hass,
            LIGHT_DOMAIN,
            {
                LIGHT_DOMAIN: {
                    "platform": "cololight",
                    "name": CONF_NAME,
                    "host": "1.1.1.1",
                }
            },
        )
    )


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on(mock_send, hass):
    """Test the light turns of successfully."""

    await hass.services.async_call(
        LIGHT_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: ENTITY_LIGHT}, blocking=True,
    )

    state = hass.states.get(ENTITY_LIGHT)

    mock_send.assert_called_with(
        b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcfd"
    )
    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 255


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on_with_brightness(mock_send, hass):
    """Test the light turns on to the specified brightness."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_LIGHT, ATTR_BRIGHTNESS: 60},
        blocking=True,
    )

    state = hass.states.get(ENTITY_LIGHT)

    mock_send.assert_called_with(
        b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf\x17"
    )
    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on_with_effect(mock_send, hass):
    """Test the light turns on with effect."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_LIGHT, ATTR_EFFECT: "Sunrise", ATTR_BRIGHTNESS: 60},
        blocking=True,
    )

    state = hass.states.get(ENTITY_LIGHT)

    expected_messages = [
        call(
            b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x01\xc1\n\x00"
        ),
        call(
            b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf\x17"
        ),
    ]

    mock_send.assert_has_calls(expected_messages)
    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60
    assert state.attributes.get(ATTR_EFFECT) == "Sunrise"


@patch("homeassistant.components.cololight.light.PyCololight._send")
async def test_turn_on_with_colour(mock_send, hass):
    """Test the light turns on with colour."""

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_LIGHT, ATTR_HS_COLOR: (300, 50), ATTR_BRIGHTNESS: 60},
        blocking=True,
    )

    state = hass.states.get(ENTITY_LIGHT)

    expected_messages = [
        call(
            b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x00\xff\x7f\xff"
        ),
        call(
            b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf\x17"
        ),
    ]
    mock_send.assert_has_calls(expected_messages)
    assert mock_send.call_count == 2

    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60
    assert state.attributes.get(ATTR_HS_COLOR) == (300, 50)


@patch("homeassistant.components.cololight.light.coloLight.send_message")
async def test_turn_off(mock_sending, hass):
    """Test the light turns off successfully."""

    await hass.services.async_call(
        LIGHT_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: ENTITY_LIGHT}, blocking=True,
    )

    state = hass.states.get(ENTITY_LIGHT)

    mock_sending.assert_called_with(
        b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xce\x1e"
    )
    assert state.state == STATE_OFF
