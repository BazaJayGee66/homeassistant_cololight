import json
from importlib.metadata import version
from pathlib import Path

from custom_components import cololight

MANIFEST_PATH = Path(cololight.__file__).with_name("manifest.json")


def test_installed_pycololight_matches_manifest_pin():
    requirements = json.loads(MANIFEST_PATH.read_text())["requirements"]

    assert f"pycololight=={version('pycololight')}" in requirements
