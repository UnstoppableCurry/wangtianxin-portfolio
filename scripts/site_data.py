"""Load and enrich portfolio data. Never invent metrics or private README text."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from chronicle import build_chronicle

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

CATEGORY_LABELS = {
    "vision-seal": "印章视觉",
    "ocr-doc": "OCR 文档",
    "agent-infra": "Agent 基础设施",
    "convertmodel": "ConvertModel",
    "app-store": "App Store",
    "data-nlp": "数据与 NLP",
    "research": "研究",
    "other": "其他",
}

CATEGORY_ORDER = [
    "vision-seal",
    "ocr-doc",
    "agent-infra",
    "convertmodel",
    "app-store",
    "data-nlp",
    "research",
    "other",
]

DOMAIN_CONVERT = ("中转生意", "convert")
DOMAIN_SEAL = ("印模", "yolo")
DOMAIN_MEMEORY = ("memeory",)

# App Store / product URLs from data/apps.json, attached only to matching catalog names.
APP_ATTACHMENTS = {
    "sudoku-app": "Sudoku Logic Refined",
    "sudoku-site": "Sudoku Logic Refined",
    "ai-agent-atlas": "AI Agent Atlas",
    "ai-agent-atlas-site": "AI Agent Atlas",
    "DentalExamPrep-iOS": "口腔主治题库",
    "dentalexamprep": "口腔主治题库",
    "dental-exam-app": "口腔主治题库",
}

TECH_TERMS = [
    "WebAssembly",
    "ONNX",
    "NCNN",
    "MNN",
    "TNN",
    "TFLite",
    "PaddleLite",
    "PaddleOCR",
    "OpenVINO",
    "OpenVino",
    "YOLOv8",
    "YOLOv3",
    "YOLO",
    "ArcFace",
    "PyTorch",
    "Three.js",
    "Capacitor",
    "SwiftUI",
    "LibreOffice",
    "pdfplumber",
    "WebSocket",
    "SQLite",
    "FTS5",
    "Claude Code",
    "Codex",
    "ncnn",
    "OpenCL",
    "ResNet",
    "Transformers",
    "Hugging Face",
    "RWKV",
    "UFormer",
    "Playwright",
    "DingTalk",
    "OpenClaw",
    "AnythingLLM",
    "Bun",
    "MCP",
]

FEATURED = [
    {
        "id": "onnx2anything",
        "kicker": "端侧转换",
        "title": "ONNX2Anything",
        "lede": "在浏览器里把 ONNX 转成 NCNN / MNN / TNN / TFLite / PaddleLite，模型不离开本机。",
        "repo": "onnx2anything",
    },
    {
        "id": "sudoku",
        "kicker": "App Store",
        "title": "Sudoku Logic Refined",
        "lede": "数独 iOS / macOS 应用与产品站点。仓库为私有，公开入口是 App Store 与 sudoku.app。",
        "repo": "sudoku-app",
        "extra_repos": ["sudoku-site"],
    },
    {
        "id": "atlas",
        "kicker": "App Store",
        "title": "AI Agent Atlas",
        "lede": "交互式地图，解释当代 AI coding agent 如何工作；含 App Store 产品与公开站点。",
        "repo": "ai-agent-atlas",
        "extra_repos": ["ai-agent-atlas-site"],
    },
    {
        "id": "dental",
        "kicker": "App Store",
        "title": "口腔主治题库",
        "lede": "口腔主治医师考试题库 iOS 应用。源码与支持页仓库为私有，公开入口是 App Store。",
        "repo": "dental-exam-app",
        "extra_repos": ["DentalExamPrep-iOS", "dentalexamprep"],
    },
    {
        "id": "kimi-k3",
        "kicker": "学习工具",
        "title": "Kimi K3 架构 3D 探索器",
        "lede": "用真实三维结构而不是隐喻，看 token、注意力、MoE 与训练数据流。",
        "repo": "kimi-k3-learn-explorer",
    },
    {
        "id": "convertmodel",
        "kicker": "文档 / 中转",
        "title": "ConvertModel 文档与中继说明",
        "lede": "客户端文档站，以及 Claude Code / Codex 在 OpenAI 兼容与 Anthropic 端点上的中继笔记。",
        "repo": "convertmodel-docs",
        "extra_repos": ["convertmodel-claude-code-codex-relay"],
    },
    {
        "id": "face-payment",
        "kicker": "视觉演示",
        "title": "Face-payment",
        "lede": "YOLO + ArcFace 人脸支付学习实现。公开效果演示来自仓库 README 中的 Bilibili 链接。",
        "repo": "Face-payment",
    },
]


def load_json(name: str) -> Any:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_catalog() -> list[dict[str, Any]]:
    data = load_json("catalog.json")
    if not isinstance(data, list):
        raise ValueError("catalog.json must be a list")
    return data


def load_tokens() -> dict[str, Any]:
    data = load_json("tokens.json")
    if not isinstance(data, dict):
        raise ValueError("tokens.json must be an object")
    return data


def load_apps() -> list[dict[str, Any]]:
    data = load_json("apps.json")
    if not isinstance(data, list):
        raise ValueError("apps.json must be a list")
    return data


def slug_for(name: str) -> str:
    return name


def year_of(iso: str | None) -> str:
    if not iso:
        return ""
    return iso[:4]


def is_github_url(url: str | None) -> bool:
    if not url:
        return False
    return "github.com" in url.lower()


def clean_url(url: str) -> str:
    url = url.strip()
    url = re.sub(r"[)\],.]+$", "", url)
    url = url.split("?", 1)[0] if "bilibili.com" in url else url
    return url


def extract_bilibili_demo(readme: str) -> str | None:
    matches = re.findall(r"https?://(?:www\.)?bilibili\.com/video/BV[0-9A-Za-z]+", readme)
    if matches:
        return clean_url(matches[0])
    return None


def first_meaningful_paragraph(text: str) -> str:
    if not text:
        return ""
    stripped = re.sub(r"<[^>]+>", " ", text)
    lines: list[str] = []
    for raw in stripped.splitlines():
        line = raw.strip()
        if not line:
            if lines:
                break
            continue
        if line.startswith(("#", "```", "|", "![", "[![", "---", "> [", "flowchart")):
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"[*_`]+", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"\s+", " ", line).strip()
        if len(line) < 8:
            continue
        if line.lower().startswith(("license", "mit ")):
            continue
        lines.append(line)
        if sum(len(x) for x in lines) >= 80:
            break
    return " ".join(lines).strip()


def extract_problem(readme: str) -> str:
    if not readme:
        return ""
    match = re.search(
        r"解决什么问题\s*\n+(.+?)(?:\n#{1,3}\s|\Z)",
        readme,
        flags=re.S,
    )
    if match:
        para = first_meaningful_paragraph(match.group(1))
        if para:
            return para
    why = re.search(
        r"(?:Why [^\n?]+\??|为什么[^\n]*)\s*\n+(.+?)(?:\n#{1,3}\s|\Z)",
        readme,
        flags=re.S,
    )
    if why:
        para = first_meaningful_paragraph(why.group(1))
        if para:
            return para
    return ""


def extract_tech(language: str | None, blob: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    if language:
        found.append(language)
        seen.add(language.lower())
    for term in TECH_TERMS:
        if term.lower() in seen:
            continue
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])", blob, flags=re.I):
            found.append(term)
            seen.add(term.lower())
    return found


def match_token_projects(repo_name: str, top_projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rn = repo_name.strip().lower().replace("_", "-")
    hits = []
    for project in top_projects:
        pn = str(project.get("project") or "").strip().lower().replace("_", "-")
        if not pn:
            continue
        if pn == rn:
            hits.append(project)
    return hits


def domain_totals(top_projects: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    index = {p["project"]: p for p in top_projects}

    def sum_keys(keys: tuple[str, ...]) -> dict[str, int]:
        acc = {"all": 0, "input": 0, "output": 0, "cacheRead": 0, "cacheCreate": 0, "sessions": 0}
        matched = []
        for key in keys:
            row = index.get(key)
            if not row:
                continue
            matched.append(key)
            for field in acc:
                acc[field] += int(row.get(field) or 0)
        acc["keys"] = matched  # type: ignore[assignment]
        return acc

    return {
        "convertmodel": sum_keys(DOMAIN_CONVERT),
        "seal": sum_keys(DOMAIN_SEAL),
        "memeory": sum_keys(DOMAIN_MEMEORY),
    }


def collect_links(item: dict[str, Any], apps_by_name: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(kind: str, label: str, url: str | None, primary: bool = False) -> None:
        if not url:
            return
        url = url.strip()
        if not url or url in seen:
            return
        if is_github_url(url) and kind == "demo":
            return
        seen.add(url)
        links.append({"kind": kind, "label": label, "url": url, "primary": "1" if primary else "0"})

    add("demo", "打开演示", item.get("demoUrl"), primary=True)
    pages = item.get("pagesUrl")
    if pages and pages != item.get("demoUrl"):
        add("demo", "GitHub Pages", pages, primary=not item.get("demoUrl"))
    homepage = item.get("homepage")
    if homepage and not is_github_url(homepage):
        already = homepage.rstrip("/") in {u.rstrip("/") for u in seen} or homepage in seen
        if not already:
            add("site", "产品站点", homepage, primary=not any(x["kind"] == "demo" for x in links))

    if item.get("name") == "Face-payment" and not item.get("private"):
        bili = extract_bilibili_demo(item.get("readmeExcerpt") or "")
        add("demo", "Bilibili 演示", bili, primary=True)

    app = apps_by_name.get(APP_ATTACHMENTS.get(item["name"], ""))
    if app:
        add("store", "App Store", app.get("demo"), primary=True)
        site = app.get("site")
        add("site", "产品站点", site)

    add("repo", "GitHub 仓库", item.get("url"))
    return links


def enrich_item(
    item: dict[str, Any],
    apps_by_name: dict[str, dict[str, Any]],
    top_projects: list[dict[str, Any]],
) -> dict[str, Any]:
    private = bool(item.get("private"))
    readme = "" if private else (item.get("readmeExcerpt") or "")
    description = (item.get("description") or "").strip()
    blob = f"{description}\n{readme}"
    problem = extract_problem(readme)
    built = description or first_meaningful_paragraph(readme)
    links = collect_links(item, apps_by_name)
    has_demo = any(link["kind"] in {"demo", "store"} and link.get("primary") == "1" for link in links)
    if not has_demo:
        has_demo = any(link["kind"] in {"demo", "store"} for link in links)
    tokens = match_token_projects(item["name"], top_projects)
    return {
        **item,
        "slug": slug_for(item["name"]),
        "year": year_of(item.get("created")),
        "updated_year": year_of(item.get("updated")),
        "category_label": CATEGORY_LABELS.get(item.get("category") or "other", "其他"),
        "language": item.get("language") or "",
        "description": description,
        "readme_public": readme,
        "problem": problem,
        "built": built,
        "tech": extract_tech(item.get("language"), blob),
        "links": links,
        "has_demo": has_demo,
        "token_matches": tokens,
        "privacy_label": "私有仓库，需要权限" if private else "公开仓库",
    }


def build_context() -> dict[str, Any]:
    catalog = load_catalog()
    tokens = load_tokens()
    apps = load_apps()
    apps_by_name = {app["name"]: app for app in apps}
    top_projects = list(tokens.get("top_projects") or [])
    items = [enrich_item(row, apps_by_name, top_projects) for row in catalog]
    by_name = {item["name"]: item for item in items}

    public = [i for i in items if not i["private"]]
    private = [i for i in items if i["private"]]
    demo_items = [i for i in items if i["has_demo"]]
    years = sorted({i["year"] for i in items if i["year"]}, reverse=True)
    languages = sorted({i["language"] for i in items if i["language"]})
    categories = []
    for key in CATEGORY_ORDER:
        count = sum(1 for i in items if i["category"] == key)
        if count:
            categories.append({"key": key, "label": CATEGORY_LABELS[key], "count": count})

    featured = []
    for spec in FEATURED:
        repo = by_name.get(spec["repo"])
        extras = [by_name[name] for name in spec.get("extra_repos", []) if name in by_name]
        featured.append({**spec, "item": repo, "extras": extras})

    chronicle = build_chronicle(set(by_name))

    return {
        "items": items,
        "by_name": by_name,
        "apps": apps,
        "tokens": tokens,
        "domains": domain_totals(top_projects),
        "counts": {
            "all": len(items),
            "public": len(public),
            "private": len(private),
            "demo": len(demo_items),
            "stars": sum(int(i.get("stars") or 0) for i in items),
            "apps": len(apps),
        },
        "years": years,
        "languages": languages,
        "categories": categories,
        "featured": featured,
        "chronicle": chronicle,
    }
