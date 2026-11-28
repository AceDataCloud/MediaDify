import json
from pathlib import Path

import dify_plugin  # noqa: F401 - patch before HTTP imports
import pytest
import requests
import yaml
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.tool import ToolRuntime

from tools.acemusic_client import build_request
from tools.api_contracts import ENDPOINTS
from tools.client import AceMediaClient

SOURCES = json.loads(Path("tests/source-tools.json").read_text())


def response(body, status=200):
    value = requests.Response()
    value.status_code = status
    value._content = json.dumps(body).encode()
    value.close = lambda: setattr(value, "closed_by_plugin", True)
    return value


def test_one_provider_keeps_all_original_native_tool_names_and_loads_each_implementation():
    registration = PluginRegistration(DifyPluginEnv())
    assert list(registration.tools_mapping) == ["ace_media"]
    actual = registration.tools_mapping["ace_media"][2]
    expected = {name for source in SOURCES for name in source["tool_names"]}
    retired = {row["tool"] for row in json.loads(Path("tests/retired-tools.json").read_text())}
    expected -= retired
    assert len(expected) == 127 and len(SOURCES) == 25
    assert set(actual) == expected
    for name in expected:
        assert registration.get_tool_cls("ace_media", name) is not None


def test_general_key_save_only_reads_model_catalog(monkeypatch):
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return response({"data": [{"id": "fixture"}]})

    monkeypatch.setattr(requests, "request", request)
    registration = PluginRegistration(DifyPluginEnv())
    registration.get_tool_provider_cls("ace_media")()._validate_credentials(
        {"acedata_bearer_token": "placeholder"}
    )
    assert len(calls) == 1 and calls[0][:2] == ("GET", "https://api.acedata.cloud/v1/models")
    assert calls[0][2]["json"] is None and calls[0][2]["allow_redirects"] is False


@pytest.mark.parametrize(
    "name", [key for key, endpoint in ENDPOINTS.items() if endpoint.get("operation") == "task"]
)
def test_each_task_tool_queries_its_own_service_path(name, monkeypatch):
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return response({"id": "original-task", "finished_at": None, "response": None})

    monkeypatch.setattr(requests, "request", request)
    result = AceMediaClient("placeholder").invoke(name, {"task_id": "original-task"})
    assert len(calls) == 1
    assert calls[0][1] == "https://api.acedata.cloud" + ENDPOINTS[name]["task_path"]
    assert calls[0][2]["json"]["id"] == "original-task"
    assert result["status"] == "pending" and result["task_id"] == "original-task"


def test_audio_services_keep_audio_outputs_ahead_of_optional_unrendered_video(monkeypatch):
    name = next(
        key
        for key, endpoint in ENDPOINTS.items()
        if endpoint.get("operation") == "task" and endpoint["service"] == "suno"
    )
    body = {
        "id": "original",
        "finished_at": 1,
        "response": {
            "status": "success",
            "data": [
                {
                    "audio_url": "https://example.org/song.mp3",
                    "video_url": "https://example.org/not-rendered.mp4",
                    "image_url": "https://example.org/cover.png",
                }
            ],
        },
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    result = AceMediaClient("placeholder").invoke(name, {"task_id": "original"})
    assert result["media_urls"] == ["https://example.org/song.mp3"]


def test_acemusic_preserves_all_exact_wire_contracts():
    cases = json.loads(Path("tests/acemusic-requests.json").read_text())
    assert len(cases) == 12
    for operation, (inputs, expected) in cases.items():
        assert list(build_request(operation, inputs)) == expected


def test_acemusic_partial_result_and_original_task_survive_native_dispatch(monkeypatch):
    r = response(
        {
            "id": "original",
            "response": {
                "status": "partial_failed",
                "data": [{"audio_url": "https://example.org/one-song.mp3"}],
            },
        }
    )
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    registration = PluginRegistration(DifyPluginEnv())
    cls = registration.get_tool_cls("ace_media", "acemusic_retrieve")
    tool = cls(
        ToolRuntime(
            credentials={"acedata_bearer_token": "placeholder"}, user_id=None, session_id=None
        ),
        None,
    )
    messages = list(tool._invoke({"task_id": "original"}))
    assert messages[0].message.json_object["id"] == "original"
    assert messages[0].message.json_object["response"]["status"] == "partial_failed"


def test_native_model_options_are_accepted_by_their_runtime_enums():
    for path in Path("tools").glob("*.yaml"):
        tool = yaml.safe_load(path.read_text())
        name = tool["identity"]["name"]
        for parameter in tool["parameters"]:
            if parameter["name"] not in {
                "model",
                "version",
                "mv",
                "model_version",
            } or not parameter.get("options"):
                continue
            offered = {str(option["value"]) for option in parameter["options"]}
            if name.startswith("acemusic_"):
                supported = set(
                    json.loads(Path("tools/acemusic_models.json").read_text())["models"]
                )
            else:
                schema = ENDPOINTS[name]["properties"].get(parameter["name"], {})
                if not schema.get("enum"):
                    continue
                supported = {str(value) for value in schema["enum"]}
            assert offered <= supported, (name, parameter["name"], offered - supported)
