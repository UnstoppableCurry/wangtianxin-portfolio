from __future__ import annotations

import html
import re


def e(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def format_int(n: int | float) -> str:
    return f"{int(n):,}"


def format_cn_count(n: int) -> str:
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f} 亿"
    if n >= 10_000:
        return f"{n / 10_000:.1f} 万"
    return format_int(n)


def normalize_base(base: str | None) -> str:
    return (base or "").rstrip("/")


def join_base(base: str, path: str) -> str:
    """Root-relative URL that keeps a GitHub Pages project prefix.

    `/wangtianxin-portfolio` + `assets/img/seal.svg`
    -> `/wangtianxin-portfolio/assets/img/seal.svg`
    Empty base stays site-root (`/assets/...`) for user pages only.
    """
    base = normalize_base(base)
    path = path.lstrip("/")
    if not path:
        return f"{base}/" if base else "/"
    return f"{base}/{path}" if base else f"/{path}"


def asset(base: str, path: str) -> str:
    return join_base(base, path)


def page_url(base: str, path: str) -> str:
    path = path.strip("/")
    if not path:
        return join_base(base, "")
    return join_base(base, path) + "/"


def sanitize_readme(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.I)
    text = re.sub(r"on\w+\s*=", "", text, flags=re.I)
    text = re.sub(r"!\[[^\]]*\]\((?!https?:)[^)]+\)", "", text)
    return text.strip()


def readme_html(text: str) -> str:
    clean = sanitize_readme(text)
    if not clean:
        return ""
    return f'<pre class="readme">{e(clean)}</pre>'
