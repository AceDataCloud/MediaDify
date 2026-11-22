# Privacy policy — Ace Media and Tools

Effective date: 2026-11-23. Maintainer: Ace Data Cloud, dev@acedata.cloud.

## Data sent to Ace Data Cloud

The plugin sends the configured application API key in an HTTPS Authorization
header to the fixed `api.acedata.cloud` host. Saving a credential reads the model
catalog only. It does not generate media, index documents or run a face operation.
Saving a key does not establish authorization to use every service: account
permissions, Allowed APIs, balance and the chosen operation still apply.

When a user invokes a tool, it sends that tool's input and requested parameters:
text prompts, lyrics, search queries, selected models, reference-image/audio/video
URLs, task and track IDs, voice references, and callback URLs when supplied.
The API may retrieve user-provided reference URLs as part of the requested
operation. The plugin does not itself fetch arbitrary reference URLs, run shell
commands, browse websites or connect to user-selected API hosts.

Face tools can process identifiable face images and return facial landmarks or
transformed images. These inputs and outputs may be biometric or otherwise
sensitive personal data. Voice references, photos, video, lyrics and prompts can
also contain personal information. Users must have the necessary rights and
consent for the material they provide; do not use these tools to impersonate
people or process material without authorization. These capabilities are
disclosed for the Marketplace's higher-risk review.

Selected tools can create or delete tasks/personas within the configured key's service permissions. Destructive operations require their explicit confirmation control; the plugin does not delete unrelated resources as part of installation or migration.

The API also receives ordinary connection metadata, such as the Dify server's IP
address and API usage needed to operate and bill the selected service.

## Storage, logging and recipients

The plugin adds no database, analytics or telemetry. It does not intentionally
log API keys, prompts, reference contents or raw service errors. Credentials and
input exist in memory for the request; results and task IDs are returned to Dify.
Known internal/request/credential fields are removed from tool results. Dify
manages stored credentials, workflow inputs, outputs and logs under the user's
workspace and deployment policies.

The only direct external API recipient is Ace Data Cloud. Processing providers,
retention and data rights on that service are governed by the
[Ace Data Cloud privacy policy](https://platform.acedata.cloud/privacy). This
plugin does not promise zero retention by the API service. A supplied callback
URL instructs the API to deliver the requested task result to that destination;
use a destination you control and are authorized to receive the result.

The source repository's optional synchronization job reads public API metadata
from `platform.acedata.cloud`. That job is not part of the runtime plugin and does
not receive Dify credentials, workflow inputs or private account data.

## Your controls and requests

Create a key for the intended workspace with suitable API, expiry and usage
restrictions. Limit who can use the Dify provider credential. Remove that
credential from Dify or revoke the key in Ace Data Cloud to stop future use.
Removing the plugin does not erase already stored Dify or API-side data.

Contact dev@acedata.cloud for API-side data-rights or privacy requests, and the
Dify workspace administrator for data retained by that deployment.
