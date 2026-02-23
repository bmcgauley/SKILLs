---
name: adsense-audit
description: Comprehensive Google AdSense compliance audit skill. This skill should be used when a user wants to audit a website for AdSense approval, troubleshoot a "Low Value Content" rejection, assess policy violations, or improve a site's eligibility for Google AdSense monetization. Applies to new applicants, rejected sites, and sites seeking to improve ad performance.
---

# AdSense Audit Skill

## Purpose

To systematically audit any website against Google AdSense Program Policies, identify specific violations or weaknesses causing rejection, and produce an actionable remediation plan with a prioritized fix list.

## When to Use This Skill

- User receives AdSense rejection (especially "Low Value Content", "Policy Violations", "Site Not Ready")
- User wants to proactively prepare a site for AdSense application
- User wants to improve AdSense ad revenue quality
- User shares a screenshot of AdSense policy violations dashboard

## Audit Workflow

### Step 1: Gather Site Intelligence

Use bash_tool with curl and Python HTML parsing to crawl:
- Homepage (structure, purpose clarity, navigation)
- Blog index (post volume, frequency, categories)
- 2-3 individual blog/content posts (depth, originality, word count)
- About page (E-E-A-T signals: author credentials, expertise)
- Shop/product pages if present (affiliate/e-commerce ratio)
- Contact, Privacy Policy, Terms pages (trust signals)

Capture for each page: total character count of text content, page purpose, content signals.

### Step 2: Policy Areas to Audit (load references/adsense-policies.md)

1. Content Quality / Thin Content — most common rejection reason
2. E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)
3. Prohibited Content (adult, violence, hate, drugs, weapons)
4. Ad Implementation (click fraud, deceptive placement, self-clicking)
5. Traffic Quality (no artificial/paid traffic to ad pages)
6. Navigation and UX (clear nav, no broken links, no excessive popups)
7. Copyright (no scraped/reposted content without rights)
8. Required Pages (About, Privacy Policy, Contact)
9. Affiliate Content Ratio (not primarily affiliate without added value)
10. Language Support (content in AdSense-supported language)

### Step 3: Score Each Area

For each of the 10 policy areas, assign: PASS / WARNING / FAIL

### Step 4: Identify Root Cause of "Low Value Content"

Check specifically:
- Total number of indexed content pages
- Average word count per post (1,000+ words expected for substantive posts)
- Content type: original analysis vs. news aggregation vs. AI summaries
- AI-generated content disclosure without sufficient added original value
- Recency and posting frequency (not all in one burst)
- Whether primary purpose is e-commerce vs. content

### Step 5: Produce Audit Report

Structure:
```
## AdSense Audit: [Site Name]
Audit Date | Rejection Reason | Overall Readiness

### Executive Summary
### Policy Compliance Scorecard (table)
### Detailed Findings (per violation: What Google Sees, Policy Violated, Fix, Time to Fix)
### Remediation Roadmap (Phase 1/2/3)
### Resubmission Checklist
```

Save as /mnt/user-data/outputs/adsense-audit-[sitename].md

## Fast-Reference: "Low Value Content" Causes

Google flags pages that are:
- Primarily news aggregation/summaries without original insight
- AI-generated without disclosed added original value
- Thin (under 500 words of original text)
- Auto-generated or templated
- Part of a site with too few total content pages (fewer than 15-25)
- Published in a burst (not a consistent history over time)
- Behind login walls
- Primarily affiliate/e-commerce without supporting editorial content

## E-E-A-T Quick Checklist

- Author bio with real credentials visible on content pages
- About page establishes who runs the site and expertise
- External citations and sources linked within posts
- Contact information accessible
- Privacy Policy present and comprehensive
- Content shows lived experience, not just information aggregation

## Content Volume Benchmarks for AdSense Approval

- Minimum 15-25 published posts before applying
- Each post: 800-1,500+ words of original analysis
- Posts published over at least 3-6 months (not all at once)
- Mix of evergreen and timely content

## Site Structure Requirements

- Clear functional navigation, no broken links
- About, Contact, Privacy Policy all present
- No login walls blocking primary content
- Mobile responsive
- Fast load speed (Core Web Vitals pass)
