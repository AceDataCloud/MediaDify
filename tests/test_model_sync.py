import json
from pathlib import Path

import dify_plugin  # noqa: F401 - patch before HTTP imports
import yaml

from scripts.sync_models import apply
from tools.api_contracts import ENDPOINTS


def test_live_source_snapshot_matches_every_runtime_enum_and_native_picker():
    snapshot = json.loads(Path("tests/published-model-options.json").read_text())
    pickers = {
        tool["identity"]["name"]: tool
        for path in Path("tools").glob("*.yaml")
        if (tool := yaml.safe_load(path.read_text()))
    }
    assert not apply(snapshot, check=True)
    for name, entry in snapshot.items():
        if name == "acemusic":
            assert (
                json.loads(Path("tools/acemusic_models.json").read_text())["models"]
                == entry["options"]["model"]
            )
            names = ["acemusic_generate", "acemusic_custom"]
        else:
            names = [name] if name in pickers else []
            assert ENDPOINTS[name]["api_id"] == entry["api_id"]
            for field, models in entry["options"].items():
                assert ENDPOINTS[name]["properties"][field]["enum"] == models
        for tool_name in names:
            for parameter in pickers[tool_name]["parameters"]:
                field = parameter["name"]
                if field in entry["options"] and parameter["type"] == "select":
                    assert {str(option["value"]) for option in parameter["options"]} == {
                        str(model) for model in entry["options"][field]
                    }, (tool_name, field)


def test_deprecated_source_operations_are_absent_from_the_new_bundle():
    retired = {row["tool"] for row in json.loads(Path("tests/retired-tools.json").read_text())}
    assert len(retired) == 9
    assert retired.isdisjoint(ENDPOINTS)
    names = {
        yaml.safe_load(path.read_text())["identity"]["name"]
        for path in Path("tools").glob("*.yaml")
    }
    assert retired.isdisjoint(names)
