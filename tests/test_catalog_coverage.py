import json
from pathlib import Path

import dify_plugin  # noqa: F401 - patch before HTTP imports

from scripts.check_media_coverage import missing_operations
from tools.api_contracts import ENDPOINTS


def test_every_public_media_operation_is_covered_without_turning_services_into_models():
    catalog = json.loads(Path("tests/public-media-catalog.json").read_text())
    assert missing_operations(catalog) == []
    for service in ("digitalhuman", "maestro"):
        item = next(item for item in catalog["items"] if item["service_alias"] == service)
        assert item["kind"] == "service"
        endpoint = ENDPOINTS[service + "_generate_video"]
        assert endpoint["api_id"] in item["api_ids"]
        assert "model" not in endpoint["properties"] and "model" not in endpoint["defaults"]
    assert ENDPOINTS["dreamina_generate_video"]["properties"]["model"]["enum"] == ["omnihuman-1.5"]
    assert ENDPOINTS["gemini_generate_video"]["properties"]["model"]["enum"] == ["omni-flash"]


def test_new_catalog_api_creates_an_explicit_gap_instead_of_silently_disappearing():
    value = {"items": [{"id": "future-service", "kind": "service", "api_ids": ["new-api"]}]}
    assert missing_operations(value)[0]["missing_api_ids"] == ["new-api"]
