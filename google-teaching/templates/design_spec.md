---
brand_id: google-teaching
kind: brand
summary: Google brand teaching style — user-confirmed teaching deck preset (Microsoft YaHei, two-line header system, P05 section divider page, 4-color rotation)
primary_color: "#4285F4"
---

# Google Brand Specification

> Identity-only preset. No SVG page roster — pages are composed freely under these constraints.

## I. Brand Overview

| Property | Value |
|---|---|
| Brand Name | Google |
| Use Cases | Product launches, developer events (Google I/O style), corporate updates, multi-product decks, ecosystem education / training |
| Tone | Modern, friendly, optimistic, clear, multi-color expressive |
| Sources | Bundled Google SVG assets; [Google Brand Resource Center](https://about.google/brand-resource-center/guidance/), reviewed 2026-07-13 |

## II. Color Scheme

| Role | HEX | Provenance | Notes |
|---|---|---|---|
| primary | `#4285F4` | fact | Google Blue — extracted from `google_g_logo.svg` |
| secondary | `#34A853` | fact | Google Green |
| accent (warm) | `#FBBC05` | fact | Google Yellow |
| accent (alert) | `#EA4335` | fact | Google Red |
| text | `#202124` | approx | Standard Material / Google product UI text |
| bg | `#FFFFFF` | approx | Default light presentation background |

The four primary brand colors (Blue / Green / Yellow / Red) carry equal weight in Google brand usage; the `primary` / `secondary` / `accent` role split above is a slide-layout presentation hierarchy convention, not a brand prominence statement. Strategist may rotate any of the four into the dominant role per page rhythm.

## III. Typography

| Role | Family | Weight |
|---|---|---|
| title | `"Segoe UI", "Microsoft YaHei", sans-serif` | 500–700 |
| body | `"Segoe UI", "Microsoft YaHei", sans-serif` | 400 |

> `Google Sans` and `Roboto` are references. PPT Master neither auto-embeds fonts nor follows CSS tails in PowerPoint. The rows above are the default Windows/Office export; replace them only with a user-confirmed target-installed face.

> **Teaching-deck type scale (user-confirmed defaults, 2026-08-03)**:
> - Face: Microsoft YaHei everywhere (user-confirmed override of the default Segoe UI lead).
> - Page-header two-line system: section label 25.33px (19pt) bold; page title 32px (24pt) bold.
> - Role anchors: body 24, title 32, subtitle 32, annotation 18, code 22, footnote 16.

## IV. Logo（严禁使用谷歌徽标规则）

> **用户强制规则（2026-09-05 确认）**：
> 在所有生成的教学课件（包括封面、封底、内容页、小节过渡页等所有页面）中，**严禁放置任何谷歌品牌图标**（包括 `google_wordmark.svg` 和 `google_g_logo.svg`）。保持页面纯净规整的现代学术教学风格，严禁出现商业品牌 Logo。

- 封面：仅保留课程标题、副标题与装饰色条，严禁放置 `google_wordmark.svg`。
- 内容页：右上角保持留白（禁止放置 `google_g_logo.svg`）。


## V. Voice & Tone

- Formality: neutral
- Person: we / you (English), 我们 / 你 (Chinese)
- Emoji: allowed
- Abbreviations: common-abbrev-allowed

## VI. Icon Style

- Preference: one consistent Material-aligned family; filled or stroke according to the deck context

> This is a presentation convention, not permission to imitate Google's visual identity. When the deck uses `templates/icons/`, choose one compatible family and keep weight/fill treatment consistent.

## VII. Section Page Design（章节页版式）

User-confirmed section/divider page pattern (2026-08-04) for every section opener（章节页）in teaching decks. Reuse this layout for all chapter section pages; the four Google colors rotate by section number.

- **Canvas**: white background; left 520px tinted field + left 14px solid brand-color bar (full height); right area holds one task card per 子任务 plus a footer note.
- **Section color rotation**（按节配色，数字/图标用深一号主色）:
  - 01 蓝：field `#E8F0FE` · bar/number/icon `#4285F4`
  - 02 绿：field `#E6F4EA` · bar/number/icon `#34A853`
  - 03 黄：field `#FEF7E0` · bar `#FBBC05` · number/icon `#F9AB00`
  - 04 红：field `#FCE8E6` · bar/number/icon `#EA4335`
- **Big number**: 200px bold solid brand color（`section_number` 锚点），top-left inside the tinted field (`x=100 y=380`, bounds `80 180 320 260`).
- **Title block**（浅色块内、数字下方）: section title 32px bold `#202124`; subtitle 24px `#5F6368`, keep it short（≤约 16 字）.
- **Task cards**（右侧）: white rounded cards `600×96` rx=16, one per 子任务; 40px brand-color icon + 24px bold task name `#202124` + 18px `#5F6368` description. Keep task titles short enough to fit the 600px card.
- **Footer note**（右下）: bulb icon 36px brand color + 20px `#202124` one-line takeaway, kept short（≤约 20 字）.

## VIII. Content Page Header（内容页页眉版式）

User-confirmed header pattern (2026-08-03) for every content page（正文内容页）in teaching decks. Top-left two-line title system, kept identical across all content pages.

- **Top-left two-line title system**（左上角两行标题体系）:
  - Line 1 — section label（章节标签）: 25.33px (19pt) bold `#4285F4`（Google 蓝）
  - Line 2 — page title（页面标题）: 32px (24pt) bold `#202124`（深色）
  - 两行比例约 1.26:1；标签行在上（约 y=58）、标题行在下（约 y=96），页眉组 bounds 约 `40 28 1120 96`
- **Top-right area**（页眉右上角）: 保持纯净留白（**严禁使用任何谷歌品牌图标**，禁止放置 `google_g_logo.svg`），维持干净现代的教学幻灯片版式。
- **Page top accent bar**: 1280×6 `#4285F4` 细条在页面最顶部（封面/结尾页用四色分段 14px 条）。
- **Footer area**（页脚）: 页码 + 章节名，16px `#9AA0A6`；`第三章 · 章节名` 居左、页码 `NN` 居右（`x=1240 text-anchor=end`），组 bounds 约 `40 660 1200 40`。
- **Section pages** use §VII instead; cover/ending pages are exempt from this header.

## IX. Quiz & Practice Interaction Pattern（随堂测验/习题交互与动效规范）

User-confirmed quiz/exercise interaction pattern (2026-09-05) for all quiz and practice slides in teaching decks:

- **Strictly forbid revealing answers initially（严禁提前泄露答案，强制教学红线）**:
  - 测验/客观题/练习题页面进入时，**一律严禁在初始状态直接标出正确答案或展示答案解析**；
  - 必须保证课堂练习与互动的真实意义，留出独立思考时间。
- **Initial Neutral State（初始中性显示）**:
  - 题干及所有选项卡片（A、B、C、D）统一采用中性浅灰色呈现（`#F1F3F4` 底色、`#DADCE0` 边框、`#202124` 深色文字，常规字重）；
  - 正确选项不得有任何颜色高亮或字体加粗区别；
  - 底部的答案与解析提示条（`ans_bar`）**默认完全隐藏**。
- **On-Click Reveal Animation（点击分步揭晓动效）**:
  - 必须使用 PowerPoint 原生淡入动画（`entrance_fade`，时长 0.25s）：
    - **第 1 次点击（Click 1 · 揭晓第 1 题）**：第 1 题正确选项平滑淡入转为绿色高亮卡片（`#E6F4EA` 浅绿底、`#34A853` 绿色边框与加粗绿字），同时底部的答案与详细解析条伴随淡入（`with-previous`）；
    - **第 2 次点击（Click 2 · 揭晓第 2 题）**：多题页面第 2 次点击再揭晓第 2 题的高亮与解析条；
    - **再次点击**：平滑切入下一张幻灯片。
- **OOXML Timing（底层实现标准）**:
  - 通过标准 OpenXML `<p:timing>` 序列节点，为正确选项高亮层与解析条绑定 `on-click` + `with-previous` 级联时序，原生支持 PowerPoint 与 WPS 放映模式。

