import pytest

# Imported first so HA loads this repo's custom_components, not phcc's testing config.
import custom_components.cololight  # noqa: F401


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
