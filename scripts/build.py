#!/usr/bin/env python3
"""Generate the static Chinese portfolio site into dist/."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from htmlutil import asset, e, format_cn_count, format_int, page_url, readme_html
from site_data import CATEGORY_LABELS, ROOT, build_context

SITE_DIR = ROOT / "site"
DIST = ROOT / "dist"
CANONICAL_BASE = os.environ.get(
    "CANONICAL_BASE", "https://unstoppablecurry.github.io/wangtianxin-portfolio"
).rstrip("/")
SITE_BASE = os.environ.get("SITE_BASE", "").rstrip("/")
SITE_NAME = "王天信 · 工作编年"
SITE_DESC = (
    "王天信（Tianxin Wang）的中文作品集：印章/印模计算机视觉、OCR 文档比对、"
    "端侧推理、AI Agent 基础设施、ConvertModel 与 App Store 产品的完整档案。"
)


def href(path: str = "") -> str:
    return page_url(SITE_BASE, path)


def file_href(path: str) -> str:
    return asset(SITE_BASE, path)


def canonical(path: str = "") -> str:
    extra = f"/{path.strip('/')}/" if path.strip("/") else "/"
    if path.endswith(".xml") or path.endswith(".txt") or path.endswith(".json"):
        extra = f"/{path.lstrip('/')}"
    return CANONICAL_BASE + extra


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def nav_items(current: str) -> list[tuple[str, str, str]]:
    return [
        (href(), "首页", "home"),
        (f"{href()}#journey", "历程", "journey"),
        (f"{href()}#paper", "论文", "paper"),
        (f"{href()}#work", "作品", "work"),
        (f"{href()}#apps", "应用", "apps"),
        (f"{href()}#tokens", "用量", "tokens"),
        (href("archive"), "目录", "archive"),
    ]


def layout(
    title: str,
    body: str,
    *,
    description: str | None = None,
    path: str = "",
    current: str = "home",
    extra_head: str = "",
) -> str:
    desc = description or SITE_DESC
    nav = "".join(
        f'<li><a href="{e(url)}"{" aria-current=\"page\"" if key == current else ""}>{e(label)}</a></li>'
        for url, label, key in nav_items(current)
    )
    return f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="author" content="王天信">
  <link rel="canonical" href="{e(canonical(path))}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{e(canonical(path))}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <meta name="theme-color" content="#e7e2d8">
  <link rel="icon" href="{e(file_href('assets/img/favicon.svg'))}" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{e(file_href('assets/img/favicon.svg'))}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;600&family=Noto+Serif+SC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{e(file_href('assets/css/main.css'))}">
  {extra_head}
</head>
<body>
  <a class="skip-link" href="#main">跳到主要内容</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="{e(href())}">
        <img class="brand-mark" src="{e(file_href('assets/img/favicon.svg'))}" alt="">
        <span><span class="brand-name">王天信</span><span class="brand-sub">工作编年</span></span>
      </a>
      <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav">菜单</button>
      <nav class="site-nav" id="site-nav" data-nav aria-label="站点">
        <ul>{nav}</ul>
      </nav>
    </div>
  </header>
  <main id="main">{body}</main>
  <footer class="site-footer">
    <div class="wrap footer-grid">
      <p>王天信 · Tianxin Wang · 算法工程师<br>GitHub <a href="https://github.com/UnstoppableCurry">UnstoppableCurry</a> · <a href="mailto:294957500@qq.com">294957500@qq.com</a></p>
      <p>数字均来自仓库内 <code>data/</code> 已清洗档案。缺失项标为「待补充」，不虚构结果、下载量或期刊状态。</p>
    </div>
  </footer>
  <script src="{e(file_href('assets/js/main.js'))}" defer></script>
</body>
</html>
"""


def buttons(links: list[dict[str, str]], fallback_detail: str | None = None) -> str:
    parts = []
    primary_done = False
    for link in links:
        if link["kind"] == "repo":
            continue
        cls = "btn btn-primary" if link.get("primary") == "1" and not primary_done else "btn btn-ghost"
        if link.get("primary") == "1":
            primary_done = True
        parts.append(f'<a class="{cls}" href="{e(link["url"])}">{e(link["label"])}</a>')
    repo = next((link for link in links if link["kind"] == "repo"), None)
    if not primary_done:
        if fallback_detail:
            parts.insert(0, f'<a class="btn btn-primary" href="{e(fallback_detail)}">查看详情</a>')
        elif repo:
            parts.insert(0, f'<a class="btn btn-primary" href="{e(repo["url"])}">查看仓库</a>')
    if repo:
        parts.append(f'<a class="btn btn-ghost" href="{e(repo["url"])}">仓库</a>')
    return "".join(parts)


