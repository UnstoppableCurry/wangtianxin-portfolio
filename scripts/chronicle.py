"""Prepare a public-safe view of Mac mini / ThunderSSD organize results.

Never emit local home paths, internal GitLab URLs, machine IDs, secrets
repos, customer-seal filenames, or invented metrics.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Prefer a narrative order; unknown buckets append at the end.
ENERGY_ORDER = [
    "印章主业",
    "OCR论文",
    "ConvertModel中转生意",
    "上架产品化",
    "自动化Agent工具",
    "memeory",
    "探索游戏",
    "记忆与数据",
    "其他",
]

TIMELINE_COPY = {
    "2023-04+ seal mainline": {
        "title": "印章主线",
        "when": "2023 年 4 月起",
        "mark": "2023",
    },
    "late 2025 ~ early 2026 side business + apps": {
        "title": "中转生意与上架应用",
        "when": "2025 年末～2026 年初",
        "mark": "25",
    },
    "2026-01~05 token peak": {
        "title": "Token 账本高峰对应的工作",
        "when": "2026 年 1–5 月",
        "mark": "01",
    },
    "2026-03~07 games + agent sprouts": {
        "title": "探索游戏与 Agent 萌芽",
        "when": "2026 年 3–7 月",
        "mark": "春",
    },
    "2026-06~08 OCR paper + seal delivery": {
        "title": "OCR 论文与印章交付",
        "when": "2026 年 6–8 月",
        "mark": "夏",
    },
    "2026-07~09 hiring agents + glasses CLI": {
        "title": "招聘 Agent 与眼镜 CLI",
        "when": "2026 年 7–9 月",
        "mark": "秋",
    },
}

FACT_LABELS = {
    "fact": "已确认事实",
    "fact+inferred": "事实 + 时间窗推断",
    "inferred": "时间窗推断",
}

STATUS_LABELS = {
    "本地only": "仅本地，未上 GitHub",
    "已有GH需加强": "目录已有，叙述待加强",
}

# Hard deny: these must never appear in generated HTML.
# Do not match public gitlab.com or dotted version numbers like 10.1.2.3.
PUBLIC_FORBIDDEN = [
    re.compile(r"/Users/", re.I),
    re.compile(r"/Volumes/", re.I),
    re.compile(r"/workspace/", re.I),
    re.compile(r"192\.168\."),
    re.compile(r"secrets\.git", re.I),
    re.compile(r"c0c8477c-ec42-4657-b9c5-746c5f64efba", re.I),
    re.compile(r"niuma\.local", re.I),
    re.compile(r"git-crypt", re.I),
    re.compile(r"https?://(?!gitlab\.com)[^\s\"']*gitlab[^\s\"']*", re.I),
]

# Internal folder/log names from organize JSON — teach the category, do not inventory.
INVENTORY_REWRITES = (
    (re.compile(r"jni_inputs(?:_excluded)?"), "检测输入样本"),
    (re.compile(r"getseal_测试图"), "测试图"),
    (re.compile(r"dpi_test_seals"), "分辨率测试样本"),
    (re.compile(r"probe_in\*"), "探针输入"),
    (re.compile(r"probe_out\*"), "探针输出"),
    (re.compile(r"bmp数据"), "位图样本"),
    (re.compile(r"合成印章_多dpi"), "多分辨率合成样本"),
    (re.compile(r"login-attempt\.log"), "登录日志"),
    (re.compile(r"serve\.log"), "服务日志"),
    (re.compile(r"annotation_output\*"), "标注输出"),
    (re.compile(r"yolo alldata"), "训练全量数据"),
    (re.compile(r"P2201/交接-claude"), "设备联调交接"),
    (re.compile(r"HANDOVER\.md"), "交接稿"),
    (re.compile(r"ultraplan/会话续写 txt"), "会话续写"),
    (re.compile(r"delivery_\*/delivery md、工作交接_\*\.md、"), "交接稿、"),
    (re.compile(r"\.codex/memories"), "会话备份"),
)

PATHISH = re.compile(
    r"(?:/Users/|/Volumes/|/workspace/|~/)[^\s,;）)]+",
    re.I,
)

FRIENDLY_PATHS = (
    (re.compile(r"~/rl(?:/[^\s,;）)]*)?"), "研究实验目录"),
    (re.compile(r"Desktop/招聘"), "招聘工作副本"),
)

# Educational public copies — categories, not a download inventory.
BLACKLIST_PUBLIC = [
    "客户印模图、真章扫描、任意业务样张",
    "检测、探针或合成目录中的客户与未授权样本",
    "简历落盘与招聘候选人文件",
    "内网 GitLab 地址明文",
    "凭证解密内容、API Key、Cookie、登录日志",
    "含客户微调的权重与原始数据集",
    "交接包里的客户信息、对接人口令、未脱敏交接稿",
]

GRAY_PUBLIC = [
    {
        "item": "交接稿与会话续写",
        "rule": "须去掉客户名、内网地址、样图、口令后才能作历程旁注",
    },
    {
        "item": "发布说明 / 版本对照表",
        "rule": "可抽版本数字与分工叙述；必须去掉内网链接与客户环境路径",
    },
    {
        "item": "设备联调交接材料",
        "rule": "可保留「设备联调存在」；删除对接人姓名与口令类引用",
    },
]

DENIED_REPOS = {"secrets"}


def sanitize_text(value: object) -> str:
    text = "" if value is None else str(value)
    for pattern, label in FRIENDLY_PATHS:
        text = pattern.sub(label, text)
    for pattern, label in INVENTORY_REWRITES:
        text = pattern.sub(label, text)
    text = PATHISH.sub("本地目录", text)
    text = re.sub(r"192\.168(?:\.[0-9xX]+){0,2}", "内网地址", text)
    text = re.sub(r"内网地址\s*地址", "内网地址", text)
    text = re.sub(r"https?://(?!gitlab\.com)[^\s]*gitlab[^\s]*", "内网 GitLab", text, flags=re.I)
    text = re.sub(r"niuma\.local", "本机", text, flags=re.I)
    text = re.sub(r"c0c8477c-ec42-4657-b9c5-746c5f64efba", "本机", text, flags=re.I)
    text = re.sub(r"secrets\.git", "凭证仓", text, flags=re.I)
    text = re.sub(r"git-crypt", "加密凭证", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def as_name_list(value: object) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


def first_forbidden(blob: str) -> str | None:
    for pattern in PUBLIC_FORBIDDEN:
        match = pattern.search(blob)
        if match:
            return match.group(0)
    return None


def _bucket_rows(raw: dict[str, Any]) -> list[dict[str, Any]]:
    items = [{"key": key, "label": key, "count": int(count)} for key, count in raw.items()]
    rank = {name: idx for idx, name in enumerate(ENERGY_ORDER)}
    items.sort(key=lambda row: (rank.get(row["key"], 99), -row["count"], row["key"]))
    return items


def _timeline(pass2: dict[str, Any]) -> list[dict[str, str]]:
    draft = pass2.get("careerTimelineDraft") or {}
    stages = []
    for raw in draft.get("stages") or []:
        key = raw.get("stage") or ""
        copy = TIMELINE_COPY.get(key, {})
        stages.append(
            {
                "key": key,
                "title": copy.get("title") or sanitize_text(key),
                "when": copy.get("when") or "",
                "mark": copy.get("mark") or "",
                "fact": FACT_LABELS.get(raw.get("factOrInferred") or "", "来源待核"),
                "projects": [sanitize_text(name) for name in raw.get("projects") or []],
            }
        )
    return stages


def _card_repos(card: dict[str, Any], catalog_names: set[str]) -> list[str]:
    source = card.get("证据来源") or {}
    names: list[str] = []
    for key in ("githubName", "relatedGithub", "relatedPublicGithub"):
        names.extend(as_name_list(source.get(key)))
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        if name.lower() in DENIED_REPOS:
            continue
        if name in seen or name not in catalog_names:
            continue
        seen.add(name)
        out.append(name)
    return out


def _cards(pass3: dict[str, Any], catalog_names: set[str]) -> list[dict[str, Any]]:
    cards = []
    for raw in pass3.get("candidateCards") or []:
        energy = sanitize_text(raw.get("精力桶"))
        title = sanitize_text(raw.get("标题"))
        status = raw.get("状态") or ""
        cards.append(
            {
                "id": sanitize_text(raw.get("id")),
                "title": title,
                "energy": energy,
                "problem": sanitize_text(raw.get("解决的问题")),
                "public_ok": [sanitize_text(x) for x in raw.get("可公开写什么") or []],
                "must_redact": [sanitize_text(x) for x in raw.get("必须脱敏什么") or []],
                "form": sanitize_text(raw.get("建议展示形态")),
                "status": STATUS_LABELS.get(status, sanitize_text(status)),
                "status_key": status,
                "priority": int(raw.get("priority") or 0),
                "repos": _card_repos(raw, catalog_names),
                "search": " ".join(
                    [
                        title,
                        energy,
                        sanitize_text(raw.get("解决的问题")),
                        STATUS_LABELS.get(status, ""),
                    ]
                ),
            }
        )
    cards.sort(key=lambda row: row["priority"] or 99)
    return cards


def _ocr(pass3: dict[str, Any]) -> dict[str, Any]:
    raw = pass3.get("ocrTimelineOutline") or {}
    highlights = raw.get("作品集应置顶的公开叙述要点") or {}
    stages = []
    for item in raw.get("stages") or []:
        stages.append(
            {
                "name": sanitize_text(item.get("阶段")),
                "when": sanitize_text(item.get("时间窗")),
                "point": sanitize_text(item.get("要点")),
            }
        )
    return {
        "title": sanitize_text(raw.get("title") or "OCR 历程提纲"),
        "summary": sanitize_text(highlights.get("摘要")),
        "capability": sanitize_text(highlights.get("对齐能力")),
        "limits": sanitize_text(highlights.get("局限")),
        "stages": stages,
        "ablation_policy": "消融点估计不上站；数字须人工复核后再写。公开卡必须同屏保留局限句，不能把续训对照写成「只改损失」。",
        "ablation_note": "本地确有对照材料，但本页不摘录点估计，也不把实验文件写成可点击下载。",
    }


def _lists(pass3: dict[str, Any]) -> dict[str, Any]:
    raw = pass3.get("sealPublicLists") or {}
    # Keep pass3 as the existence check; publish educational categories only.
    if not raw.get("blacklist"):
        raise ValueError("organize-pass3.json missing sealPublicLists.blacklist")
    return {
        "whitelist": [sanitize_text(x) for x in raw.get("whitelist") or []],
        "blacklist": list(BLACKLIST_PUBLIC),
        "gray": [dict(row) for row in GRAY_PUBLIC],
    }


def _named_notes(rows: list[dict[str, Any]], catalog_names: set[str]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        name = sanitize_text(row.get("name"))
        if name.lower() == "secrets":
            name = "凭证仓"
        github = sanitize_text(row.get("githubName") or "")
        if github.lower() == "secrets":
            github = ""
        out.append(
            {
                "name": name,
                "note": sanitize_text(row.get("note")),
                "kind": sanitize_text(row.get("kind") or ""),
                "repo": github if github in catalog_names else "",
            }
        )
    return out


def _load(name: str) -> Any:
    with (DATA_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def build_chronicle(catalog_names: set[str]) -> dict[str, Any]:
    bundle = _load("chronicle-bundle.json")
    pass3_file = _load("organize-pass3.json")
    pass1 = bundle.get("pass1") or {}
    pass2 = bundle.get("pass2") or {}
    # organize-pass3.json is the card/outline/list source of truth.
    cards = _cards(pass3_file, catalog_names)
    energy = _bucket_rows(pass1.get("energyBuckets") or {})
    stamp = str(pass3_file.get("generatedAt") or bundle.get("generatedAt") or "")
    match = re.search(r"(\d{4}-\d{2}-\d{2})", stamp)
    return {
        "generated_label": f"整理批次 {match.group(1)}" if match else "整理批次",
        "principle": "只写自己的工作；不编造客户、营收或实验指标；密钥、客户印模图与内网地址一律不公开。",
        "energy": energy,
        "energy_total": sum(row["count"] for row in energy),
        "timeline": _timeline(pass2),
        "cards": cards,
        "card_count": len(cards),
        "energy_filters": sorted({card["energy"] for card in cards}, key=lambda k: ENERGY_ORDER.index(k) if k in ENERGY_ORDER else 99),
        "ocr": _ocr(pass3_file),
        "lists": _lists(pass3_file),
        "covered": _named_notes(pass1.get("alreadyCovered") or [], catalog_names),
        "memory": _named_notes(pass1.get("memoryItems") or [], catalog_names),
        "data": _named_notes(pass1.get("dataItems") or [], catalog_names),
        "counts": {
            "covered": len(pass1.get("alreadyCovered") or []),
            "cards": len(cards),
            "memory": len(pass1.get("memoryItems") or []),
            "data": len(pass1.get("dataItems") or []),
            "energy": len(energy),
        },
    }
