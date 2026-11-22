"""Refresh model choices from the public API rows already bound to each tool."""

import argparse
import concurrent.futures
import json
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"model", "version", "mv", "model_version", "model_name", "face_model_version"}


def read_api(api_id):
    url = f"https://platform.acedata.cloud/api/v1/apis/{api_id}/"
    result = requests.get(url, timeout=(10, 30), allow_redirects=False)
    result.raise_for_status()
    api = result.json()
    if api.get("stage") == "Deprecated":
        raise ValueError(f"Review the deprecated API {api_id}; do not silently replace it")
    return api_id, api


def model_options(api, path):
    definition = api["definition"]
    paths = definition["paths"]
    if path not in paths:
        if path not in {api.get("path"), api.get("path2")}:
            raise ValueError(f"API {api['id']} no longer declares {path}")
        path = api["path"]
    operation = paths[path].get("post", paths[path].get("get", {}))
    content = operation.get("requestBody", {}).get("content", {})
    schema = next(iter(content.values()), {}).get("schema", {})
    return {
        field: value["enum"]
        for field, value in schema.get("properties", {}).items()
        if field in FIELDS and value.get("enum")
    }


def public_snapshot(contracts, acemusic):
    ids = sorted({entry["api_id"] for entry in contracts.values()} | {acemusic["api_id"]})
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        apis = dict(pool.map(read_api, ids))
    snapshot = {}
    for name, endpoint in contracts.items():
        options = model_options(apis[endpoint["api_id"]], endpoint["path"])
        if options:
            snapshot[name] = {
                "api_id": endpoint["api_id"],
                "path": endpoint["path"],
                "options": options,
            }
    snapshot["acemusic"] = {
        "api_id": acemusic["api_id"],
        "path": "/acemusic/audios",
        "options": model_options(apis[acemusic["api_id"]], "/acemusic/audios"),
    }
    return snapshot


def apply(snapshot, root=ROOT, check=False):
    contract_path = root / "tools/api_contracts.json"
    contracts = json.loads(contract_path.read_text())
    files = {}
    picker_by_name = {}
    for path in (root / "tools").glob("*.yaml"):
        tool = yaml.safe_load(path.read_text())
        picker_by_name[tool["identity"]["name"]] = (path, tool)
    for name, entry in snapshot.items():
        if name == "acemusic":
            continue
        endpoint = contracts[name]
        for field, models in entry["options"].items():
            if not models or len(models) != len(set(models)):
                raise ValueError(f"Invalid model options for {name}/{field}")
            if field not in endpoint["properties"]:
                raise ValueError(f"Review the newly added model control {name}/{field}")
            default = endpoint.get("defaults", {}).get(field)
            if default not in (None, "") and default not in models:
                raise ValueError(f"Review the retired default for {name}/{field}")
            endpoint["properties"][field]["enum"] = models
            if field in endpoint["schema"].get("properties", {}):
                endpoint["schema"]["properties"][field]["enum"] = models
            if name in picker_by_name:
                path, tool = picker_by_name[name]
                parameter = next((p for p in tool["parameters"] if p["name"] == field), None)
                if parameter is None:
                    continue
                existing = {str(option["value"]): option for option in parameter.get("options", [])}
                if parameter.get("type") == "select":
                    if (
                        parameter.get("default") not in (None, "")
                        and parameter["default"] not in models
                    ):
                        raise ValueError(f"Review the retired picker default for {name}/{field}")
                    parameter["options"] = [
                        existing.get(
                            str(value),
                            {"value": value, "label": {"en_US": str(value), "zh_Hans": str(value)}},
                        )
                        for value in models
                    ]
                    files[str(path.relative_to(root))] = yaml.safe_dump(
                        tool, allow_unicode=True, sort_keys=False
                    )
    ace_models = snapshot["acemusic"]["options"]["model"]
    files["tools/acemusic_models.json"] = (
        json.dumps({"api_id": snapshot["acemusic"]["api_id"], "models": ace_models}, indent=2)
        + "\n"
    )
    for name in ("acemusic_generate", "acemusic_custom"):
        path, tool = picker_by_name[name]
        parameter = next(p for p in tool["parameters"] if p["name"] == "model")
        parameter["options"] = [
            {"value": value, "label": {"en_US": value, "zh_Hans": value}} for value in ace_models
        ]
        files[str(path.relative_to(root))] = yaml.safe_dump(
            tool, allow_unicode=True, sort_keys=False
        )
    files["tools/api_contracts.json"] = json.dumps(contracts, ensure_ascii=False, indent=2) + "\n"
    files["tests/published-model-options.json"] = (
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    )
    changed = []
    for relative, expected in files.items():
        path = root / relative
        if path.exists() and path.read_text() == expected:
            continue
        changed.append(relative)
        if not check:
            path.write_text(expected)
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    snapshot = (
        public_snapshot(
            json.loads((ROOT / "tools/api_contracts.json").read_text()),
            json.loads((ROOT / "tools/acemusic_models.json").read_text()),
        )
        if args.refresh
        else json.loads((ROOT / "tests/published-model-options.json").read_text())
    )
    changed = apply(snapshot, check=args.check)
    print(f"{len(snapshot)} published operation model lists; {len(changed)} files changed")
    if args.check and changed:
        raise SystemExit("Model declarations need regeneration: " + ", ".join(changed))


if __name__ == "__main__":
    main()
