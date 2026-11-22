from dify_plugin import Tool

from tools.client import AceMediaClient


class DreaminaGetTasks(Tool):
    def _invoke(self, tool_parameters):
        result = AceMediaClient(self.runtime.credentials.get("acedata_bearer_token", "")).invoke(
            "dreamina_get_tasks", tool_parameters
        )
        yield self.create_json_message(result)
        for field, value in result.items():
            yield self.create_variable_message(field, value)
        for url in result["media_urls"]:
            yield self.create_link_message(url)
