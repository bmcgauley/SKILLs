---
name: podcast-episode-producer
description: Complete podcast episode content production workflow. This skill should be used when a user provides a podcast transcript and needs a full suite of publishing assets generated including a blog post, slide deck prompt, YouTube title/description with chapter markers, cross-platform social copy, a Buffer queue schedule, an infographic description, and a full image brief system (A/B YouTube thumbnails paired with titles, and primary episode art in 16:9 and 1:1). Produces all outputs in a consistent order with copy-paste-ready sections for each publishing platform. Designed to be reusable across any podcast show — brand configuration is stored in references/brand.md and references/show-config.md and must be set up before first use.
---

# Podcast Episode Producer

## Overview

This skill transforms a raw podcast transcript into a complete, publish-ready content suite. It is show-agnostic — all brand identity and show configuration live in the reference files. Before using this skill for a new show, configure `references/brand.md` and `references/show-config.md`.

**Trigger:** User drops a transcript (PDF, text, or document) and asks for episode assets, publishing materials, show notes, or any combination of the deliverables below.

**Always read before starting:**
- `references/brand.md` — visual identity, colors, typography, platform specs
- `references/show-config.md` — show name, hosts, URLs, CTA links, posting schedule defaults

---

## Pre-Production: Episode Extraction

Before generating any deliverable, extract and confirm the following from the transcript:

```
EPISODE METADATA
- Show name: [from show-config.md]
- Episode title (working): [derive from transcript's biggest story]
- Date range covered: [stated in transcript or inferred]
- Number of sections/chapters: [count from transcript structure]
- Chapter titles and timestamps: [extract or approximate from transcript]
- Top 3 stories: [the three highest-impact items]
- Single most provocative hook: [the one thing that makes someone click]
- Key stats/numbers: [pull all specific numbers mentioned]
```

Present this block to the user for confirmation if any item is ambiguous. Otherwise proceed directly.

---

## Output Sequence

Produce all deliverables in this exact order. Each section must be clearly headed and self-contained for copy-paste use.

---

### DELIVERABLE 1 — Blog Post

**Format:** Long-form article for dual publication (Substack + primary blog)

**Requirements:**
- Apply `references/human-writing-standards.md` throughout — no AI clichés, varied sentence structure, authentic voice
- Open with a strong, specific first paragraph — no generic scene-setting
- Use H2 headers for each podcast chapter/section
- Insert `[SLIDE IMAGE: description]` placeholders at the top of each section — describe what the corresponding slide deck slide shows so the user knows where to place images after generating the deck
- Write each section as narrative prose drawn from the transcript — synthesize, don't transcribe
- Include a minimum of one key stat or data point per section, pulled from the transcript
- End each section with a forward-leaning sentence that flows into the next
- Final section: synthesis/thesis paragraph — what does this week/episode actually mean
- After the thesis: CTA block formatted as follows:

```
[BUYMEACOFFEE BUTTON: "label text → buymeacoffee.com/[handle from show-config.md]"]
[SUBSCRIBE BUTTON (Substack): "label text"]
[LISTEN BUTTON: "label text — platform links"]
```

- Footer: show name, host name, primary URL, secondary URL
- Length: Substantive. Match depth to transcript length. Do not truncate.

---

### DELIVERABLE 2 — Slide Deck Prompt (NotebookLM / AI Presentation Tool)

**Format:** One-shot prompt the user pastes directly into their presentation generator

**Structure of the prompt:**

Open with brand identity block (pull from `references/brand.md`):
- Background color
- Primary and secondary accent colors and their uses
- Typography specification
- Footer template (show branding, source, date range)
- Category badge style and position
- Overall visual mood descriptor

Then list slides in order, one per podcast chapter plus:
- Title slide (Slide 1)
- One slide per chapter (labeled with chapter name and badge)
- Week-in-review / thesis slide
- Closing / CTA slide

For each chapter slide specify:
- Badge label in brackets
- Primary stat or headline for large-text treatment
- Supporting callouts (secondary data points)
- Any visual element recommendation (map, chart, flow diagram, icon)
- Any pull quote for a quote bar

Close the prompt with: "Use the provided transcript as source material for all factual claims. Maintain the [mood from brand.md] throughout. No light backgrounds."

---

### DELIVERABLE 3 — YouTube

Present as two paired blocks — A and B. Each block contains all four elements together so the title/image relationship is explicit.

**Block format for each:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUTUBE THUMBNAIL [A or B]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PAIRED YOUTUBE TITLE:
[Title text — written so it works with the image text, not duplicating it]