def capsules_for(item: dict) -> str:
    bits = [
        f'<span class="capsule">{e(item["category_label"])}</span>',
        f'<span class="capsule">Stars <b>{e(item.get("stars") or 0)}</b></span>',
    ]
    if item.get("language"):
        bits.append(f'<span class="capsule">{e(item["language"])}</span>')
    if item.get("year"):
        bits.append(f'<span class="capsule">{e(item["year"])}</span>')
    if item["private"]:
        bits.append('<span class="capsule private-flag">私有仓库，需要权限</span>')
    if item["has_demo"]:
        bits.append('<span class="capsule">有演示</span>')
    if item.get("token_matches"):
        total = sum(int(row.get("all") or 0) for row in item["token_matches"])
        bits.append(f'<span class="capsule">Tokens <b>{e(format_cn_count(total))}</b></span>')
    return f'<div class="capsules">{"".join(bits)}</div>'


def render_home(ctx: dict) -> str:
    counts = ctx["counts"]
    tokens = ctx["tokens"]
    totals = tokens["totals"]
    domains = ctx["domains"]
    cats = "".join(
        f'<a class="capability" href="{e(href("archive"))}#{e(c["key"])}">'
        f'<span class="idx">{idx:02d}</span><strong>{e(c["label"])}</strong>'
        f'<span class="count">{c["count"]} 项</span></a>'
        for idx, c in enumerate(ctx["categories"], start=1)
    )
    featured_html = []
    for idx, feat in enumerate(ctx["featured"], start=1):
        item = feat["item"]
        if not item:
            continue
        detail = href(f"p/{item['slug']}")
        featured_html.append(
            f'<article class="feature">'
            f'<div class="feature-num">{idx:02d}</div>'
            f'<div><p class="kicker">{e(feat["kicker"])}</p>'
            f'<h3><a href="{e(detail)}">{e(feat["title"])}</a></h3>'
            f'<p>{e(feat["lede"])}</p>{capsules_for(item)}</div>'
            f'<div class="feature-actions btn-row">{buttons(item["links"], detail)}</div>'
            f"</article>"
        )
    apps_html = []
    for app in ctx["apps"]:
        site = f'<a class="btn btn-ghost" href="{e(app["site"])}">产品站点</a>' if app.get("site") else ""
        apps_html.append(
            f'<article class="app-card">'
            f'<p class="kicker">{e(app["bundle"])}</p>'
            f"<h3>{e(app['name'])}</h3>"
            f'<div class="btn-row">'
            f'<a class="btn btn-primary" href="{e(app["demo"])}">App Store</a>{site}'
            f"</div></article>"
        )
    max_month = max((int(m["all"]) for m in tokens["by_month"]), default=1) or 1
    month_rows = "".join(
        f'<div class="bar-row"><span>{e(m["month"])}</span>'
        f'<div class="bar" aria-hidden="true"><i style="width:{max(1, int(m["all"]) * 100 / max_month)}%"></i></div>'
        f'<span>{e(format_cn_count(m["all"]))} · {e(m["sessions"])} 会话</span></div>'
        for m in tokens["by_month"]
    )
    max_dev = max((int(d["all"]) for d in tokens["by_device"]), default=1) or 1
    device_rows = "".join(
        f'<div class="bar-row"><span>{e(d["device"])}</span>'
        f'<div class="bar" aria-hidden="true"><i style="width:{max(1, int(d["all"]) * 100 / max_dev)}%"></i></div>'
        f'<span>{e(format_cn_count(d["all"]))} · {e(d["sessions"])} 会话</span></div>'
        for d in tokens["by_device"]
    )
    top_rows = "".join(
        f'<div class="bar-row"><span>{e(p["project"])}</span>'
        f'<div class="bar" aria-hidden="true"><i style="width:{max(1, int(p["all"]) * 100 / int(tokens["top_projects"][0]["all"]))}%"></i></div>'
        f'<span>{e(format_cn_count(p["all"]))}</span></div>'
        for p in tokens["top_projects"][:12]
    )
    person_ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "王天信",
        "alternateName": "Tianxin Wang",
        "jobTitle": "算法工程师",
        "email": "mailto:294957500@qq.com",
        "url": canonical(),
        "sameAs": ["https://github.com/UnstoppableCurry"],
    }
    extra = f'<script type="application/ld+json">{json.dumps(person_ld, ensure_ascii=False)}</script>'
    body = f"""
    <section class="hero wrap">
      <div>
        <p class="kicker">Portfolio Chronicle</p>
        <h1>王天信<span class="en">Tianxin Wang · 算法工程师</span></h1>
        <p class="lede">从河北科技大学的电气工程出发，经过河北尚云与北京翼维科技，于 2023 年 4 月进入北京动码印章科技有限公司。主线是印章/印模计算机视觉、OCR 文档比对与端侧推理；并行展开 AI Agent 基础设施、ConvertModel API 中转，以及上架的 App Store 产品。下面先讲轨迹，再放证据。</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="#work">先看演示</a>
          <a class="btn btn-ghost" href="{e(href('archive'))}">全部 {counts['all']} 个仓库</a>
          <a class="btn btn-ghost" href="https://github.com/UnstoppableCurry">GitHub</a>
        </div>
      </div>
      <aside class="ledger" aria-label="用量与规模账本">
        <h2>账本 / Ledger</h2>
        <dl>
          <dt>档案条目</dt><dd>{counts['all']}</dd>
          <dt>公开 / 私有</dt><dd>{counts['public']} / {counts['private']}</dd>
          <dt>可演示</dt><dd>{counts['demo']}</dd>
          <dt>Stars 合计</dt><dd>{counts['stars']}</dd>
          <dt>App Store</dt><dd>{counts['apps']}</dd>
          <dt>Tokens 合计</dt><dd>{format_cn_count(totals['all'])}</dd>
          <dt>输入 / 输出</dt><dd>{format_cn_count(totals['input'])} / {format_cn_count(totals['output'])}</dd>
        </dl>
        <div class="capsules">
          <span class="capsule">ConvertModel <b>{format_cn_count(domains['convertmodel']['all'])}</b></span>
          <span class="capsule">印章视觉 <b>{format_cn_count(domains['seal']['all'])}</b></span>
          <span class="capsule">memeory <b>{format_cn_count(domains['memeory']['all'])}</b></span>
        </div>
        <p class="note">Token 数字来自 <code>data/tokens.json</code> 的 memeory 日聚合，不是收入或客户数。</p>
      </aside>
    </section>

    <section class="section" id="journey">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">JOURNEY</p>
            <h2 class="section-title">职业编年</h2>
          </div>
          <p>只写已确认事实。未提供起止年份的段落标为待补充，不补造年表。</p>
        </div>
        <div class="timeline">
          <article class="chapter">
            <div class="year-mark" aria-hidden="true">学</div>
            <p class="meta">学业 · 年份待补充</p>
            <h3>河北科技大学 · 电气工程及自动化</h3>
            <p>工科底子。后续视觉、端侧与文档工作都从这条训练出发，而不是凭空切换赛道。</p>
          </article>
          <article class="chapter">
            <div class="year-mark" aria-hidden="true">尚</div>
            <p class="meta">河北尚云 · 年份待补充</p>
            <h3>河北尚云</h3>
            <p>职业早期节点。本页不扩写未提供的职责、产品名或业绩。</p>
          </article>
          <article class="chapter">
            <div class="year-mark" aria-hidden="true">翼</div>
            <p class="meta">北京翼维科技 · 年份待补充</p>
            <h3>北京翼维科技</h3>
            <p>进入北京后的工作节点。细节待补充，不在此虚构项目清单。</p>
          </article>
          <article class="chapter">
            <div class="year-mark" aria-hidden="true">2023</div>
            <p class="meta">2023-04 至今</p>
            <h3>北京动码印章科技有限公司</h3>
            <p>自 2023 年 4 月起。核心工作落在印章/印模视觉、OCR 文档比对、端侧推理，并延伸到 Agent 基础设施与 ConvertModel。</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="map">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">CAPABILITY</p>
            <h2 class="section-title">能力地图</h2>
          </div>
          <p>分类与计数直接从目录动态汇总，共 {counts['all']} 项。</p>
        </div>
        <div class="capability-grid">{cats}</div>
      </div>
    </section>

    <section class="section" id="paper">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">PAPER</p>
            <h2 class="section-title">论文与研究</h2>
          </div>
        </div>
        <div class="paper-panel">
          <img class="seal-stamp" src="{e(file_href('assets/img/seal.svg'))}" alt="朱文印：信">
          <div>
            <p class="kicker">研究文稿</p>
            <h3>《面向OCR文档比对的神经半马尔可夫行对齐》</h3>
            <p>Neural semi-Markov line alignment for OCR document comparison</p>
            <p>主题是 OCR 文档比对里的行对齐，而不是泛泛的识别准确率宣传。本页只记录题目与问题意识。</p>
            <p class="honest">诚实声明：此处不填写期刊、会议、录用状态、DOI、引用数、实验表格或任何未提供的结果。目录里的 OCR / 合同比对仓库与该主题相邻，但不被标记为这篇文稿的正式发表版本。</p>
            <div class="btn-row">
              <a class="btn btn-ghost" href="{e(href('p/ContractComparison'))}">ContractComparison</a>
              <a class="btn btn-ghost" href="{e(href('p/word-print-layout-pipeline'))}">word-print-layout-pipeline</a>
              <a class="btn btn-ghost" href="{e(href('p/ocr-compare'))}">ocr-compare</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="work">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">FEATURED</p>
            <h2 class="section-title">可演示的主线工作</h2>
          </div>
          <p>演示按钮优先。没有演示的条目在完整目录里以「查看详情」进入。</p>
        </div>
        <div class="featured-list">{''.join(featured_html)}</div>
      </div>
    </section>

    <section class="section" id="apps">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">APP STORE</p>
            <h2 class="section-title">上架应用</h2>
          </div>
          <p>三款产品均来自 <code>data/apps.json</code>，不添加下载量或其他商店指标。</p>
        </div>
        <div class="apps-grid">{''.join(apps_html)}</div>
      </div>
    </section>

    <section class="section" id="tokens">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">TOKENS</p>
            <h2 class="section-title">Token 用量账本</h2>
          </div>
          <p>精确摘录，不估算缺口。覆盖说明见原文。</p>
        </div>
        <div class="token-board">
          <div class="panel">
            <h3>总计</h3>
            <dl class="stat-list">
              <dt>all</dt><dd>{format_int(totals['all'])}</dd>
              <dt>input</dt><dd>{format_int(totals['input'])}</dd>
              <dt>output</dt><dd>{format_int(totals['output'])}</dd>
              <dt>cacheRead</dt><dd>{format_int(totals['cacheRead'])}</dd>
              <dt>cacheCreate</dt><dd>{format_int(totals['cacheCreate'])}</dd>
            </dl>
            <h3 style="margin-top:1.2rem">主要域</h3>
            <p>ConvertModel = 中转生意 + convert；印章 = 印模 + yolo；memeory 单独成项。</p>
            <div class="capsules">
              <span class="capsule">ConvertModel <b>{format_int(domains['convertmodel']['all'])}</b></span>
              <span class="capsule">印章 <b>{format_int(domains['seal']['all'])}</b></span>
              <span class="capsule">memeory <b>{format_int(domains['memeory']['all'])}</b></span>
            </div>
          </div>
          <div class="panel">
            <h3>按月</h3>
            {month_rows}
          </div>
          <div class="panel">
            <h3>按设备</h3>
            {device_rows}
          </div>
          <div class="panel">
            <h3>用量最高的项目名</h3>
            <p>名称来自采集器对工作目录的推断，部分噪声名（如 New project）保持原样。</p>
            {top_rows}
          </div>
        </div>
        <details class="honest">
          <summary>覆盖说明（原文）</summary>
          <p>{e(tokens.get('coverage_note') or '待补充')}</p>
        </details>
      </div>
    </section>

    <section class="section" id="archive-teaser">
      <div class="wrap">
        <div class="section-head">
          <div>
            <p class="section-en">ARCHIVE</p>
            <h2 class="section-title">完整目录</h2>
          </div>
          <a class="btn btn-primary" href="{e(href('archive'))}">检索全部 {counts['all']} 项</a>
        </div>
        <p>每条都可点进独立详情页。私有仓库保留 GitHub 链接，并标明需要权限；不展示私有 README。</p>
      </div>
    </section>
    """
    return layout(SITE_NAME, body, path="", current="home", extra_head=extra)


