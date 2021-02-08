import sys

import cololight

from unittest.mock import patch

from tests.conftest import hass, hass_storage
from tests.common import MockConfigEntry

from homeassistant import data_entry_flow


NAME = "cololight_test"
HOST = "1.1.1.1"

DEMO_USER_INPUT = {
    "name": NAME,
    "host": HOST,
}


async def test_form(hass):
    """Test config entry configured successfully."""

    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=DEMO_USER_INPUT
    )

    assert result["type"] == "create_entry"
    assert result["title"] == NAME
    assert result["data"] == DEMO_USER_INPUT


async def test_form_already_configured(hass):
    """Test host is already configured."""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=DEMO_USER_INPUT, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN,
        context={"source": "user"},
        data=DEMO_USER_INPUT,
    )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"


@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_color_schemes",
    return_value=["Mood | Green", "Mood | Red"],
)
async def test_options_creating_effect(mock_color_schemes, hass):
    """Test options for create effect"""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=DEMO_USER_INPUT, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"select": "Create"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "options_add_custom_effect"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": "test",
            "color_scheme": "Mood | Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {
        "test": {
            "color_scheme": "Mood",
            "color": "Green",
            "cycle_speed": 1,
            "mode": 1,
        }
    }

    result = await hass.config_entries.options.async_init(entry.entry_id)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"select": "Create"}
    )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": "test_2",
            "color_scheme": "Mood | Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    )

    assert result["data"] == {
        "test": {
            "color_scheme": "Mood",
            "color": "Green",
            "cycle_speed": 1,
            "mode": 1,
        },
        "test_2": {
            "color_scheme": "Mood",
            "color": "Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    }


@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_color_schemes",
    return_value=["Mood | Green", "Mood | Red"],
)
async def test_options_updating_effect(mock_scheme_colors, hass):
    """Test options for create effect is updated if already existing"""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=DEMO_USER_INPUT, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"select": "Create"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": "test",
            "color_scheme": "Mood | Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    )
    assert result["data"] == {
        "test": {
            "color_scheme": "Mood",
            "color": "Green",
            "cycle_speed": 1,
            "mode": 1,
        }
    }

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"select": "Create"}
    )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": "test",
            "color_scheme": "Mood | Red",
            "cycle_speed": 1,
            "mode": 1,
        },
    )

    assert result["data"] == {
        "test": {
            "color_scheme": "Mood",
            "color": "Red",
            "cycle_speed": 1,
            "mode": 1,
        }
    }


async def test_options_deleting_effect(hass):
    """Test options for deleting effect"""
    test_effects = {
        "test": {"color_scheme": "Mood", "color": "Green", "cycle_speed": 1, "mode": 1},
        "test_2": {
            "color_scheme": "Mood",
            "color": "Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    }

    expected_effetcs = {
        "test": {"color_scheme": "Mood", "color": "Green", "cycle_speed": 1, "mode": 1},
    }

    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=DEMO_USER_INPUT, unique_id=HOST
    )
    entry.add_to_hass(hass)

    entry.options = test_effects

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"select": "Delete"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "options_delete_custom_effect"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": ["test_2"],
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert entry.options == expected_effetcs


@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_color_schemes",
    return_value=["Mood | Green"],
)
async def test_options_has_error_if_invalid(mock_color_schemes, hass):
    """Test options will show error if invalid"""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=DEMO_USER_INPUT, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"select": "Create"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "options_add_custom_effect"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": "test",
            "color_scheme": "Mood | Green",
            "cycle_speed": 50,
            "mode": 1,
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"cycle_speed": "invalid_cycle_speed"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": "test",
            "color_scheme": "Mood | Green",
            "cycle_speed": 1,
            "mode": 50,
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"mode": "invalid_mode"}


async def test_end_to_end_with_options(hass):
    """Test an end to end flow, creating entity and add effects"""
    flow = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input=DEMO_USER_INPUT
    )

    await hass.async_block_till_done()

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"select": "Create"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "name": "test_effect",
            "color_scheme": "Mood | Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    )

    await hass.async_block_till_done()
    assert "test_effect" in hass.data["cololight"][entry["result"].entry_id].effects
