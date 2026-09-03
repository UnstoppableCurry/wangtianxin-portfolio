#!/usr/bin/env python3
"""Validate generated site: JSON, routes, apps, and no fabricated URLs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from site_data import ROOT, build_context, extract_bilibili_demo

DIST = ROOT / "dist"
FORBIDDEN_URL_PATTERNS = [
    r"example\.com",
    r"placeholder\.(com|net|org)",
    r"your-domain",
    r"lorem ipsum",
    r"TODO\.com",
    r"https?://localhost",
    r"127\.0\.0\.1",
]
APP_IDS = ["6769751978", "6766811028", "6759594555"]
REQUIRED_DEMOS = [
    "https://onnx2anything.com",
    "https://sudoku.app",
    "https://apps.apple.com/app/id6769751978",
    "https://apps.apple.com/app/ai-agent-atlas/id6766811028",
    "https://unstoppablecurry.github.io/ai-agent-atlas-site/",
    "https://apps.apple.com/cn/app/id6759594555",
    "https://unstoppablecurry.github.io/kimi-k3-learn-explorer/",
    "https://unstoppablecurry.github.io/convertmodel-docs/",
    "https://www.bilibili.com/video/BV1bL4y1s7Fr",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing file {path}")
    return path.read_text(encoding="utf-8")


def test_json_loads() -> dict:
    ctx = build_context()
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    tokens = json.loads((ROOT / "data" / "tokens.json").read_text(encoding="utf-8"))
    apps = json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))
    if len(catalog) != 66:
        fail(f"catalog should have 66 items, got {len(catalog)}")
    if ctx["counts"]["all"] != 66:
        fail(f"enriched catalog should have 66 items, got {ctx['counts']['all']}")
    if len(apps) != 3:
        fail(f"apps.json should have 3 products, got {len(apps)}")
    if int(tokens["totals"]["all"]) != 20863761904:
        fail("token totals.all changed or failed to load")
    return ctx


def test_pages(ctx: dict) -> None:
    home = read(DIST / "index.html")
    archive = read(DIST / "archive" / "index.html")
    not_found = read(DIST / "404.html")
    sitemap = read(DIST / "sitemap.xml")
    robots = read(DIST / "robots.txt")
    favicon = DIST / "assets" / "img" / "favicon.svg"
    if not favicon.is_file():
        fail("favicon missing")
    if "sitemap.xml" not in robots:
        fail("robots.txt missing sitemap")
    if "页不在册" not in not_found:
        fail("404 page missing Chinese copy")

    for item in ctx["items"]:
        if item["name"] not in archive:
            fail(f"archive does not render {item['name']}")
        page = DIST / "p" / item["slug"] / "index.html"
        html = read(page)
        if item["name"] not in html:
            fail(f"detail page missing name for {item['name']}")
        if f"p/{item['slug']}" not in sitemap:
            fail(f"sitemap missing {item['slug']}")
        if item["private"]:
            if "私有仓库，需要权限" not in html:
                fail(f"private repo not marked: {item['name']}")
            if item.get("readmeExcerpt"):
                fail(f"private README should be empty in source: {item['name']}")
        loc = f"p/{item['slug']}/index.html"
        if loc.count(item["name"]) < 1:
            fail(f"detail filename/route issue {item['name']}")

    if home.count('class="archive-item"') != 0:
        fail("home should not dump the full archive grid")
    if archive.count("data-item") != 66:
        fail(f"archive should list 66 items, got {archive.count('data-item')}")
    if home.count('class="feature"') != 7:
        fail(f"home should feature 7 demo-first works, got {home.count('class=\"feature\"')}")
    cat_sum = sum(c["count"] for c in ctx["categories"])
    if cat_sum != 66:
        fail(f"category counts should sum to 66, got {cat_sum}")
    seal = len(re.findall(r'data-category="vision-seal"', archive))
    if seal != 12:
        fail(f"archive should mark 12 vision-seal items, got {seal}")
    demo_marked = len(re.findall(r'data-demo="1"', archive))
    if demo_marked != ctx["counts"]["demo"]:
        fail("archive demo flags should match enriched demo count")


def test_apps_and_urls(ctx: dict) -> None:
    pages = [DIST / "index.html", DIST / "archive" / "index.html"]
    pages.extend(DIST / "p" / item["slug"] / "index.html" for item in ctx["items"])
    blob = "\n".join(read(path) for path in pages)
    hrefs = re.findall(r'href="([^"]+)"', blob)
    href_blob = "\n".join(hrefs)
    for app_id in APP_IDS:
        if app_id not in blob:
            fail(f"missing App Store id {app_id}")
    for url in REQUIRED_DEMOS:
        if url not in blob:
            fail(f"missing required demo/product URL {url}")
    for pattern in FORBIDDEN_URL_PATTERNS:
        if re.search(pattern, href_blob, flags=re.I):
            fail(f"forbidden placeholder href matched: {pattern}")
    if re.search(r"https?://doi\.org|10\.xxxx", href_blob, flags=re.I):
        fail("do not invent DOI links")
    face = next(item for item in ctx["items"] if item["name"] == "Face-payment")
    bili = extract_bilibili_demo(face.get("readmeExcerpt") or "")
    if bili != "https://www.bilibili.com/video/BV1bL4y1s7Fr":
        fail(f"Face-payment Bilibili demo parse failed: {bili}")
    if not face["has_demo"]:
        fail("Face-payment should count as having a demo")


def test_tokens_exact(ctx: dict) -> None:
    home = read(DIST / "index.html")
    if "20,863,761,904" not in home and "20863761904" not in home:
        fail("exact token total missing on home")
    domains = ctx["domains"]
    if domains["convertmodel"]["all"] != 5587373996 + 2332268115:
        fail("ConvertModel domain should be 中转生意 + convert")
    if domains["seal"]["all"] != 867055748 + 877354616:
        fail("seal domain should be 印模 + yolo")
    if domains["memeory"]["all"] != 478327077:
        fail("memeory domain mismatch")
    if "中转生意" not in home or "印模" not in home:
        fail("domain source names should appear")


def test_no_private_readme_leak(ctx: dict) -> None:
    for item in ctx["items"]:
        if not item["private"]:
            continue
        html = read(DIST / "p" / item["slug"] / "index.html")
        if "私有仓库不展示 README" not in html:
            fail(f"private detail missing README guard: {item['name']}")


def main() -> None:
    if not DIST.exists():
        fail("dist/ missing; run python3 scripts/build.py first")
    ctx = test_json_loads()
    test_pages(ctx)
    test_apps_and_urls(ctx)
    test_tokens_exact(ctx)
    test_no_private_readme_leak(ctx)
    print(
        "PASS: "
        f"{ctx['counts']['all']} catalog items, "
        f"{ctx['counts']['public']} public / {ctx['counts']['private']} private, "
        f"{ctx['counts']['demo']} with demo, "
        f"{ctx['counts']['apps']} App Store products, "
        "all detail routes present."
    )


if __name__ == "__main__":
    main()