def render_archive(ctx: dict) -> str:
    cat_opts = "".join(
        f'<option value="{e(c["key"])}">{e(c["label"])} ({c["count"]})</option>'
        for c in ctx["categories"]
    )
    year_opts = "".join(f'<option value="{e(y)}">{e(y)}</option>' for y in ctx["years"])
    lang_opts = "".join(f'<option value="{e(lang)}">{e(lang)}</option>' for lang in ctx["languages"])
    chips = "".join(
        f'<a class="chip" href="#{e(c["key"])}">{e(c["label"])} {c["count"]}</a>'
        for c in ctx["categories"]
    )
    cards = []
    for item in sorted(ctx["items"], key=lambda x: (x.get("updated") or ""), reverse=True):
        detail = href(f"p/{item['slug']}")
        desc = item["description"] or "描述待补充"
        search = " ".join(
            [
                item["name"],
                item["description"],
                item["category_label"],
                item.get("language") or "",
                item.get("year") or "",
            ]
        )
        cards.append(
            f'<a class="archive-item" href="{e(detail)}" data-item '
            f'data-category="{e(item["category"])}" data-year="{e(item["year"])}" '
            f'data-private="{1 if item["private"] else 0}" data-language="{e(item["language"])}" '
            f'data-demo="{1 if item["has_demo"] else 0}" data-search="{e(search)}">'
            f"<div><h3>{e(item['name'])}</h3><p>{e(desc)}</p>{capsules_for(item)}</div>"
            f'<div class="btn-row"><span class="btn {"btn-primary" if item["has_demo"] else "btn-ghost"}">'
            f'{"打开演示 / 详情" if item["has_demo"] else "查看详情"}</span></div></a>'
        )
    body = f"""
    <section class="section" style="border-top:0">
      <div class="wrap" data-archive>
        <div class="section-head">
          <div>
            <p class="section-en">ARCHIVE</p>
            <h1 class="section-title">完整项目目录</h1>
          </div>
          <p class="count-live" data-count aria-live="polite">当前显示 {ctx['counts']['all']} / {ctx['counts']['all']} 条</p>
        </div>
        <p>共 {ctx['counts']['all']} 项：公开 {ctx['counts']['public']}，私有 {ctx['counts']['private']}，可演示 {ctx['counts']['demo']}。筛选只改变可见性，不删除档案。</p>
        <div class="filters">
          <label>检索
            <input type="search" data-search placeholder="按名称、描述、语言或年份搜索" autocomplete="off">
          </label>
          <div class="filter-row" role="group" aria-label="分类快捷">
            {chips}
          </div>
          <div class="filter-row">
            <label>分类 <select data-filter-category><option value="all">全部分类</option>{cat_opts}</select></label>
            <label>年份 <select data-filter-year><option value="all">全部年份</option>{year_opts}</select></label>
            <label>可见性 <select data-filter-visibility>
              <option value="all">公开 + 私有</option>
              <option value="public">仅公开</option>
              <option value="private">仅私有</option>
            </select></label>
            <label>语言 <select data-filter-language><option value="all">全部语言</option>{lang_opts}</select></label>
            <label>演示 <select data-filter-demo>
              <option value="all">全部</option>
              <option value="yes">有演示</option>
              <option value="no">无演示</option>
            </select></label>
          </div>
        </div>
        <div class="archive-list">{''.join(cards)}</div>
        <p class="empty-state" data-empty hidden>没有符合当前筛选的项目。</p>
      </div>
    </section>
    """
    return layout("完整目录 · 王天信", body, path="archive", current="archive")


