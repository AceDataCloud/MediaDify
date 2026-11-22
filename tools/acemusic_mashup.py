from dify_plugin import Tool

from tools.acemusic_client import invoke


class AceMusicMashup(Tool):
    def _invoke(self, tool_parameters):
        result = invoke(
            self.runtime.credentials.get("acedata_bearer_token"),
            "mashup",
            tool_parameters,
        )
        yield self.create_json_message(result)
        yield self.create_variable_message("result", result)
        task_id = result.get("task_id") or result.get("id")
        if isinstance(task_id, str):
            yield self.create_variable_message("task_id", task_id)