IMAGE DESCRIPTION:
[Episode-specific scene/composition prompt for image generation tool.
 No text described here — text is handled by application fields below.
 Include: subject, composition, mood, lighting, background elements, 
 camera angle, 16:9 with center-safe zone for 1:1 crop.]

APPLICATION FIELDS:
  Main Headline: [Short, punchy — plays WITH the YouTube title]
  Subheadline: [Optional — only include if it adds contrast or tension]
  CTA: [Optional — if used, subtle, positioned bottom-right, echoes title]

BRAND INSTRUCTIONS:
  Main headline: [typeface, weight, color, size descriptor, position]
  Subheadline: [typeface, weight, color, size descriptor, position — or "not used"]
  CTA: [typeface, weight, color, size descriptor, position — or "not used"]
  [Pull remaining specs from references/brand.md]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Thumbnail A:** Bolder, more literal — represents the episode's biggest single story  
**Thumbnail B:** More conceptual or provocative — plays on tension, irony, or the unexpected angle

After both thumbnail blocks, produce the full YouTube description:

```
YOUTUBE DESCRIPTION:
[2–3 paragraph description — hook paragraph, content summary paragraph, community/CTA paragraph]

📌 CHAPTERS:
[Timestamp — Chapter title]
[Repeat for all chapters derived from transcript]

🔑 KEY STORIES THIS WEEK:
[Arrow-prefixed one-liners for each major story]

🚀 JOIN THE COMMUNITY:
[Pull all links from show-config.md]

[Hashtag block — mix show-specific tags from show-config.md with episode-specific topic tags]
```

---

### DELIVERABLE 4 — Primary Episode Images (Podcast Art)

Two image briefs — same episode, same composition intent, two aspect ratios. These are the canonical episode images used on RSS feeds, Apple Podcasts, Spotify, and as the primary social post image. All fields are required.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY EPISODE IMAGE — 16:9
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMAGE DESCRIPTION:
[Same scene/composition as A/B thumbnails but composed for full episode 
 identity — richer, more complete. Subject centered for safe 1:1 crop.
 No text described — handled by fields below.]

APPLICATION FIELDS:
  Main Headline: [Full episode title or show name + episode hook]
  Subheadline: [The three top story hooks]
  CTA: [Full CTA — readable, complete, e.g., "Listen Now → mcgauleylabs.news"]

BRAND INSTRUCTIONS:
  [Full typeface, color, weight, position specs for all three fields]
  [Pull from references/brand.md]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIMARY EPISODE IMAGE — 1:1 CROP NOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use identical fields as 16:9 above.
Crop instruction: Center square of the 16:9 image.
Verify subject and all three text fields remain fully visible in the crop.
If not, note which field to reposition before cropping.
```

---

### DELIVERABLE 5 — SEO Keywords

Generate a keyword set for the episode and apply the correct optimized mix to every platform that supports keywords, tags, or hashtags. Produce the keyword set first, then embed the platform-specific optimized selections directly inside each platform's copy block in Deliverable 6.

**Keyword Set Structure:**

```
PRIMARY KEYWORDS (broad, high-volume — 8–12 terms):
[comma-separated list]

SECONDARY KEYWORDS (entity/topic-specific — 15–25 terms):
[comma-separated list — show name, guest names, company names, model names, key topics]