def render_detail(item: dict, ctx: dict) -> str:
    detail = href(f"p/{item['slug']}")
    problem = item["problem"] or "待补充"
    built = item["built"] or "待补充"
    tech = "、".join(item["tech"]) if item["tech"] else "待补充"
    results = "待补充"
    if item["has_demo"]:
        results = "有公开演示或产品入口，见下方链接。不在此填写未提供的准确率、下载量或客户数。"
    if item.get("stars"):
        results = (results + " " if results != "待补充" else "") + f'GitHub stars：{item["stars"]}（仓库元数据，不是业务结果）。'
    token_block = "<p>待补充。未在 tokens.json 的 top_projects 中找到与仓库名完全对应的记录。</p>"
    if item["token_matches"]:
        rows = "".join(
            f"<tr><td>{e(t['project'])}</td><td>{format_int(t['all'])}</td>"
            f"<td>{format_int(t['sessions'])}</td></tr>"
            for t in item["token_matches"]
        )
        token_block = (
            "<p>仅在项目名与仓库名完全对应时显示。</p>"
            f'<table><thead><tr><th>项目</th><th>all</th><th>sessions</th></tr></thead><tbody>{rows}</tbody></table>'
        )
    readme = (
        "<p>私有仓库不展示 README。</p>"
        if item["private"]
        else (readme_html(item["readme_public"]) or "<p>待补充</p>")
    )
    privacy = (
        f'<p class="private-flag">私有仓库，需要权限。链接保留，但不展开内部说明。</p>'
        if item["private"]
        else "<p>公开仓库。</p>"
    )
    body = f"""
    <div class="wrap detail-layout">
      <article class="detail-card prose">
        <p class="kicker">{e(item['category_label'])} · {e(item['year'] or '年份待补充')}</p>
        <h1>{e(item['name'])}</h1>
        {capsules_for(item)}
        {privacy}
        <h2>问题</h2>
        <p>{e(problem)}</p>
        <h2>做了什么</h2>
        <p>{e(built)}</p>
        <h2>技术</h2>
        <p>{e(tech)}</p>
        <h2>证据 / 结果</h2>
        <p>{e(results)}</p>
        <h2>日期</h2>
        <p>创建 {e(item.get('created') or '待补充')} · 更新 {e(item.get('updated') or '待补充')}</p>
        <h2>Token 用量</h2>
        {token_block}
        <h2>README 摘录</h2>
        {readme}
        <div class="btn-row">{buttons(item['links'], None)}</div>
      </article>
      <aside class="ledger">
        <h2>索引</h2>
        <dl>
          <dt>可见性</dt><dd>{e(item['privacy_label'])}</dd>
          <dt>Stars</dt><dd>{e(item.get('stars') or 0)}</dd>
          <dt>语言</dt><dd>{e(item['language'] or '待补充')}</dd>
          <dt>分类</dt><dd>{e(item['category_label'])}</dd>
        </dl>
        <div class="btn-row" style="margin-top:1rem">
          <a class="btn btn-ghost" href="{e(href('archive'))}">返回目录</a>
          <a class="btn btn-ghost" href="{e(href())}">返回首页</a>
        </div>
      </aside>
    </div>
    """
    desc = item["description"] or f"{item['name']} — 王天信作品档案"
    return layout(f"{item['name']} · 王天信", body, description=desc, path=f"p/{item['slug']}", current="archive")


