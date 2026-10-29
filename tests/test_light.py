import pytest
import logging
import threading

from unittest.mock import patch
from pycololight import PyCololight, UnavailableException

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
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
from homeassistant.util.dt import utcnow

from custom_components.cololight.light import SCAN_INTERVAL

LIGHT_1_NAME = "cololight_test"
LIGHT_1_HOST = "1.1.1.1"
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
            "host": LIGHT_1_HOST,
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


@patch("custom_components.cololight.light.PyCololight._send")
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
    assert state.attributes.get("color_mode") == "hs"
    assert state.attributes.get(ATTR_BRIGHTNESS) == 255


@patch("custom_components.cololight.light.PyCololight._send")
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
    assert state.attributes.get("color_mode") == "hs"
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60


@patch("custom_components.cololight.light.PyCololight._send")
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
    assert state.attributes.get("color_mode") == "brightness"
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60
    assert state.attributes.get(ATTR_EFFECT) == "Sunrise"


@patch("custom_components.cololight.light.PyCololight._send")
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
    assert state.attributes.get("color_mode") == "hs"
    assert state.attributes.get(ATTR_BRIGHTNESS) == 60
    assert state.attributes.get(ATTR_HS_COLOR) == (300, 50)


@patch("custom_components.cololight.light.PyCololight._send")
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


@patch("custom_components.cololight.light.PyCololight._send")
async def test_commands_are_not_sent_from_the_event_loop(mock_send, hass):
    sending_threads = []
    mock_send.side_effect = lambda *args, **kwargs: sending_threads.append(
        threading.get_ident()
    )

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT, ATTR_HS_COLOR: (300, 50)},
        blocking=True,
    )
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT},
        blocking=True,
    )

    assert len(sending_threads) == 3
    assert threading.get_ident() not in sending_threads


async def poll(hass):
    async_fire_time_changed(hass, utcnow() + SCAN_INTERVAL)
    # Home Assistant polls in background tasks, which a plain block_till_done skips.
    await hass.async_block_till_done(wait_background_tasks=True)


def logged_exception_types(caplog):
    return [
        record.exc_info[0]
        for record in caplog.records
        if record.name == "custom_components.cololight.light"
        and record.levelno == logging.ERROR
        and record.exc_info
    ]


@pytest.mark.parametrize("service", [SERVICE_TURN_ON, SERVICE_TURN_OFF])
@patch("custom_components.cololight.light.PyCololight._send")
async def test_poll_straight_after_a_command_is_skipped(mock_send, service, hass):
    polled_hosts = []
    record_poll = property(lambda light: polled_hosts.append(light.host))

    with patch.object(PyCololight, "state", record_poll):
        await hass.services.async_call(
            LIGHT_DOMAIN,
            service,
            {ATTR_ENTITY_ID: ENTITY_1_LIGHT},
            blocking=True,
        )
        assert LIGHT_1_HOST not in polled_hosts

        await poll(hass)
        assert LIGHT_1_HOST in polled_hosts


@patch("custom_components.cololight.light.PyCololight._send")
async def test_light_is_unavailable_when_a_poll_times_out(mock_send, hass):
    with patch(
        "custom_components.cololight.light.PyCololight._receive",
        side_effect=UnavailableException,
    ):
        await poll(hass)

    assert hass.states.get(ENTITY_1_LIGHT).state == STATE_UNAVAILABLE


@patch("custom_components.cololight.light.PyCololight._send")
async def test_light_is_available_again_when_it_replies(mock_send, hass):
    # pycololight reads byte 40 as on (207) or off (206), and byte 41 as brightness.
    on_reply = bytes(40) + bytes([207, 100])

    with patch(
        "custom_components.cololight.light.PyCololight._receive",
        side_effect=UnavailableException,
    ):
        await poll(hass)
    assert hass.states.get(ENTITY_1_LIGHT).state == STATE_UNAVAILABLE

    with patch(
        "custom_components.cololight.light.PyCololight._receive",
        return_value=on_reply,
    ):
        await poll(hass)

    assert hass.states.get(ENTITY_1_LIGHT).state == STATE_ON


@patch("custom_components.cololight.light.PyCololight._send")
async def test_unexpected_poll_error_makes_light_unavailable_and_logs_traceback(
    mock_send, hass, caplog
):
    with patch(
        "custom_components.cololight.light.PyCololight._receive",
        side_effect=RuntimeError,
    ):
        await poll(hass)

    assert hass.states.get(ENTITY_1_LIGHT).state == STATE_UNAVAILABLE
    assert RuntimeError in logged_exception_types(caplog)


@patch("custom_components.cololight.light.PyCololight._send")
async def test_poll_error_traceback_is_not_logged_again_while_unavailable(
    mock_send, hass, caplog
):
    with patch(
        "custom_components.cololight.light.PyCololight._receive",
        side_effect=RuntimeError,
    ) as mock_receive:
        await poll(hass)
        caplog.clear()
        receives_before = mock_receive.call_count

        await poll(hass)

    assert mock_receive.call_count > receives_before
    assert logged_exception_types(caplog) == []


class FakeDevice:
    """Replies to state queries with the last brightness it was sent."""

    def __init__(self):
        self.brightness = 100

    def send(self, commands, response=False):
        for command in commands:
            # pycololight sends brightness as 0xcf then the 0-100 value, and reads the
            # state reply's bytes 40-41 in the same form.
            if command[-2] == 0xCF:
                self.brightness = command[-1]

    def receive(self):
        return bytes(40) + bytes([0xCF, self.brightness])


@pytest.fixture
def fake_device():
    device = FakeDevice()
    with (
        patch(
            "custom_components.cololight.light.PyCololight._send",
            side_effect=device.send,
        ),
        patch(
            "custom_components.cololight.light.PyCololight._receive",
            side_effect=device.receive,
        ),
    ):
        yield device


async def test_brightness_set_from_home_assistant_is_kept_by_the_next_poll(
    fake_device, hass
):
    drifted = []
    for brightness in range(1, 256):
        await hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: ENTITY_1_LIGHT, ATTR_BRIGHTNESS: brightness},
            blocking=True,
        )
        await poll(hass)
        polled = hass.states.get(ENTITY_1_LIGHT).attributes.get(ATTR_BRIGHTNESS)
        if polled != brightness:
            drifted.append(brightness)

    assert drifted == []


async def test_brightness_changed_outside_home_assistant_shows_on_the_next_poll(
    fake_device, hass
):
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: ENTITY_1_LIGHT, ATTR_BRIGHTNESS: 60},
        blocking=True,
    )
    fake_device.brightness = 100

    await poll(hass)

    assert hass.states.get(ENTITY_1_LIGHT).attributes.get(ATTR_BRIGHTNESS) == 255


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
