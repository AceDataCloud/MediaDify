# Ace Media and Tools for Dify

One **Ace Data Cloud** provider brings **124 native tools across 25 service families** into Dify. It consolidates the existing image, video, music, speech, face and search integrations. Each service keeps its own tool names and controls; one General application API key is configured on the provider.

**Distribution:** source/release packages alone do not establish a Marketplace listing or Verified status. Check the [official Marketplace page](https://marketplace.dify.ai/plugin/acedatacloud/ace_media) for current availability; until accepted, use only your workspace's permitted local-package flow. The official consolidation review determines the transition schedule. No existing plugin is uninstalled, and no existing workflow is changed automatically.

[Source](https://github.com/AceDataCloud/MediaDify) · [Issues](https://github.com/AceDataCloud/MediaDify/issues) · [Simplified Chinese](readme/README_zh_Hans.md) · dev@acedata.cloud

## Install and configure

1. Download the `.difypkg` from this repository's release or review artifact. Use **Plugins → Install → Local Package** only where your Dify workspace permits local plugins. A source package does not carry Marketplace verification.
2. Open **Integrations → Tools → Ace Media and Tools**. These are native Tools; chat-model selection remains in the separate Ace Data Cloud model provider.
3. Sign in at [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications). If the General application has not been initialized, initialize it first. Copy an authorized existing key or create a dedicated key with an appropriate expiry and usage/API limits.
4. In the Dify provider credential dialog, paste the **raw API token**, without `Bearer` or quotes. Do not use a platform management token. Restrict who may use the Dify credential.
5. Save once. Saving only reads `/v1/models`; it does not generate media or run face/search tools. The key must be permitted to read that catalog. Saving validates the key, not entitlement or balance for every service.

Task/persona deletion tools require an explicit confirmation flag and the selected resource ID. Enable only the operations your workflow needs.

Use a **General application** key with access to the services you select. If Allowed APIs are restricted, permit the actual generation/operation endpoints and task-query endpoints used by your workflow, as well as the read-only model catalog. A service-specific key cannot cover all 25 families. API calls use current account pricing; a free plugin does not make generation, voice operations, uploads or search free.

## Select the service tool

Search by the service name in the Dify tool picker. Existing tool IDs and request controls are preserved for the active contracts. The package contains:

| Service | Active native tools | Implementation provenance |
|---|---:|---|
| Face Transform | 1 | [Source adapter](https://github.com/AceDataCloud/FaceDify) |
| Fish Audio | 6 | [Source adapter](https://github.com/AceDataCloud/FishAudioDify) |
| Flux | 5 | [Source adapter](https://github.com/AceDataCloud/FluxDify) |
| GPT Image | 5 | [Source adapter](https://github.com/AceDataCloud/GPTImageDify) |
| Google Search | 1 | [Source adapter](https://github.com/AceDataCloud/GoogleSearchDify) |
| Grok | 4 | [Source adapter](https://github.com/AceDataCloud/GrokDify) |
| Hailuo | 3 | [Source adapter](https://github.com/AceDataCloud/HailuoDify) |
| HappyHorse | 3 | [Source adapter](https://github.com/AceDataCloud/HappyHorseDify) |
| Kling | 8 | [Source adapter](https://github.com/AceDataCloud/KlingDify) |
| Luma | 3 | [Source adapter](https://github.com/AceDataCloud/LumaDify) |
| Midjourney | 9 | [Source adapter](https://github.com/AceDataCloud/MidjourneyDify) |
| MiniMax | 5 | [Source adapter](https://github.com/AceDataCloud/MiniMaxDify) |
| Nano Banana | 4 | [Source adapter](https://github.com/AceDataCloud/NanoBananaDify) |
| Producer | 7 | [Source adapter](https://github.com/AceDataCloud/ProducerDify) |
| Qwen Image | 3 | [Source adapter](https://github.com/AceDataCloud/QwenImageDify) |
| Seedance | 3 | [Source adapter](https://github.com/AceDataCloud/SeedanceDify) |
| Seedream | 5 | [Source adapter](https://github.com/AceDataCloud/SeedreamDify) |
| Suno | 19 | [Source adapter](https://github.com/AceDataCloud/SunoDify) |
| Veo | 3 | [Source adapter](https://github.com/AceDataCloud/VeoDify) |
| Wan | 4 | [Source adapter](https://github.com/AceDataCloud/WanDify) |
| ACE Music | 9 | [Source adapter](https://github.com/AceDataCloud/ACEMusicDify) |
| Digital Human | 5 | [Public video API](https://platform.acedata.cloud/api/v1/apis/5ced04db-8d92-4a6b-b988-91423dcc1f02/) |
| Dreamina OmniHuman 1.5 | 3 | [Public video API](https://platform.acedata.cloud/api/v1/apis/b3880780-678f-4495-bda7-3a1ecf42781c/) |
| Gemini Omni Flash Video | 3 | [Public video API](https://platform.acedata.cloud/api/v1/apis/d9d2fd18-5b1e-4218-b572-a75cf46f5451/) |
| Maestro | 3 | [Public video API](https://platform.acedata.cloud/api/v1/apis/ab512c42-324c-42e6-8d79-49a5042f3548/) |

Model dropdowns and runtime validation are synchronized from each operation's actual public API definition, not a short popular-model list. Image and video models stay in their native tool interfaces. The source synchronization never guesses a model's price or capabilities from its name.

## Additional video operations

Digital Human and Maestro are fixed service operations, not invented model IDs. Digital Human accepts a source image/video and driving audio, or text with an owned voice ID; its clone-voice tool accepts an authorized voice sample. Deprecated engine/resolution selectors are not exposed as meaningful choices. Dreamina uses the documented `omnihuman-1.5` model at `/dreamina/videos`; Gemini uses `omni-flash` at `/gemini/videos`, with an image required when editing a reference video.

Maestro supports generate/remix/edit/extend, with the original `ref_task_id` required for revisions and exactly one output language. Digital Human and Maestro history tools list the caller's recent tasks; they do not pretend to retrieve a selected ID array. Dreamina/Gemini batch tools explicitly take IDs. Returned reference images/audio are not advertised as newly generated video; Dreamina's documented `done` state and Maestro's delivered `output_url` variants are handled.

The full public media catalog is checked by API operation in addition to existing model lists. New uncovered operations fail the source synchronization for adapter review. Standard OpenAI speech/transcription/embedding interfaces belong to the companion model-provider source; that source-level coverage is not a claim about its current Marketplace release.

## A first asynchronous workflow

1. Add a service's creation tool, such as an ACE Music song tool or Suno audio tool. Supply your own prompt and the parameters appropriate to that action.
2. Run creation **once**, then keep the returned `task_id`/trace ID. An accepted request or `pending` result is not a completed song, image or video.
3. Bind that original task ID into the **same service's** task-retrieval tool. If still pending, query it again or use the tool's bounded wait option when available. Do not repeat generation to poll status.
4. Use completed outputs only. Generic media tools expose status/data/media links and per-item batch states. ACE Music retains its original `result` envelope, including partial failures and any usable tracks in `response.data[].audio_url`.

When creation times out before returning a task ID, inspect the original request or task history before resubmitting. Paid submissions are not retried automatically. Completed media links can expire; follow your own retention requirements. Synchronous tools, such as search or face processing, return their result directly.

Reference images, audio and video must be accessible URLs supported by the selected operation. ACE Music reference import requires a public HTTPS MP3 URL. Use material and voices you are authorized to process. The plugin passes references to Ace Data Cloud; it does not fetch arbitrary URLs itself. If you supply a callback URL, use a destination you control.

## Consolidation and existing workflows

This package addresses Dify's [Marketplace Curation Policy](https://github.com/langgenius/dify-plugins/blob/main/docs/marketplace-curation-policy.md#3-no-same-author-near-duplicate-plugins) for the existing Ace single-service family. Producer, Hailuo, Luma and ACE Music are included in this consolidation instead of being submitted as four additional near-duplicate plugins.

Installing this plugin does **not** migrate existing workflows. During an approved transition, duplicate a workflow for testing, replace an old provider node with **Ace Media and Tools → the same tool name**, transfer its existing parameter bindings, and select an authorized General application credential. Validate that draft before switching production use. Credential identifiers/provider IDs differ even when the tool ID is retained. Do not rewrite shared workflows or retire old installations in bulk.

The official review will determine the transition schedule. Legacy Marketplace entries have not been removed by this repository. Their eventual retirement or migration requires separate coordination and approval.

Nine old source tools point to APIs already marked **Deprecated** by the public production service. They are intentionally absent from this new package; no replacement model/endpoint is chosen silently:

| Historical tool ID | Deprecated public API |
|---|---|
| `fish_create_voice` | `/fish/voices` |
| `kling_virtual_try_on` | `/kling/virtual-try-on` |
| `kling_apparel` | `/kling/apparel` |
| `kling_voices` | `/kling/voices` |
| `kling_elements` | `/kling/elements` |
| `veo_extend_video` | `/veo/extend` |
| `veo_edit_objects` | `/veo/objects` |
| `veo_reshoot_video` | `/veo/reshoot` |
| `veo_upsample_video` | `/veo/upsample` |

Other public APIs retain their current Alpha/Beta/Production status. Consult the selected API's documentation and validate the intended workflow before relying on an experimental operation.

## Privacy and operational limits

The network recipient is the fixed HTTPS host `api.acedata.cloud`. Prompts, lyrics, queries, reference URLs and requested operation parameters are sent there with the API key. Face tools can process identifiable face images and facial landmarks; images, voices and other inputs may contain personal or biometric data. Only use authorized material and appropriate consent. Read the complete [Privacy policy](PRIVACY.md).

The plugin adds no database, analytics or telemetry and does not intentionally log credentials or raw API errors. Dify retains workflow data under your workspace settings. Removing a plugin does not erase Dify or API-side records.

| Symptom | Action |
|---|---|
| Credential Save fails | Check the raw application key, expiry, `/v1/models` access and network. |
| A selected service returns 401/403 | Check that service's permissions, Allowed APIs, content rules and balance. Do not share your key. |
| 429 | Reduce concurrency and retry later; do not repeat an uncertain creation request blindly. |
| Missing or pending output | Query the original task in the same service and preserve its trace ID. |
| Model option missing after a new launch | Update to a reviewed package generated from the current public API definitions. |

## Maintenance and validation

The shared transport/task/error handling is implemented once; service-specific parameter adapters and original native tool controls are retained. The included MIT license and source-provenance ledger preserve attribution.

```sh
python -m pip install -r requirements.txt pytest ruff
python -m pytest
ruff check .
ruff format --check .
python scripts/sync_models.py --refresh
python scripts/sync_models.py --check
python scripts/check_media_coverage.py --refresh
dify plugin package . -o ../ace_media-0.1.3.difypkg
```

The normal test suite loads every tool through the real Dify SDK, replays source request-contract examples, checks original-task and batch behavior, and verifies model/picker/runtime parity. Tests use offline responses; they do not make paid calls. The new consolidated package has not been represented as a fresh Dify Cloud or live paid-generation acceptance. Source/CLI validation and official Marketplace publication are separate steps.

The daily source workflow reads only public metadata, regenerates model options and opens a reviewed bot PR when data changes. Deprecated APIs or a retired default stop synchronization for review rather than silently switching models. Official package review and workspace upgrades still apply.
