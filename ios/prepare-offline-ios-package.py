#!/usr/bin/env python3
"""Build the self-contained WebApp snapshot used by the iOS test shell.

The normal GitHub Pages build is never modified. This script copies the current
web game plus every asset into the Xcode project, patches only that copy so
high-resolution terrain requests go through the native iOS cache, and bundles a
5x5 Svalbard terrain block for offline startup/testing.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
IOS_APP = ROOT / "ios" / "ArcticResearch" / "ArcticResearch"
WEBAPP = IOS_APP / "WebApp"
TILE_KM = 128
TILE_PIXELS = 1024
SVALBARD_CENTER_TILE = (2, 9)
SVALBARD_RADIUS_TILES = 2
CACHE_LIMIT_MB = 150

CORE_FILES = [
    "index.html",
    "style.css",
    "coast-data.js",
    "river-data.js",
    "wildlife-data.js",
    "visual-assets-data.js",
    "photo-pass-version.js",
    "expedition.js",
    "sprite-atlas-data.js",
    "glacier-data.js",
    "frame-guard.js",
    "game.js",
    "glacier-overlay-v2.js",
    "manifest.webmanifest",
]


def source_revision() -> str:
    env = os.environ.get("GITHUB_SHA", "").strip()
    if env:
        return env
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def copy_web_snapshot() -> None:
    if WEBAPP.exists():
        shutil.rmtree(WEBAPP)
    WEBAPP.mkdir(parents=True)

    missing = [name for name in CORE_FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit(f"Missing required game files: {', '.join(missing)}")
    for name in CORE_FILES:
        shutil.copy2(ROOT / name, WEBAPP / name)

    assets = ROOT / "assets"
    if not assets.is_dir():
        raise SystemExit("Missing assets directory")
    shutil.copytree(assets, WEBAPP / "assets", dirs_exist_ok=True)


def patch_native_map_transport() -> None:
    path = WEBAPP / "game.js"
    text = path.read_text(encoding="utf-8")
    start_marker = "  function terrainTileUrl(tile,year=2024){"
    end_marker = "  const terrainPixelIsLand="
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate terrainTileUrl in packaged game.js")

    replacement = """  function terrainTileUrl(tile,year=2024){
    // Native iOS builds use a stable app-local URL. The Swift shell serves
    // preloaded Svalbard tiles first, then a persistent 150 MB on-device cache,
    // and only then downloads GEBCO terrain. The browser build keeps using WMS.
    if(window.AR_IOS_OFFLINE_SHELL===true)return`arsapp://local/_terrain/${year}/${tile.ix}/${tile.iy}.png`;
    const minE=Math.round(tile.minX*1000),maxE=Math.round(tile.maxX*1000),minN=Math.round(-tile.maxY*1000),maxN=Math.round(-tile.minY*1000),layer=`GEBCO_NORTH_POLAR_VIEW_bed_${year}`;
    return`https://wms.gebco.net/${year}/north-polar/mapserv?BBOX=${minE}%2C${minN}%2C${maxE}%2C${maxN}&crs=EPSG%3A3996&format=image%2Fpng&height=${TERRAIN_TILE_PIXELS}&layers=${layer}&request=getmap&service=wms&version=1.3.0&width=${TERRAIN_TILE_PIXELS}`;
  }