LONG-TAIL KEYWORDS (specific phrases, lower competition — 15–25 phrases):
[comma-separated list — conversational queries, specific claims, niche audience hooks]
```

**Platform Keyword Limits & Format Rules:**

| Platform | Format | Limit | Mix Strategy |
|---|---|---|---|
| YouTube Tags | comma-separated, no # | 500 characters total | 5–6 primary + 8–10 secondary + 4–5 long-tail |
| YouTube Description | natural language inline | No tag limit in body | Weave 3–4 primary naturally into first 200 chars |
| Instagram | hashtags (#) | 30 tags max | 4–5 primary + 8–10 secondary + 4–6 long-tail |
| LinkedIn | hashtags (#) | 5–8 recommended | 3 primary + 2–3 secondary only — quality over quantity |
| RSS.com | comma-separated or tags field | varies by platform | 5 primary + 5 secondary — highest clarity terms only |
| Blog/Substack | inline natural language + meta keywords | meta: 10–15 phrases | Mix all tiers naturally; front-load primary in title/H2s |

**Application rules:**
- Embed the optimized keyword/hashtag block directly at the bottom of each platform's copy in Deliverable 6 — do not list keywords separately from the copy that uses them
- For blog posts: include a meta keywords line at the end of the post (comma-separated, no #), and ensure primary keywords appear naturally in the title, at least two H2 headers, and the opening paragraph
- YouTube tags go in a dedicated TAGS field below the description, not embedded in description body
- Never repeat the same hashtag twice on a single platform
- Instagram: place hashtag block after the CTA line, separated by a line break
- LinkedIn: place 3–5 hashtags at the very end of the post, on their own line

---

### DELIVERABLE 6 — Cross-Platform Descriptions

Produce one block per platform, clearly labeled:

**RSS.com (Podcast Listing)**
```
Title: [Episode title]
Description: [3–4 sentence summary. Hook sentence. Content overview. Source/credibility line. Listen CTA.]
```

**Instagram Caption**
```
[Hook line — bold statement or provocative question, no hashtags yet]
[2–3 lines of content context]
[CTA line with link direction]
[Hashtag block — 8–12 tags, mix broad and niche]
```

**LinkedIn Post**
```
[Opening statement — professional framing of the episode's business/strategic angle]
[Bullet list of 4–6 key stories with brief context — professional audience lens]
[Closing insight sentence]
[CTA + link]
[Hashtag block — 5–8 professional tags]
```

---

### DELIVERABLE 7 — Buffer Queue (7-Day Posting Schedule)

**Default schedule** (override with show-config.md settings if specified):
- Episode airs: Sunday
- Promotion window: Sunday through following Saturday
- Next episode teaser: Saturday

Produce as a table:

| Day | Platform | Time | Post Type | Content Summary |
|---|---|---|---|---|
| [Day] | [Platform] | [Time] | [Type] | [What to post — brief description or first line of copy] |

**Post types across the week:**
- Day 1 (Sunday): Full launch posts on all platforms simultaneously
- Day 2 (Monday): Biggest single stat or story as a standalone post
- Day 3 (Tuesday): Quote card — most provocative line from the episode
- Day 4 (Wednesday): Educational explainer — one concept from the episode, drives to blog
- Day 5 (Thursday): Most unexpected/weird story — curiosity hook
- Day 6 (Friday): Reminder + "catch up before next episode" CTA
- Day 7 (Saturday): Teaser for next episode or open question to audience

Adjust platform mix per show-config.md. Default platforms: YouTube, Instagram, LinkedIn, RSS.

---

### DELIVERABLE 8 — Infographic Description

```
FORMAT RECOMMENDATION: [Landscape 16:9 for LinkedIn/Twitter/YouTube community post; 
Square 1:1 crop for Instagram. State which is primary.]

TITLE BAR: [Show name | Episode date range]
SUBTITLE: [Episode title]

DESIGN SYSTEM:
[Pull background, accent colors, typography from references/brand.md]
[Describe grid/overlay style consistent with brand]
[Describe footer bar — show URL, secondary URL, support link]

PANEL LAYOUT: [Number of panels based on chapter count — typically 4–6]

Panel 1 — [SECTION NAME] [badge color]:
  Primary stat: [largest number or boldest claim from this chapter]
  Supporting callouts: [2–3 secondary data points]
  Visual element: [icon, map, chart type, or illustration suggestion]

[Repeat for each chapter]

FOOTER BAR (full width):
  [Pull all URLs from show-config.md]

PRODUCTION NOTE: Build in Canva using brand hex codes. 
Generate landscape first, export, then crop to 1:1 for Instagram.
```

---

## Quality Standards

Apply these checks before delivering any output:

**Writing (Blog Post):**
- Scanned for AI cliché phrases — none present
- No em dash overuse (max one per 3–4 paragraphs)
- No lists of exactly three unless genuinely appropriate
- Varied sentence length and structure throughout
- Specific data points, not vague generalities
- Each section earns its word count — no padding

**Completeness:**
- All 8 deliverables present
- Keyword set generated and embedded in every platform block that supports tags/hashtags
- Platform-specific keyword limits respected (YouTube 500 chars, Instagram 30 tags, LinkedIn 5–8 tags)
- All `[SLIDE IMAGE]` placeholders in blog post
- All CTA links populated from show-config.md
- Thumbnail A and B are visually and textually distinct from each other
- Thumbnail image text does not duplicate the paired YouTube title
- 16:9 primary image confirmed safe for center 1:1 crop

**Brand:**
- All colors reference hex codes from brand.md
- Typography specs consistent across all image briefs
- Show name and URLs consistent with show-config.md throughout

---

## Reference Files

Load these before beginning any episode:

- `references/brand.md` — Complete visual identity spec
- `references/show-config.md` — Show name, hosts, URLs, CTAs, platform preferences, posting schedule
- `references/human-writing-standards.md` — Writing quality rules (anti-AI patterns, voice, structure)
