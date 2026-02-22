# podcast-episode-producer

A complete podcast episode content production skill for Claude. Drop a transcript, get every publishing asset you need — blog post, slide deck prompt, YouTube title/description with chapters, cross-platform social copy, a 7-day Buffer queue, an infographic description, and a full image brief system.

## Structure

```
podcast-episode-producer/
├── SKILL.md                          # Main skill instructions
└── references/
    ├── brand.md                      # Visual identity spec (pre-configured for Imaginarii Labs)
    ├── show-config.md                # Show name, URLs, CTAs, schedule (pre-configured for McGauley Labs)
    └── human-writing-standards.md   # Anti-AI writing patterns and quality standards
```

## Setup for a New Show

1. Duplicate `references/brand.md` and replace all values with the new show's visual identity
2. Duplicate `references/show-config.md` and replace all values with the new show's details
3. Keep `SKILL.md` and `references/human-writing-standards.md` unchanged — these are show-agnostic

## Usage

Trigger by dropping a transcript and asking for episode assets. Claude will:

1. Extract episode metadata (title options, date range, chapters, key stats)
2. Produce all 7 deliverables in order:
   - Blog post (with slide image placeholders and CTA blocks)
   - Slide deck prompt (NotebookLM-ready, one-shot)
   - YouTube: Title A + Thumbnail A brief, then Title B + Thumbnail B brief
   - Primary episode images (16:9 and 1:1 crop brief)
   - Cross-platform descriptions (RSS, Instagram, LinkedIn)
   - Buffer queue (7-day posting schedule)
   - Infographic description

## Image System

**4 images per episode:**

| Image | Purpose | Fields Required |
|---|---|---|
| Thumbnail A | YouTube A/B test — literal/direct | Headline (plays with Title A), subheadline optional, CTA optional |
| Thumbnail B | YouTube A/B test — conceptual/provocative | Headline (plays with Title B), subheadline optional, CTA optional |
| Primary 16:9 | Canonical episode art — all platforms | All three fields required |
| Primary 1:1 | Center crop of 16:9 | Same fields, verify crop |

Thumbnail A and B are always presented paired with their YouTube title so the relationship is explicit. Text is never described in the image generation prompt — all text is handled by the application fields and brand instructions.

## Current Configuration

- **Show:** This Week in AI / McGauley Labs
- **Host:** Brian McGauley
- **Brand:** Imaginarii Labs (black + cyan + magenta, Space Mono)
- **Posting schedule:** Sundays, 7-day promotion window

## Part of the Imaginarii Skills Repository

`imagi-narii.com` | `mcgauleylabs.news`
