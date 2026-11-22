from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.client import AceMediaClient, AceMediaError


class AceMediaProvider(ToolProvider):
    def _validate_credentials(self, credentials):
        try:
            AceMediaClient(credentials.get("acedata_bearer_token")).validate()
        except (ValueError, AceMediaError) as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from None
