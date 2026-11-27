import json
from pathlib import Path

import dify_plugin  # noqa: F401 - patch before HTTP imports
import pytest
import yaml

from scripts.sync_models import apply, model_options
from tools.api_contracts import ENDPOINTS
from tools.client import AceMediaClient


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
                location = entry["locations"][field]
                if location == "body":
                    assert ENDPOINTS[name]["properties"][field]["enum"] == models
                else:
                    parameter = next(
                        p
                        for p in ENDPOINTS[name]["parameters"]
                        if p["in"] == location and p["name"] == field
                    )
                    assert parameter["schema"]["enum"] == models
                    assert field not in ENDPOINTS[name]["properties"]
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


def test_public_parameter_location_is_preserved_without_assuming_body():
    models = ["s1", "s2-pro", "s2.1-pro"]
    api = {
        "id": "fixture",
        "definition": {
            "paths": {
                "/fish/tts": {
                    "post": {
                        "parameters": [
                            {"name": "model", "in": "header", "schema": {"enum": models}}
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"properties": {"text": {"type": "string"}}}
                                }
                            }
                        },
                    }
                }
            }
        },
    }
    options, locations = model_options(api, "/fish/tts")
    assert options == {"model": models} and locations == {"model": "header"}


@pytest.mark.parametrize(
    ("tool", "inputs"),
    [
        ("seedream_generate_image", {"prompt": "A red flower"}),
        ("seedream_edit_image", {"prompt": "Make it blue", "image": "https://example.org/ref.png"}),
    ],
)
def test_every_seedream_picker_model_builds_a_valid_request(tool, inputs):
    client = AceMediaClient("fixture")
    for model in ENDPOINTS[tool]["properties"]["model"]["enum"]:
        method, path, body, *_ = client.prepare(tool, {**inputs, "model": model})
        assert (method, path, body["model"]) == ("POST", "/seedream/images", model)
    with pytest.raises(ValueError):
        client.prepare(
            tool,
            {**inputs, "model": "doubao-seedream-5-5-261028", "tools": '[{"type":"web_search"}]'},
        )
