"""Bundled published API contracts, shared by all native tools."""

import json
from pathlib import Path

ENDPOINTS = json.loads(Path(__file__).with_suffix(".json").read_text())
TASK_PATHS = {entry["task_path"] for entry in ENDPOINTS.values() if entry.get("task_path")}
