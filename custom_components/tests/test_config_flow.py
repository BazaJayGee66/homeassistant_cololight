from copy import deepcopy
import pytest
import cololight


from unittest.mock import patch

from tests.conftest import hass, hass_storage, load_registries
from tests.common import MockConfigEntry

from homeassistant import data_entry_flow

NAME = "cololight_test"
HOST = "1.1.1.1"

DEMO_USER_INPUT = {
    "device_data": {"name": NAME, "host": HOST, "device": "hexagon"},
    "effects_data": {
        "default_effects": [
            "80s Club",
            "Cherry Blossom",
        ],
    },
}

DEMO_USER_INPUT_2 = {
    "device_data": {"name": NAME, "host": HOST, "device": "strip"},
    "effects_data": {
        "default_effects": [
            "80s Club",
            "Cherry Blossom",
        ],
        "dynamic_effects": ["Graffiti", "Snow"],
    },
}


@pytest.fixture
def demo_user_input():
    return deepcopy(DEMO_USER_INPUT)


@pytest.fixture
def demo_user_input_2():
    return deepcopy(DEMO_USER_INPUT_2)


async def test_form(hass, demo_user_input):
    """Test config entry configured successfully."""

    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=demo_user_input["device_data"]
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "device_effects"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=demo_user_input["effects_data"],
    )

    expected_data = demo_user_input["device_data"] | demo_user_input["effects_data"]

    assert result["type"] == "create_entry"
    assert result["title"] == NAME
    assert result["data"] == expected_data

    await hass.async_block_till_done()
    assert hass.data["cololight"][result["result"].entry_id].effects == [
        "80s Club",
        "Cherry Blossom",
    ]


async def test_form_strip(hass, demo_user_input_2):
    """Test config entry configured successfully."""

    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=demo_user_input_2["device_data"]
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "device_effects"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=demo_user_input_2["effects_data"],
    )

    expected_data = demo_user_input_2["device_data"] | demo_user_input_2["effects_data"]

    assert result["type"] == "create_entry"
    assert result["title"] == NAME
    assert result["data"] == expected_data

    await hass.async_block_till_done()
    assert hass.data["cololight"][result["result"].entry_id].effects == [
        "80s Club",
        "Cherry Blossom",
        "Graffiti",
        "Snow",
    ]


async def test_form_already_configured(hass, demo_user_input):
    """Test host is already configured."""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=demo_user_input["device_data"], unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN,
        context={"source": "user"},
        data=demo_user_input["device_data"],
    )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"


@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_color_schemes",
    return_value=["Mood | Green", "Mood | Red"],
)
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_cololight"
)
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_max_mode",
    return_value=27,
)
async def test_options_creating_effect(
    mock_max_mode, mock_cololight, mock_color_schemes, hass, demo_user_input
):
    """Test options for create effect"""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=demo_user_input, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_MENU
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_effect"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "create_effect"

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
        result["flow_id"], user_input={"next_step_id": "create_effect"}
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
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_cololight"
)
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_max_mode",
    return_value=27,
)
async def test_options_updating_effect(
    mock_max_mode, mock_cololight, mock_scheme_colors, hass, demo_user_input
):
    """Test options for create effect is updated if already existing"""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=demo_user_input, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_effect"}
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
        result["flow_id"], user_input={"next_step_id": "create_effect"}
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


@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_effects",
    return_value={
        "80s Club": "80s Club",
        "Cherry Blossom": "Cherry Blossom",
        "test": "test",
        "test_2": "test_2",
    },
)
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_cololight"
)
async def test_options_removing_custom_effect(
    mock_cololight, mock_effects, hass, demo_user_input
):
    """Test options for removing effect"""
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
        "test": {
            "color_scheme": "Mood",
            "color": "Green",
            "cycle_speed": 1,
            "mode": 1,
        },
    }

    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=demo_user_input, unique_id=HOST
    )
    entry.add_to_hass(hass)

    entry.options = test_effects

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_MENU
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "remove_effect"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "remove_effect"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": ["test_2"],
        },
    )

    await hass.async_block_till_done()

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert entry.options == expected_effetcs


