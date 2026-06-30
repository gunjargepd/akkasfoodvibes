---
name: recipe-generator
description: Local control skill to manually run, verify, or configure the recipe generation pipeline.
---

# Recipe Generator Workspace Skill

This workspace skill provides instructions and helper guidelines for managing, running, and debugging the automated food recipe generation pipeline locally.

## Prerequisites

Before running the generation script locally, ensure you have:
1. Python 3.8+ installed on your system.
2. Dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your `GEMINI_API_KEY` environment variable in your terminal session.
   - **Powershell:** `$env:GEMINI_API_KEY="your-api-key"`
   - **Command Prompt:** `set GEMINI_API_KEY=your-api-key`
   - **Linux/macOS:** `export GEMINI_API_KEY="your-api-key"`

## Common Commands

### 1. Generate Recipes Manually
To trigger the script manually and generate 5 new recipes right now:
```bash
python scripts/generate_recipes.py
```

### 2. Verify Output HTML
The script creates recipe files (e.g. `savory-garlic-butter-salmon.html`) in the root directory. To verify their validity:
- Check that the `recipe-template.html` variables were fully replaced.
- Ensure the `<script type="application/ld+json">` tag contains a valid, well-structured `Recipe` schema.

### 3. Verify Feeds
- Check `feed.xml` to ensure it starts with correct channel metadata and lists the generated recipes with `<content:encoded>` tags.
- Check `sitemap.xml` to ensure all recipe links are included with their publishing dates as `<lastmod>`.
