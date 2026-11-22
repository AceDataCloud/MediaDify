import json

import dify_plugin  # noqa: F401 - patch before HTTP imports
import pytest
import requests
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.tool import ToolRuntime

from tools.api_contracts import ENDPOINTS
from tools.client import AceMediaClient, AceMediaError


def response(body, status=200):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(body).encode()
    result.close = lambda: None
    return result


CASES = [
    (
        "digitalhuman_generate_video",
        {
            "video_url": "https://example.org/person.mp4",
            "audio_url": "https://example.org/speech.wav",
        },
        "/digital-human/videos",
        {"async": True},
    ),
    (
        "digitalhuman_generate_video",
        {"image_url": "https://example.org/person.png", "text": "Hello", "voice_id": "owned-voice"},
        "/digital-human/videos",
        {"voice_id": "owned-voice", "async": True},
    ),
    (
        "digitalhuman_clone_voice",
        {"audio_url": "https://example.org/owned-voice.wav", "lang": "en"},
        "/digital-human/voices",
        {"lang": "en", "async": True},
    ),
    (
        "dreamina_generate_video",
        {
            "image_url": "https://example.org/person.png",
            "audio_url": "https://example.org/speech.wav",
        },
        "/dreamina/videos",
        {"model": "omnihuman-1.5", "async": True},
    ),
    (
        "gemini_generate_video",
        {
            "prompt": "A short clip",
            "image_urls": '["https://example.org/still.png"]',
            "video_urls": '["https://example.org/ref.mp4"]',
        },
        "/gemini/videos",
        {"model": "omni-flash", "async": True, "video_urls": ["https://example.org/ref.mp4"]},
    ),
    (
        "maestro_generate_video",
        {"prompt": "A short explainer", "langs": '["en"]'},
        "/maestro/videos",
        {"action": "generate", "langs": ["en"]},
    ),
    (
        "maestro_generate_video",
        {"prompt": "Revise the ending", "action": "edit", "ref_task_id": "original"},
        "/maestro/videos",
        {"action": "edit", "ref_task_id": "original"},
    ),
]


@pytest.mark.parametrize("tool_name,inputs,path,expected", CASES)
def test_new_native_creation_uses_public_wire_contract_once(
    tool_name, inputs, path, expected, monkeypatch
):
    calls = []

    def send(method, url, **kwargs):
        calls.append(
            requests.Request(
                method, url, headers=kwargs["headers"], json=kwargs.get("json")
            ).prepare()
        )
        return response(
            {"success": True, "task_id": "original-task", "trace_id": "fixture"},
            201 if path.startswith("/maestro/") else 200,
        )

    monkeypatch.setattr(requests, "request", send)
    registry = PluginRegistration(DifyPluginEnv())
    cls = registry.get_tool_cls("ace_media", tool_name)
    tool = cls(
        ToolRuntime(credentials={"acedata_bearer_token": "fixture"}, user_id=None, session_id=None),
        None,
    )
    messages = list(tool._invoke(inputs))
    assert (
        len(calls) == 1
        and calls[0].method == "POST"
        and calls[0].url == "https://api.acedata.cloud" + path
    )
    body = json.loads(calls[0].body)
    for key, value in expected.items():
        assert body[key] == value
    if path.startswith(("/digital-human/", "/maestro/")):
        assert "model" not in body
    assert "engine" not in body
    result = messages[0].message.json_object
    assert result["status"] == "pending" and result["task_id"] == "original-task"


