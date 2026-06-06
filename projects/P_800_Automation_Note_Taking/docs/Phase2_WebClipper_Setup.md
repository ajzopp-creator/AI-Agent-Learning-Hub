# P_800 — Phase 2: Plugin Setup Guide
## Obsidian Web Clipper + Defuddle
**Version:** 1.0  
**Date:** 2026-03-08  
**Project:** P_800 Automation Note-Taking  
**Status:** Ready to implement

---

## What This Guide Covers

1. Update Web Clipper from 0.2.9 → latest (Chrome)
2. New interface walkthrough
3. How Defuddle works (automatic — nothing to configure)
4. Custom templates for your 5 clipping sources
5. Daily workflow using Web Clipper → Obsidian

---

## Step 1 — Update Web Clipper in Chrome

You are on version **0.2.9**. Defuddle requires **0.10.9 or later**.
This is a one-click update — no coding required.

### How to Update

1. Open Chrome
2. In the address bar type: `chrome://extensions` and press Enter
3. In the top-right corner, enable **Developer mode** (toggle switch)
4. Click **Update** button that appears at the top-left
5. Wait a few seconds — all extensions update including Web Clipper
6. Turn **Developer mode** back off
7. Click the puzzle piece icon (🧩) in Chrome toolbar
8. Find **Obsidian Web Clipper** and click the pin icon to keep it visible

### Verify the Update
1. Click the Obsidian Web Clipper icon in your toolbar
2. Click the **gear icon** (⚙️) to open Settings
3. Scroll to the bottom — you should see version **0.10.9** or higher

> ⚠️ **Important:** The interface looks completely different from 0.2.9.
> This is normal — you are getting a major upgrade. The guide below
> walks you through everything new.

---

## Step 2 — New Interface Walkthrough

After updating, Web Clipper has four main sections accessible from the gear icon:

