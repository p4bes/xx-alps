#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
DIST = REPO_ROOT / "dist"

ASSET_EXCLUDES = {
    ".DS_Store",
    "exxeta_logo_crop.jpg",
    "exxeta_logo_mask_test.png",
}


def copytree_filtered(src: Path, dst: Path, excludes: set[str] | None = None) -> None:
    excludes = excludes or set()

    def ignore(_path: str, names: list[str]) -> list[str]:
        return [name for name in names if name in excludes or name == "__pycache__"]

    shutil.copytree(src, dst, ignore=ignore)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    shutil.copy2(ROOT / "alpen_etappen_karte.html", DIST / "index.html")
    shutil.copy2(ROOT / "alpen_etappen_karte.html", DIST / "alpen_etappen_karte.html")
    shutil.copy2(ROOT / "alpen_etappen_varianten.geojson", DIST / "alpen_etappen_varianten.geojson")
    shutil.copy2(ROOT / "alpen_etappen_gpx.zip", DIST / "alpen_etappen_gpx.zip")
    copytree_filtered(ROOT / "assets", DIST / "assets", ASSET_EXCLUDES)
    copytree_filtered(ROOT / "gpx", DIST / "gpx")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    files = sorted(path.relative_to(DIST) for path in DIST.rglob("*") if path.is_file())
    print(f"Prepared GitHub Pages artifact in {DIST} ({len(files)} files).")


if __name__ == "__main__":
    main()