"""
    text = text[:start] + replacement + text[end:]

    old_version = "const GAME_VERSION='expedition-23p2-photo-review'"
    if old_version in text:
        text = text.replace(old_version, "const GAME_VERSION='expedition-23aq-ios-offline1'", 1)

    path.write_text(text, encoding="utf-8")


def terrain_url(year: int, ix: int, iy: int) -> str:
    min_x = ix * TILE_KM
    min_y = iy * TILE_KM
    max_x = min_x + TILE_KM
    max_y = min_y + TILE_KM
    params = {
        "BBOX": f"{min_x * 1000},{-max_y * 1000},{max_x * 1000},{-min_y * 1000}",
        "crs": "EPSG:3996",
        "format": "image/png",
        "height": str(TILE_PIXELS),
        "layers": f"GEBCO_NORTH_POLAR_VIEW_bed_{year}",
        "request": "getmap",
        "service": "wms",
        "version": "1.3.0",
        "width": str(TILE_PIXELS),
    }
    return f"https://wms.gebco.net/{year}/north-polar/mapserv?{urllib.parse.urlencode(params)}"


def is_png(data: bytes) -> bool:
    return len(data) > 1024 and data.startswith(b"\x89PNG\r\n\x1a\n")


def fetch_tile(tile: tuple[int, int]) -> tuple[str, int]:
    ix, iy = tile
    year = 2024
    destination = WEBAPP / "assets" / "map" / "svalbard" / f"terrain-{year}-{ix}-{iy}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        terrain_url(year, ix, iy),
        headers={"User-Agent": "ArcticResearchSimulator/0.1 offline-test-packager"},
    )
    last_error: Exception | None = None
    max_attempts = 6
    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            if not is_png(data):
                raise RuntimeError(f"response was not a PNG ({len(data)} bytes)")
            destination.write_bytes(data)
            return destination.name, len(data)
        except Exception as exc:
            last_error = exc
            if attempt < max_attempts:
                time.sleep(2.0 * attempt)
    raise RuntimeError(f"Failed Svalbard tile {ix},{iy}: {last_error}")


def download_svalbard_tiles() -> list[dict[str, int | str]]:
    center_x, center_y = SVALBARD_CENTER_TILE
    tiles = [
        (ix, iy)
        for ix in range(center_x - SVALBARD_RADIUS_TILES, center_x + SVALBARD_RADIUS_TILES + 1)
        for iy in range(center_y - SVALBARD_RADIUS_TILES, center_y + SVALBARD_RADIUS_TILES + 1)
    ]
    results: list[dict[str, int | str]] = []
    # GEBCO occasionally closes bursts of WMS requests. Keep concurrency low so
    # package generation is reliable and courteous to the public service.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_map = {executor.submit(fetch_tile, tile): tile for tile in tiles}
        for future in concurrent.futures.as_completed(future_map):
            ix, iy = future_map[future]
            name, size = future.result()
            print(f"Downloaded Svalbard terrain {ix},{iy}: {size / 1024:.0f} KiB")
            results.append({"ix": ix, "iy": iy, "file": name, "bytes": size})
    return sorted(results, key=lambda item: (int(item["ix"]), int(item["iy"])))


def write_manifest(tiles: list[dict[str, int | str]]) -> None:
    asset_bytes = sum(p.stat().st_size for p in (WEBAPP / "assets").rglob("*") if p.is_file())
    manifest = {
        "package": "Arctic Research iOS Offline Test",
        "packageVersion": "23aq-ios-offline1",
        "sourceRevision": source_revision(),
        "offline": {
            "gameLogic": True,
            "photos": True,
            "sounds": True,
            "arcticOverviewMap": True,
            "svalbardHighResolution": True,
            "highResolutionAwayFromSvalbard": "download-on-demand-and-cache",
        },
        "terrain": {
            "source": "GEBCO 2024 North Polar WMS / EPSG:3996",
            "tileKm": TILE_KM,
            "tilePixels": TILE_PIXELS,
            "preloadedTileCount": len(tiles),
            "preloadedCenterTile": list(SVALBARD_CENTER_TILE),
            "preloadedRadiusTiles": SVALBARD_RADIUS_TILES,
            "runtimeCacheLimitMB": CACHE_LIMIT_MB,
            "preloadedTiles": tiles,
        },
        "bundledAssetBytes": asset_bytes,
    }
    (WEBAPP / "mobile-package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-map-download",
        action="store_true",
        help="Prepare the app snapshot without downloading the 25 bundled Svalbard terrain tiles.",
    )
    args = parser.parse_args()

    print("Preparing offline Arctic Research web snapshot...")
    copy_web_snapshot()
    patch_native_map_transport()
    tiles: list[dict[str, int | str]] = []
    if not args.skip_map_download:
        tiles = download_svalbard_tiles()
        if len(tiles) != 25:
            raise SystemExit(f"Expected 25 Svalbard tiles, got {len(tiles)}")
    write_manifest(tiles)

    total_bytes = sum(p.stat().st_size for p in WEBAPP.rglob("*") if p.is_file())
    print(f"Offline WebApp ready: {total_bytes / (1024 * 1024):.1f} MiB")
    print(f"Location: {WEBAPP}")


if __name__ == "__main__":
    main()
