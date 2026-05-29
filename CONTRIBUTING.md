# Contributing to the CUNY AI Lab Website

This guide covers how to make content changes and submit them for review.

## Quick Reference: What to Edit

| What you want to change | File to edit |
|---|---|
| Homepage text/links | `src/data/homepage.json` |
| About page text | `src/content/pages/about.md` |
| Contact page text | `src/content/pages/contact.md` |
| Team members | `src/data/team.json` |
| Tools descriptions | `src/data/tools.json` |
| Resources list | `src/data/resources.json` |
| Events | `src/data/events.json` |
| Request Access form | `src/data/request-access.json` |
| Model registry | `src/data/model-registry.json` |

## Making Changes on GitHub.com

1. **Go to the repo**: https://github.com/CUNY-AI-Lab/CUNY-AI-Lab-website
2. **Navigate to the file** you want to edit (see table above)
3. **Click the pencil icon** (Edit this file) in the top-right of the file view
4. **Make your changes** in the editor
5. **Click "Commit changes..."** (green button)
6. **Select "Create a new branch for this commit and start a pull request"**
7. **Give your branch a short name** describing the change (e.g., `update-team-bios`)
8. **Click "Propose changes"**, then **"Create pull request"**
9. **Add a brief description** of what you changed and why, then submit

An admin will review and merge your PR. You'll get a GitHub notification when it's approved.

## Editing Tips

### Markdown files (`.md`)

Files like `about.md` and `contact.md` use Markdown. The section between the `---` lines at the top is called **frontmatter** (structured data). The text below is the page content.

```markdown
---
title: About the Lab
---

This is the page content. You can use **bold**, *italics*, and [links](https://example.com).
```

### JSON files (`.json`)

Most page data lives in JSON files. Be careful with the syntax:
- All strings must be in `"double quotes"`
- No trailing commas after the last item in a list
- Use `\"` for quotes inside strings

Example — adding a team member to `team.json`:
```json
{
  "name": "New Person",
  "title": "Their Title",
  "subtitle": "Their Department",
  "photo": "images/team/new-person.jpg",
  "photo_position": "center"
}
```

### Adding images

If your change includes a new image (e.g., team photo):
1. Navigate to the target folder (e.g., `public/images/team/`)
2. Click **"Add file" > "Upload files"**
3. Upload your image, commit to a new branch
4. Team photos should be resized to max 800px width before uploading

## Making Changes Locally (Optional)

If you prefer working on your own computer:

```bash
# Clone the repo
git clone https://github.com/CUNY-AI-Lab/CUNY-AI-Lab-website.git
cd CUNY-AI-Lab-website

# Install dependencies
npm install

# Create a branch for your changes
git checkout -b your-branch-name

# Start the dev server to preview changes
npm run dev
# Opens at http://localhost:4321

# After making changes, commit and push
git add .
git commit -m "Brief description of changes"
git push -u origin your-branch-name
```

Then go to GitHub and create a pull request from your branch.

## Important

- **Never push directly to `main`** — always use a pull request
- Changes to `main` auto-deploy to the live site at https://ailab.gc.cuny.edu
- If you're unsure about a change, open the PR anyway and ask for feedback in the description
