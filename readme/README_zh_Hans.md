# Dify Ace 媒体与工具

一个 **Ace Data Cloud** 供应商整合 **21 个服务系列的 110 个当前原生工具**，覆盖图片、视频、音乐、语音、面部处理与搜索。每个服务保留独立工具名和参数，只需在供应商中配置一个通用应用 API Key。

**分发说明：**源码或 Release 包本身不代表已上架或获得 Marketplace Verified。请以[官方市场页面](https://marketplace.dify.ai/plugin/acedatacloud/ace_media)的当前状态为准；正式获准前，只能使用工作区允许的本地插件安装流程。整合和迁移时间由官方审核确定。本仓库不会自动卸载已有插件，也不会改写已有工作流。

[源码](https://github.com/AceDataCloud/MediaDify) · [反馈](https://github.com/AceDataCloud/MediaDify/issues) · [English](../README.md) · dev@acedata.cloud

## 安装与配置

1. 从本仓库 Release 或审核附件下载 `.difypkg`。仅在工作区允许本地插件时，通过 **Plugins → Install → Local Package** 安装。源码安装包不代表官方市场验证。
2. 打开 **Integrations → Tools → Ace 媒体与工具**。这是原生工具供应商；聊天模型选择仍属于独立的 Ace Data Cloud 模型供应商。
3. 登录 [Ace Data Cloud 我的应用](https://platform.acedata.cloud/console/applications)。如果尚未初始化通用应用，先初始化，再复制已有获授权 Key 或创建带有效期、用量与 API 限制的专用 Key。
4. 在 Dify 供应商凭据窗口粘贴原始 API Token，不加 `Bearer` 或引号，不使用平台管理 Token，并限制谁能使用该凭据。
5. 保存一次。保存只读 `/v1/models`，不运行生成、面部处理或搜索；Key 必须允许读取该目录。保存成功只证明 Key 可验证，不代表所有服务权限和余额都充足。

任务或人设删除工具要求显式确认标志和目标资源 ID，请只允许工作流需要的操作。

使用具有所选服务权限的**通用应用 Key**。启用 Allowed APIs 时，允许工作流涉及的生成/操作接口、同服务任务查询接口，以及只读模型目录。单服务专用 Key 无法覆盖全部 21 个系列。插件免费，API 调用按账号当前价格计费；生成、声音操作、上传和搜索可能分别计费。

## 选择服务工具

在工具选择器中搜索服务名，使用原有参数控件。当前包含：

| 服务 | 当前原生工具数 | 实现来源 |
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

模型下拉框和运行时校验按具体操作的公开 API 定义同步，不只列热门型号。图片、视频继续使用相应原生工具，模型价格和能力不会根据名称猜测。

## 异步工作流

1. 选择对应服务的创建工具，填写有权使用的提示词与参数。
2. 创建只提交一次，保留返回的 `task_id`/trace ID。请求受理或 `pending` 不代表内容已生成。
3. 把原任务 ID 绑定到**同一服务**的任务查询工具。仍在处理时继续查询原 ID，或使用支持的有界等待选项；不要重新调用生成来查询进度。
4. 只使用已完成结果。通用工具输出状态、数据、媒体链接和逐项批任务状态；ACE Music 保留原始 `result`，包括部分失败状态及 `response.data[].audio_url` 中可用的音轨。

创建超时且未拿到任务 ID 时，先查原请求和任务历史，再决定是否重提。插件不自动重试付费提交。搜索、面部处理等同步工具直接返回结果。引用素材必须符合所选 API 的可访问 URL 要求；ACE Music 引用导入需要公共 HTTPS MP3 URL。插件把引用地址交给 API，不自行抓取任意 URL；回调地址应由你控制。

## 整合与迁移

本包按 Dify 的[同作者插件整合规则](https://github.com/langgenius/dify-plugins/blob/main/docs/marketplace-curation-policy.md#3-no-same-author-near-duplicate-plugins)整合既有单服务系列。Producer、Hailuo、Luma、ACE Music 加入同一包，不再作为四个近重复插件单独向市场投稿。

安装本包不会迁移现有工作流。在获得批准的过渡期，先复制工作流用于测试，再把原供应商节点替换为 **Ace 媒体与工具 → 同名工具**，转移参数绑定并选择获授权通用 Key。先验证草稿，再切换生产；即使工具 ID 相同，供应商和凭据标识也不同。不要批量重写共享工作流或卸载旧插件。

过渡时间由官方审核与维护安排确定。本仓库没有移除既有市场条目；实际退役或迁移须另行协调并批准。

以下 9 个旧源码工具对应的生产公开 API 已标记 **Deprecated**，不再纳入新包；插件不会擅自替换模型或接口：

| 历史工具 ID | 已弃用公开 API |
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

其他公开 API 仍保留各自 Alpha/Beta/Production 状态，使用实验性操作前请查看当前文档并验证工作流。

## 隐私与限制

请求固定发往 HTTPS `api.acedata.cloud`，包括 API Key、提示词、歌词、查询、引用 URL 及所选操作参数。面部工具可能处理可识别照片与面部关键点；图片、声音等输入也可能包含个人或生物特征信息。请确保素材权利与必要同意。详见完整[隐私政策](../PRIVACY.md)。

插件不新增数据库、分析统计或遥测，也不主动记录凭据和原始 API 错误。Dify 按工作区设置保留流程数据；卸载插件不会删除 Dify 或 API 侧已有记录。

- 保存失败：检查原始应用 Key、有效期、模型目录权限和网络。
- 401/403：检查所选服务的权限、Allowed APIs、内容规则和余额，不要发送 Key 给他人。
- 429：降低并发、稍后再试；不确定是否受理的创建请求应先核对历史。
- 结果未完成：继续查询同服务原任务 ID，保留 trace ID。

## 维护和验证

共享网络、任务与错误逻辑只保留一份，服务专用参数适配和工具控件沿用原实现。保留 MIT 许可及源码来源记录。

```sh
python -m pip install -r requirements.txt pytest ruff
python -m pytest
ruff check .
ruff format --check .
python scripts/sync_models.py --refresh
python scripts/sync_models.py --check
dify plugin package . -o ../ace_media-0.1.1.difypkg
```

正常测试会通过真实 Dify SDK 加载全部工具，重放源请求契约并检查任务状态及模型控件一致性。测试使用离线响应，不调用付费服务。没有把新整合包声称为已完成 Dify Cloud 或新付费生成验收。源码/打包验证与官方上架是不同阶段。

每日源码任务只读公开元数据，更新模型选项并在变化时创建待审核的 Dev bot PR。遇到接口或默认模型弃用会停下交由审核，不自动换模型；市场审核和工作区升级仍须正常完成。
