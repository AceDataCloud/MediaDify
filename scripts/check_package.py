"""Inspect the actual distribution archive; never infer package safety from Git status."""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import yaml


def check(path):
    package_path = Path(path)
    archive = zipfile.ZipFile(path)
    names = archive.namelist()
    forbidden = {
        ".git",
        ".github",
        ".gitignore",
        ".difyignore",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "tests",
        "scripts",
        ".DS_Store",
    }
    bad = [
        name
        for name in names
        if set(Path(name).parts) & forbidden
        or any(part.startswith(".env") for part in Path(name).parts)
        or name.endswith((".pyc", ".log", ".exe"))
    ]
    if bad:
        raise ValueError("Development/private files in package: " + ", ".join(bad))
    manifest = yaml.safe_load(archive.read("manifest.yaml"))
    provider = yaml.safe_load(archive.read("provider/ace_media.yaml"))
    assert manifest["author"] == "acedatacloud" and manifest["name"] == "ace_media"
    assert manifest["plugins"]["tools"] == ["provider/ace_media.yaml"]
    assert len(manifest["tags"]) <= 3 and manifest["tags"]
    expected = {
        name
        for source in json.loads(Path("tests/source-tools.json").read_text())
        for name in source["tool_names"]
    }
    retired = {row["tool"] for row in json.loads(Path("tests/retired-tools.json").read_text())}
    actual = {yaml.safe_load(archive.read(path))["identity"]["name"] for path in provider["tools"]}
    assert actual == expected - retired
    assert manifest.get("verified") is not True
    for path in (
        "README.md",
        "PRIVACY.md",
        "LICENSE",
        "_assets/icon.png",
        "tools/api_contracts.json",
        "tools/acemusic_operations.json",
    ):
        assert path in names
    return {
        "file": str(package_path),
        "version": manifest["version"],
        "native_tools": len(actual),
        "files": len(names),
        "sha256": hashlib.sha256(package_path.read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    print(json.dumps(check(sys.argv[1]), indent=2))