@pytest.mark.parametrize(
    "tool,inputs",
    [
        ("digitalhuman_generate_video", {"audio_url": "https://example.org/audio.wav"}),
        (
            "digitalhuman_generate_video",
            {"image_url": "https://example.org/face.png", "text": "Missing voice"},
        ),
        (
            "gemini_generate_video",
            {"prompt": "Edit", "video_urls": '["https://example.org/video.mp4"]'},
        ),
        ("gemini_generate_video", {"prompt": "Edit", "image_urls": "[17]"}),
        ("maestro_generate_video", {"prompt": "Edit", "action": "edit"}),
        ("maestro_generate_video", {"prompt": "Explain", "langs": '["en","zh-cn"]'}),
        ("maestro_generate_video", {"prompt": "Caption", "scenario": "captions"}),
        ("digitalhuman_delete_task", {"id": "original", "confirm": False}),
    ],
)
def test_invalid_conditional_inputs_are_rejected_before_network(tool, inputs, monkeypatch):
    monkeypatch.setattr(
        requests, "request", lambda *a, **k: pytest.fail("invalid input was submitted")
    )
    with pytest.raises(ValueError):
        AceMediaClient("fixture").invoke(tool, inputs)


def test_dreamina_done_is_terminal_and_input_media_is_not_advertised_as_output(monkeypatch):
    body = {
        "id": "original",
        "finished_at": 1,
        "response": {
            "success": True,
            "task_id": "original",
            "data": {
                "status": "done",
                "audio_url": "https://example.org/input.wav",
                "image_url": "https://example.org/input.png",
                "video_url": "https://example.org/output.mp4",
            },
        },
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    result = AceMediaClient("fixture").invoke("dreamina_get_task", {"task_id": "original"})
    assert result["status"] == "succeeded" and result["media_urls"] == [
        "https://example.org/output.mp4"
    ]
    body["finished_at"] = None
    assert (
        AceMediaClient("fixture").invoke("dreamina_get_task", {"task_id": "original"})["status"]
        == "pending"
    )


def test_maestro_delivered_variant_output_url_is_available(monkeypatch):
    body = {
        "id": "original",
        "finished_at": 1,
        "request": {"file_urls": ["https://example.org/input.png"]},
        "response": {
            "success": True,
            "data": {
                "state": "succeeded",
                "variants": [{"kind": "video", "output_url": "https://example.org/output.mp4"}],
                "project": {"tarball_url": "https://example.org/source.gz"},
            },
        },
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    result = AceMediaClient("fixture").invoke("maestro_get_task", {"task_id": "original"})
    assert result["status"] == "succeeded" and result["media_urls"] == [
        "https://example.org/output.mp4"
    ]


@pytest.mark.parametrize("tool", ["digitalhuman_list_tasks", "maestro_list_tasks"])
def test_history_is_not_pretended_to_be_an_id_batch(tool, monkeypatch):
    calls = []

    def send(method, url, **kwargs):
        calls.append(kwargs["json"])
        return response({"count": 0, "items": []})

    monkeypatch.setattr(requests, "request", send)
    AceMediaClient("fixture").invoke(tool, {"limit": 7, "created_at_min": 1700000000})
    assert calls == [{"action": "retrieve_batch", "limit": 7, "created_at_min": 1700000000}]
    assert "ids" not in ENDPOINTS[tool]["properties"]


@pytest.mark.parametrize("tool", ["dreamina_get_tasks", "gemini_get_tasks"])
def test_selected_id_batch_preserves_ids(tool, monkeypatch):
    calls = []

    def send(method, url, **kwargs):
        calls.append(kwargs["json"])
        return response({"count": 0, "items": []})

    monkeypatch.setattr(requests, "request", send)
    AceMediaClient("fixture").invoke(tool, {"ids": '["first","second"]'})
    assert calls == [{"ids": ["first", "second"], "action": "retrieve_batch"}]


def test_maestro_record_status_controls_completion_even_with_a_stale_inner_stage(monkeypatch):
    body = {
        "id": "original",
        "status": "succeeded",
        "finished_at": 1,
        "response": {
            "success": True,
            "data": {
                "state": "producing",
                "variants": [{"output_url": "https://example.org/output.mp4"}],
            },
        },
    }
    monkeypatch.setattr(requests, "request", lambda *a, **k: response(body))
    assert (
        AceMediaClient("fixture").invoke("maestro_get_task", {"task_id": "original"})["status"]
        == "succeeded"
    )
    body["status"] = "failed"
    with pytest.raises(AceMediaError):
        AceMediaClient("fixture").invoke("maestro_get_task", {"task_id": "original"})