| Tab | What It Does |
|-----|-------------|
| **General** | Vault connection, default folder, file naming |
| **Templates** | Site-specific clipping rules (this is where you'll spend time) |
| **Highlights** | Manage saved highlights |
| **Properties** | Obsidian frontmatter fields |

### First-Time Setup — Connect Your Vault

1. Click the Web Clipper icon → gear icon ⚙️
2. Go to **General**
3. Under **Vault**, select your Obsidian vault name from the dropdown
4. Under **Default folder**, type the path where clipped notes should go:
   ```
   Clippings
   ```
   *(or whatever folder you use in Obsidian — create it first if needed)*
5. Under **Note name**, use:
   ```
   {{title}} {{date}}
   ```
   This names each clipped note with the page title + today's date.

---

## Step 3 — How Defuddle Works (Automatic)

**You don't need to configure anything for Defuddle.** It runs automatically.

Every time you clip a page, Web Clipper uses Defuddle to:
- Strip ads, banners, navigation menus, footers, cookie notices
- Keep only the main article or content
- Use the site's own mobile styles to identify what's clutter
- Convert the clean content to Markdown

**Before Defuddle (old version 0.2.9):**
You'd get the full messy page — ads, nav bars, sidebars, all of it.

**After Defuddle (new version):**
You get clean, readable Markdown — just the content you actually want.

The templates below make it even better by telling Web Clipper exactly
what to do with each specific site.

---

## Step 4 — Custom Templates for Your Sources

Templates tell Web Clipper how to handle specific websites automatically.
When you clip a page, Web Clipper matches the URL and applies the right template.

**How to create a template:**
1. Click Web Clipper icon → gear icon ⚙️ → **Templates**
2. Click **+ New template**
3. Fill in the fields as shown below for each source
4. Click **Save**

---

### Template 1 — WhatsApp Web (Impens & Anderssen)

> Use this when you open WhatsApp Web and want to clip a channel's messages
> into your Obsidian daily note.

| Field | Value |
|-------|-------|
| **Template name** | WhatsApp Trading Channel |
| **Trigger URL** | `https://web.whatsapp.com` |
| **Note name** | `WhatsApp {{author}} {{date}}` |
| **Folder** | `Daily-Notes/Clippings` |

**Template body — paste this exactly:**
```
## 💬 WhatsApp — {{title}}
**Date:** {{date}}
**Channel:** {{author}}

---

{{content}}

---
*Clipped via Web Clipper · {{url}}*
```

**How to use it each morning:**
1. Open WhatsApp Web in Chrome
2. Open the Impens (Pioneer Club) channel
3. Scroll to today's messages
4. Click Web Clipper icon
5. Template auto-applies → click **Add to Obsidian**
6. Repeat for Anderssen (Club 84) channel

> 💡 **Tip:** WhatsApp Web can be tricky to clip because messages are
> dynamically loaded. If content is missing, try selecting the messages
> manually first (highlight them), then clip — Web Clipper will capture
> your selection.

---

### Template 2 — Investors.com Big Picture

> Use this to clip the daily Big Picture column for your market posture section.
> Defuddle will strip the Investors.com ads and paywalled sidebars automatically.

| Field | Value |
|-------|-------|
| **Template name** | IBD Big Picture |
| **Trigger URL** | `https://www.investors.com/market-trend/the-big-picture` |
| **Note name** | `IBD Big Picture {{date}}` |
| **Folder** | `Daily-Notes/Clippings` |

**Template body:**
```
## 📰 IBD Big Picture — {{date}}
**Source:** Investors.com
**URL:** {{url}}

---

{{content}}

---
*Clipped via Web Clipper + Defuddle*
```

> 💡 **Tip:** This feeds directly into your P_010 Market Posture workflow.
> Clip it first, then open P_010 to run your analysis.

---

### Template 3 — X (Twitter) Trading Posts

> Use this to clip posts from trading accounts you follow —
> analyst commentary, setup alerts, market calls.

| Field | Value |
|-------|-------|
| **Template name** | X Trading Post |
| **Trigger URL** | `https://x.com` |
| **Note name** | `X Post {{author}} {{date}}` |
| **Folder** | `Daily-Notes/Clippings` |

**Template body:**
```
## 🐦 X Post — {{author}}
**Date:** {{date}}
**URL:** {{url}}

---

{{content}}

---
*Clipped via Web Clipper*
```

> 💡 **Tip:** For X/Twitter, clip individual post pages
> (not the main feed) for the cleanest results.
> Navigate to the post itself, then clip.

---

### Template 4 — News Articles & Research Pages

> General-purpose template for financial news, research reports,
> analyst notes — any article you want to save to Obsidian.

| Field | Value |
|-------|-------|
| **Template name** | Research Article |
| **Trigger URL** | *(leave blank — this is the default fallback)* |
| **Note name** | `{{title}} {{date}}` |
| **Folder** | `Daily-Notes/Clippings` |

**Template body:**
```
## 📄 {{title}}
**Source:** {{site}}
**Date:** {{date}}
**URL:** {{url}}

---

{{content}}

---
*Clipped via Web Clipper + Defuddle*
```

> 💡 **Tip:** Set this as your **default template** in General settings.
> It will apply to any site that doesn't match a specific template above.

---

### Template 5 — Other Websites (Catch-All)

> For anything that doesn't fit the templates above —
> charts, tools, data pages, forums.

| Field | Value |
|-------|-------|
| **Template name** | General Clip |
| **Trigger URL** | *(leave blank)* |
| **Note name** | `Clip {{title}} {{date}}` |
| **Folder** | `Clippings` |

**Template body:**
```
## 🔗 {{title}}
**Date:** {{date}}
**URL:** {{url}}

---

{{content}}

---
```

> 💡 **Tip:** If you clip the same site repeatedly, create a dedicated
> template for it just like the ones above. The more specific the
> trigger URL, the cleaner the result.

---

## Step 5 — Template Priority Order

Web Clipper checks templates top-to-bottom and applies the first match.
Set your template order like this in the Templates tab
(drag to reorder):

| Order | Template | Why |
|-------|----------|-----|
| 1 | WhatsApp Trading Channel | Most specific URL |
| 2 | IBD Big Picture | Most specific URL |
| 3 | X Trading Post | Broad domain |
| 4 | Research Article | Broad fallback |
| 5 | General Clip | Last resort catch-all |

---

## Step 6 — Daily Morning Workflow

Once templates are set up, your morning clipping routine becomes:

```
1. Open WhatsApp Web
   → Open Impens channel → click Web Clipper → Add to Obsidian
   → Open Anderssen channel → click Web Clipper → Add to Obsidian

2. Open Investors.com Big Picture
   → Click Web Clipper → Add to Obsidian
   → Open P_010 → run Market Posture analysis

3. Open X (Twitter)
   → Navigate to any trading post you want to save
   → Click Web Clipper → Add to Obsidian

4. Any other article or research page
   → Click Web Clipper → Add to Obsidian
```

All clipped notes land in `Daily-Notes/Clippings` and are
immediately searchable in Obsidian.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Web Clipper icon not showing | Click 🧩 puzzle piece → pin Obsidian Web Clipper |
| Content missing from clip | Try selecting text first, then clip |
| Clip goes to wrong folder | Check template folder path in Settings → Templates |
| Obsidian not receiving clip | Make sure Obsidian is open on your desktop |
| WhatsApp messages not captured | Scroll messages into view first, then clip |
| Old version still showing | Repeat Step 1 update process |

---

## File Locations

| File | Path |
|------|------|
| This guide | `P_800_Automation_Note_Taking\docs\Phase2_WebClipper_Setup.md` |
| Daily note template | `P_800_Automation_Note_Taking\templates\Daily-Flow.md` |

---

## What's Next — Phase 4

After Web Clipper is working, Phase 4 builds the
**WhatsApp Chat Formatter artifact** — a Claude tool that takes your
raw WhatsApp clips and formats them into clean, structured Obsidian
note sections with one click.

Phase 2 (clipping) feeds Phase 4 (formatting). Get this working first.
