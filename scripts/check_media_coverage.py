"""Detect newly published media operations that still need a native Dify adapter."""

import argparse
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
URL = "https://platform.acedata.cloud/api/v1/models/catalog/"
# These standard interfaces are implemented by the companion model-provider
# source PR, not by another duplicate Tools wrapper. They are not a claim that
# that pending model-provider package is already published in Marketplace.
COMPANION_APIS = {
    "078d0146-f820-4617-b98e-47ba15a93d60": "text-to-speech",
    "60f037ff-7d2f-4ea4-ae42-feba542c8cb2": "speech-to-text",
    "a0840c8a-2b9a-4407-8aaf-0057f0e1f65c": "text-embedding",
}


def snapshot(catalog):
    return {
        "source": URL,
        "companion_provider": {
            "plugin_id": "acedatacloud/acedatacloud",
            "source_pr": "https://github.com/AceDataCloud/ModelProviderDify/pull/14",
            "coverage_scope": "source contracts only; Marketplace status is tracked separately",
            "apis": COMPANION_APIS,
        },
        "items": [
            {
                key: item.get(key)
                for key in ("key", "id", "kind", "modality", "service_alias", "api_ids")
            }
            for item in catalog["items"]
            if item["modality"] in {"image", "video", "audio", "search", "embedding"}
        ],
    }


def missing_operations(catalog, root=ROOT):
    contracts = json.loads((root / "tools/api_contracts.json").read_text())
    acemusic = json.loads((root / "tools/acemusic_operations.json").read_text())
    covered = {entry["api_id"] for entry in contracts.values()} | {
        entry["api_id"] for entry in acemusic.values()
    }
    missing = []
    for item in catalog["items"]:
        unknown = set(item["api_ids"]) - covered - COMPANION_APIS.keys()
        if unknown:
            missing.append({**item, "missing_api_ids": sorted(unknown)})
    return missing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    path = ROOT / "tests/public-media-catalog.json"
    if args.refresh:
        response = requests.get(URL, timeout=(10, 30), allow_redirects=False)
        response.raise_for_status()
        data = snapshot(response.json())
    else:
        data = json.loads(path.read_text())
    missing = missing_operations(data)
    if missing:
        raise SystemExit("Published operations need native adapters: " + json.dumps(missing))
    if args.refresh:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(
        f"{len(data['items'])} public media/embedding items; no uncovered API operations (including the explicit companion-provider source scope)"
    )


if __name__ == "__main__":
    main()
