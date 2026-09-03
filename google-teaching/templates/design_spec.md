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

## IV. Logo

Google uses a dual-lockup brand system — pick by context, never combine on the same page.

| File | Form | Usage |
|---|---|---|
| `../images/google_wordmark.svg` | Full "Google" wordmark (272×92) | Cover hero, ending sign-off, any moment the full brand reads at a glance |
| `../images/google_g_logo.svg` | Square multi-color "G" mark (24×24) | Header / footer corners, page-number neighbors, tight badges, any small-size moment where the wordmark would become illegible |

- Cover: prefer wordmark
- Per-page: optional — only when wordmark or G mark genuinely fits the layout; do not stamp every page
- Use only unmodified approved artwork and follow the official guidance for the actual context; never imply affiliation, sponsorship, or endorsement
- Clearspace: follow the applicable official asset guidance; never crowd the logo or place it on a busy background

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
- **Top-right Google G mark**（页眉右上角）: `google_g_logo.svg` 24×24 at `x=1216 y=36`, one per content page.
- **Page top accent bar**: 1280×6 `#4285F4` 细条在页面最顶部（封面/结尾页用四色分段 14px 条）。
- **Footer area**（页脚）: 页码 + 章节名，16px `#9AA0A6`；`第三章 · 章节名` 居左、页码 `NN` 居右（`x=1240 text-anchor=end`），组 bounds 约 `40 660 1200 40`。
- **Section pages** use §VII instead; cover/ending pages are exempt from this header.
