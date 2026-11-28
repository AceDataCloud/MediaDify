from dify_plugin import Tool

from tools.acemusic_client import invoke


class AceMusicListAssets(Tool):
    def _invoke(self, tool_parameters):
        result = invoke(
            self.runtime.credentials.get("acedata_bearer_token"),
            "list_assets",
            tool_parameters,
        )
        yield self.create_json_message(result)
        yield self.create_variable_message("result", result)