def render_404() -> str:
    body = f"""
    <section class="page-404">
      <div>
        <p class="kicker">404</p>
        <h1>页不在册</h1>
        <p>这份编年里没有该路径。回到首页或完整目录继续。</p>
        <div class="btn-row" style="justify-content:center">
          <a class="btn btn-primary" href="{e(href())}">回首页</a>
          <a class="btn btn-ghost" href="{e(href('archive'))}">完整目录</a>
        </div>
      </div>
    </section>
    """
    return layout("页不在册 · 王天信", body, description="未找到该页面。", current="home")


def write_seo(ctx: dict) -> None:
    paths = ["", "archive"] + [f"p/{item['slug']}" for item in ctx["items"]]
    urls = "\n".join(
        f"  <url><loc>{e(canonical(path))}</loc></url>"
        for path in paths
    )
    write(
        DIST / "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
    )
    write(
        DIST / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {canonical('sitemap.xml')}\n",
    )


def main() -> None:
    ctx = build_context()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SITE_DIR / "assets", DIST / "assets")
    write(DIST / ".nojekyll", "")
    write(DIST / "index.html", render_home(ctx))
    write(DIST / "archive" / "index.html", render_archive(ctx))
    write(DIST / "404.html", render_404())
    for item in ctx["items"]:
        write(DIST / "p" / item["slug"] / "index.html", render_detail(item, ctx))
    archive_payload = [
        {
            "name": item["name"],
            "slug": item["slug"],
            "category": item["category"],
            "year": item["year"],
            "private": item["private"],
            "language": item["language"],
            "has_demo": item["has_demo"],
            "stars": item.get("stars") or 0,
        }
        for item in ctx["items"]
    ]
    write(DIST / "data" / "archive.json", json.dumps(archive_payload, ensure_ascii=False, indent=2))
    write_seo(ctx)
    print(
        f"built {ctx['counts']['all']} projects, "
        f"{ctx['counts']['public']} public, {ctx['counts']['private']} private, "
        f"{ctx['counts']['demo']} with demo -> {DIST}"
    )


if __name__ == "__main__":
    main()
