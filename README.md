# 王天信 · 工作编年

静态中文作品集：叙事历程在前，证据与可点击档案在后。无后端，构建后即可用 GitHub Pages 发布。

线上预期地址：<https://unstoppablecurry.github.io/wangtianxin-portfolio/>

## 内容结构

```
data/
  catalog.json    66 个自有非 fork 仓库（公开仓含 README 摘录；私有仓只有安全的名称/描述）
  tokens.json     memeory 日聚合的 token 用量（设备 / 月份 / 项目名）
  apps.json       3 个 App Store 产品及站点
scripts/
  site_data.py    读取并保守 enrichment（演示链接、分类、token 精确匹配）
  build.py        生成 dist/
  test_site.py    校验 JSON、66 条渲染、详情路由、应用 ID、禁止虚构链接
site/assets/      CSS / JS / 印章 favicon 与纸纹
.github/workflows/pages.yml
```

生成后的 `dist/`：

| 路径 | 说明 |
| --- | --- |
| `/wangtianxin-portfolio/` | 首页：编年、能力地图、论文、可演示主线、App Store、token 账本 |
| `/wangtianxin-portfolio/archive/` | 可检索、可筛选的完整目录 |
| `/wangtianxin-portfolio/p/<repo>/` | 每一条仓库的独立详情页 |
| `/404.html` | 未找到页面 |
| `/sitemap.xml` `/robots.txt` | SEO |

详情页字段：问题、做了什么、技术、证据/结果、日期、stars、可见性、公开 README 摘录、可精确匹配时的 token、链接（演示优先，仓库其次）。缺失项写「待补充」，不补造指标。

## 本地预览

需要 Python 3.10+，无第三方依赖。

```bash
python3 scripts/build.py
python3 scripts/test_site.py
python3 scripts/serve.py
```

默认 `SITE_BASE=/wangtianxin-portfolio`，与 GitHub Pages 项目站一致。打开 <http://127.0.0.1:4173/wangtianxin-portfolio/>。根路径 `/` 会重定向到该前缀。`serve.py` 对未知路径返回 `404.html`。

不要用 `python3 -m http.server --directory dist` 直接预览：页面里的 `/wangtianxin-portfolio/assets/...` 在未挂前缀的服务器上会 404（这也是线上印章图曾经破图的原因）。

## GitHub Pages 部署

1. 仓库 Settings → Pages → Source 选 **GitHub Actions**。
2. 合并到 `main` 后，工作流 `.github/workflows/pages.yml` 会：
   - 用官方 `actions/checkout`、`actions/setup-python` 构建
   - 跑 `scripts/test_site.py`
   - 用 `actions/configure-pages`、`actions/upload-pages-artifact`、`actions/deploy-pages` 发布 `dist/`
3. 项目站地址为 `https://<owner>.github.io/<repo>/`。`SITE_BASE` 由仓库名自动生成。

首次启用 Pages 时，GitHub 可能要求仓库管理员批准 `github-pages` environment。

## 数据与诚实性

- 不编造客户、收入、下载量、期刊录用、DOI 或实验指标。
- 私有仓库保留 GitHub 链接，并标明「私有仓库，需要权限」；不输出私有 README。
- Token 账本使用 `data/tokens.json` 原值。ConvertModel 域 = `中转生意` + `convert`；印章域 = `印模` + `yolo`；`memeory` 单独列出。仓库详情只在项目名与仓库名完全一致时挂接用量。
- Face-payment 的 Bilibili 演示来自该公开仓库 README，不是另造的链接。
- 论文只记录题目《面向OCR文档比对的神经半马尔可夫行对齐》及其英文对照，不宣称发表状态。

## 联系

- 王天信（Tianxin Wang）
- GitHub: <https://github.com/UnstoppableCurry>
- 邮箱: <294957500@qq.com>
