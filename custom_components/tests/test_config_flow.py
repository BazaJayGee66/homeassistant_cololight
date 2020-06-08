import sys

# from unittest.mock import patch

import cololight

# Link to homeassistant module
sys.path.insert(1, "/homeassistant/core")
from tests.conftest import hass, hass_storage
from tests.common import MockConfigEntry

from homeassistant import data_entry_flow
from homeassistant.const import CONF_SCAN_INTERVAL


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
        cololight.DOMAIN, context={"source": "user"}, data=DEMO_USER_INPUT,
    )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"