async def test_options_removing_default_effect(hass, demo_user_input):
    """Test options for removing effect"""
    flow = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input=demo_user_input["device_data"]
    )

    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=demo_user_input["effects_data"],
    )

    await hass.async_block_till_done()

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "remove_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "name": ["Cherry Blossom"],
        },
    )

    await hass.async_block_till_done()
    assert hass.data["cololight"][entry["result"].entry_id].effects == ["80s Club"]


async def test_options_removing_dynamic_effect(hass, demo_user_input_2):
    """Test options for removing effect"""
    flow = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input=demo_user_input_2["device_data"]
    )

    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=demo_user_input_2["effects_data"],
    )

    await hass.async_block_till_done()

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "remove_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "name": ["Graffiti"],
        },
    )

    await hass.async_block_till_done()
    assert hass.data["cololight"][entry["result"].entry_id].effects == [
        "80s Club",
        "Cherry Blossom",
        "Snow",
    ]


async def test_options_restoring_default_effect(hass, demo_user_input):
    """Test options for restoring effect"""
    flow = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input=demo_user_input["device_data"]
    )

    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=demo_user_input["effects_data"],
    )

    await hass.async_block_till_done()

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "restore_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "default_effects": ["Unicorns"],
        },
    )

    await hass.async_block_till_done()
    assert hass.data["cololight"][entry["result"].entry_id].effects == [
        "80s Club",
        "Cherry Blossom",
        "Unicorns",
    ]


async def test_options_restoring_dynamic_effect(hass, demo_user_input_2):
    """Test options for restoring effect"""
    flow = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input=demo_user_input_2["device_data"]
    )

    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=demo_user_input_2["effects_data"],
    )

    await hass.async_block_till_done()

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "restore_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={"dynamic_effects": ["Color train"]},
    )

    await hass.async_block_till_done()
    assert hass.data["cololight"][entry["result"].entry_id].effects == [
        "80s Club",
        "Cherry Blossom",
        "Graffiti",
        "Snow",
        "Color train",
    ]


@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_color_schemes",
    return_value=["Mood | Green"],
)
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_cololight"
)
@patch(
    "homeassistant.components.cololight.config_flow.CololightOptionsFlowHandler._get_max_mode",
    return_value=27,
)
async def test_options_has_error_if_invalid(
    mock_max_mode, mock_cololight, mock_color_schemes, hass, demo_user_input
):
    """Test options will show error if invalid"""
    entry = MockConfigEntry(
        domain=cololight.DOMAIN, data=demo_user_input, unique_id=HOST
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.RESULT_TYPE_MENU
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_effect"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "create_effect"

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


async def test_end_to_end_with_options(hass, demo_user_input):
    """Test an end to end flow, creating entity and add effects and removing effects"""
    flow = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input=demo_user_input["device_data"]
    )

    entry = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=demo_user_input["effects_data"],
    )

    await hass.async_block_till_done()

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "create_effect"}
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

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "remove_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "name": ["Cherry Blossom"],
        },
    )

    await hass.async_block_till_done()
    assert (
        "Cherry Blossom" not in hass.data["cololight"][entry["result"].entry_id].effects
    )

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "remove_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "name": ["test_effect"],
        },
    )

    await hass.async_block_till_done()
    assert hass.data["cololight"][entry["result"].entry_id].effects == ["80s Club"]

    option_flow = await hass.config_entries.options.async_init(entry["result"].entry_id)

    option_flow = await hass.config_entries.options.async_configure(
        option_flow["flow_id"], user_input={"next_step_id": "restore_effect"}
    )

    await hass.config_entries.options.async_configure(
        option_flow["flow_id"],
        user_input={
            "default_effects": ["Savasana", "Unicorns"],
        },
    )

    await hass.async_block_till_done()
    assert hass.data["cololight"][entry["result"].entry_id].effects == [
        "80s Club",
        "Savasana",
        "Unicorns",
    ]
