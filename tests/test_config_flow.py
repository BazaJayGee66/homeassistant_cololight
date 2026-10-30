from copy import deepcopy

import pytest
from homeassistant.components.light import ATTR_EFFECT_LIST
from homeassistant.config_entries import STORAGE_KEY
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry, flush_store

from custom_components import cololight

NAME = "cololight_test"
HOST = "1.1.1.1"
ENTITY_ID = f"light.{NAME}"

HEXAGON_DATA = {
    "name": NAME,
    "host": HOST,
    "device": "hexagon",
    "default_effects": ["80s Club", "Cherry Blossom"],
}

STRIP_DATA = HEXAGON_DATA | {"device": "strip"}

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


async def setup_entry(hass, data, options=None):
    entry = MockConfigEntry(
        domain=cololight.DOMAIN,
        data=deepcopy(data),
        options=options or {},
        unique_id=data["host"],
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def configure_options(hass, entry, step_id, user_input):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": step_id}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=user_input
    )
    await hass.async_block_till_done()
    await flush_store(hass.config_entries._store)
    return result


def effect_list(hass):
    return hass.states.get(ENTITY_ID).attributes[ATTR_EFFECT_LIST]


def stored_data(hass_storage, entry):
    stored_entries = hass_storage[STORAGE_KEY]["data"]["entries"]
    return next(e["data"] for e in stored_entries if e["entry_id"] == entry.entry_id)


async def test_form(hass, demo_user_input):
    """Test config entry configured successfully."""

    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=demo_user_input["device_data"]
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device_effects"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=demo_user_input["effects_data"],
    )

    expected_data = demo_user_input["device_data"] | demo_user_input["effects_data"]

    assert result["type"] == FlowResultType.CREATE_ENTRY
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
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=demo_user_input_2["device_data"]
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device_effects"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=demo_user_input_2["effects_data"],
    )

    expected_data = demo_user_input_2["device_data"] | demo_user_input_2["effects_data"]

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME
    assert result["data"] == expected_data

    await hass.async_block_till_done()
    assert hass.data["cololight"][result["result"].entry_id].effects == [
        "80s Club",
        "Cherry Blossom",
        "Graffiti",
        "Snow",
    ]


async def test_form_strip_without_dynamic_effects(hass, demo_user_input_2):
    """Test config entry stores no dynamic effects when none are chosen"""
    result = await hass.config_entries.flow.async_init(
        cololight.DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=demo_user_input_2["device_data"]
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"default_effects": ["80s Club", "Cherry Blossom"]},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["dynamic_effects"] == []


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

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_creating_effect(hass):
    """Test options for create effect"""
    entry = await setup_entry(hass, HEXAGON_DATA)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.MENU
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_effect"}
    )

    assert result["type"] == FlowResultType.FORM
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

    assert result["type"] == FlowResultType.CREATE_ENTRY
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


async def test_options_updating_effect(hass):
    """Test options for create effect is updated if already existing"""
    entry = await setup_entry(hass, HEXAGON_DATA)

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


async def test_options_removing_custom_effect(hass):
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

    entry = await setup_entry(hass, HEXAGON_DATA, options=test_effects)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.MENU
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "remove_effect"}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "remove_effect"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "name": ["test_2"],
        },
    )

    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options == expected_effetcs
    assert effect_list(hass) == ["80s Club", "Cherry Blossom", "test"]


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


async def test_options_removing_a_restored_default_effect(hass, hass_storage):
    """Test removing an effect again after restoring it reloads and saves the entry"""
    entry = await setup_entry(hass, HEXAGON_DATA)

    await configure_options(hass, entry, "remove_effect", {"name": ["Cherry Blossom"]})
    assert effect_list(hass) == ["80s Club"]
    data = stored_data(hass_storage, entry)
    assert data["default_effects"] == ["80s Club"]

    await configure_options(
        hass, entry, "restore_effect", {"default_effects": ["Cherry Blossom"]}
    )
    assert effect_list(hass) == ["80s Club", "Cherry Blossom"]
    data = stored_data(hass_storage, entry)
    assert data["default_effects"] == ["80s Club", "Cherry Blossom"]

    await configure_options(hass, entry, "remove_effect", {"name": ["Cherry Blossom"]})
    assert effect_list(hass) == ["80s Club"]
    data = stored_data(hass_storage, entry)
    assert data["default_effects"] == ["80s Club"]


async def test_options_restoring_a_removed_default_effect_again(hass, hass_storage):
    """Test restoring an effect again after removing it reloads and saves the entry"""
    entry = await setup_entry(hass, HEXAGON_DATA)

    await configure_options(hass, entry, "remove_effect", {"name": ["Cherry Blossom"]})
    await configure_options(
        hass, entry, "restore_effect", {"default_effects": ["Cherry Blossom"]}
    )
    await configure_options(hass, entry, "remove_effect", {"name": ["Cherry Blossom"]})
    await configure_options(
        hass, entry, "restore_effect", {"default_effects": ["Cherry Blossom"]}
    )

    assert effect_list(hass) == ["80s Club", "Cherry Blossom"]
    data = stored_data(hass_storage, entry)
    assert data["default_effects"] == ["80s Club", "Cherry Blossom"]


async def test_options_removing_effect_from_entry_with_stored_marker_keys(hass):
    """Test entries saved with the old marker keys still set up and can be edited"""
    entry = await setup_entry(
        hass,
        HEXAGON_DATA,
        options={
            "removed_effects": ["Cherry Blossom"],
            "restored_effects": {"default_effects": ["Cherry Blossom"]},
        },
    )
    assert effect_list(hass) == ["80s Club", "Cherry Blossom"]

    await configure_options(hass, entry, "remove_effect", {"name": ["Cherry Blossom"]})

    assert effect_list(hass) == ["80s Club"]


async def test_options_restoring_dynamic_effect_without_stored_dynamic_effects(
    hass, hass_storage
):
    """Test restoring a dynamic effect on a strip set up without dynamic effects"""
    entry = await setup_entry(hass, STRIP_DATA)

    result = await configure_options(
        hass, entry, "restore_effect", {"dynamic_effects": ["Graffiti"]}
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert effect_list(hass) == ["80s Club", "Cherry Blossom", "Graffiti"]
    data = stored_data(hass_storage, entry)
    assert data["dynamic_effects"] == ["Graffiti"]


async def test_options_has_error_if_invalid(hass):
    """Test options will show error if invalid"""
    entry = await setup_entry(hass, HEXAGON_DATA)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.MENU
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_effect"}
    )

    assert result["type"] == FlowResultType.FORM
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

    assert result["type"] == FlowResultType.FORM
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

    assert result["type"] == FlowResultType.FORM
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
