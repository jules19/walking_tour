# Deployment Guide

> **How to convert this architecture documentation into a beautiful, live website**

This guide shows you how to deploy the Walking Tour architecture documentation as a fast, searchable website using Docsify.

---

## Why Docsify?

- ✅ **Zero build step** - Just serve the files
- ✅ **Beautiful out-of-the-box** - Professional design, no configuration needed
- ✅ **Markdown-native** - Edit documentation as markdown, renders automatically
- ✅ **Mermaid support** - Diagrams render as beautiful SVGs
- ✅ **Full-text search** - Built-in search across all pages
- ✅ **Mobile responsive** - Works perfectly on phones and tablets
- ✅ **Fast** - No JavaScript framework overhead
- ✅ **Free hosting** - Deploy to GitHub Pages at no cost

---

## Quick Start (5 Minutes)

### Option 1: Local Preview

**Step 1: Install Docsify CLI**

```bash
# Using npm
npm i docsify-cli -g

# Or using yarn
yarn global add docsify-cli
```

**Step 2: Serve the docs**

```bash
# Navigate to repository root
cd /path/to/walking_tour

# Serve the docs folder
docsify serve docs

# Open browser to http://localhost:3000
```

That's it! You should see your documentation running locally.

---

### Option 2: Python (No Installation Required)

If you don't have Node.js installed, you can use Python's built-in HTTP server:

```bash
# Navigate to docs folder
cd docs

# Python 3
python -m http.server 3000

# Python 2
python -m SimpleHTTPServer 3000

# Open browser to http://localhost:3000
```

**Note**: Mermaid diagrams and some advanced features work best with the Docsify CLI.

---

## Deploy to GitHub Pages (Free Hosting)

Host your documentation website for free using GitHub Pages.

### Step 1: Push to GitHub

```bash
# Add all files
git add docs/

# Commit
git commit -m "Add architecture documentation website"

# Push to your repository
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/docs`
5. Click **Save**

### Step 3: Access Your Site

GitHub will build your site and provide a URL like:

```
https://jules19.github.io/walking_tour/
```

**Deploy time**: ~2-5 minutes for first deployment, ~30 seconds for updates.

---

## Deploy to Vercel (Alternative)

Vercel offers a bit faster build times and a better deployment workflow.

### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

### Step 2: Deploy

```bash
# Navigate to docs folder
cd docs

# Deploy (first time)
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Scope: Your account
# - Link to existing project? No
# - Project name: walking-tour-docs
# - Directory: ./ (current directory)
# - Build command: (leave empty)
# - Output directory: ./ (current directory)

# Production deployment
vercel --prod
```

### Step 3: Custom Domain (Optional)

```bash
# Add custom domain
vercel domains add docs.walking-tour.com
```

**Your site is now live!**

Example: `https://walking-tour-docs.vercel.app`

---

## Deploy to Netlify (Alternative)

Netlify is another excellent option with drag-and-drop deployment.

### Option A: Drag and Drop (Easiest)

1. Go to [netlify.com](https://netlify.com)
2. Sign up / Log in
3. Drag the `docs` folder onto the Netlify dashboard
4. Done! Your site is live.

### Option B: Git Integration (Automatic Updates)

1. Push your repository to GitHub (see above)
2. Go to [netlify.com](https://netlify.com) and click **New site from Git**
3. Connect to GitHub and select your repository
4. Configure:
   - **Base directory**: `docs`
   - **Build command**: (leave empty)
   - **Publish directory**: `docs`
5. Click **Deploy site**

**Your site will auto-update** every time you push to GitHub.

---

## Customization

### Change Theme Colors

Edit `docs/index.html` and modify the CSS variables:

```css
:root {
  --theme-color: #4CAF50;  /* Change to your brand color */
  --theme-color-dark: #388E3C;
}
```

**Popular color schemes**:
- **Blue**: `--theme-color: #2196F3;`
- **Purple**: `--theme-color: #9C27B0;`
- **Red**: `--theme-color: #F44336;`
- **Orange**: `--theme-color: #FF9800;`

### Add a Logo

Edit `docs/index.html` and add to the `window.$docsify` config:

```javascript
window.$docsify = {
  name: 'Walking Tour',
  logo: '/_media/logo.png',  // Add this line
  // ... rest of config
}
```

Then add your logo file to `docs/_media/logo.png`.

### Change Font

Add to the `<head>` section in `docs/index.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

<style>
  body {
    font-family: 'Inter', sans-serif;
  }
</style>
```

### Add Google Analytics

Add to `docs/index.html` in the `window.$docsify` config:

```javascript
window.$docsify = {
  // ... existing config
  ga: 'UA-XXXXXXXXX-X',  // Your Google Analytics ID
}
```

---

## Advanced Features

### Dark Mode Toggle

Install the dark mode plugin by adding to `docs/index.html`:

```html
<!-- Add before closing </body> tag -->
<script src="//cdn.jsdelivr.net/npm/docsify-dark-mode@latest/dist/index.min.js"></script>
<link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify-dark-mode@latest/dist/style.min.css"/>
```

### Tabs (for code examples)

```html
<!-- Add before closing </body> tag -->
<script src="https://cdn.jsdelivr.net/npm/docsify-tabs@1"></script>
```

Usage in markdown:

````markdown
<!-- tabs:start -->

#### **Python**

```python
def hello():
    print("Hello!")
```

#### **JavaScript**

```javascript
function hello() {
  console.log("Hello!");
}
```

<!-- tabs:end -->
````

### Pagination (Next/Previous buttons)

Already included in the current setup! Configured in `docs/index.html`:

```javascript
pagination: {
  previousText: 'Previous',
  nextText: 'Next',
  crossChapter: true,
}
```

---

## Updating Documentation

### Workflow

1. **Edit markdown files** in `docs/` folder
2. **Preview changes** locally with `docsify serve docs`
3. **Commit and push** to GitHub
4. **Automatic deployment** (if using GitHub Pages/Netlify/Vercel with Git integration)

### Example Update

```bash
# Edit architecture document
vim docs/ARCHITECTURE.md

# Preview locally
docsify serve docs

# Commit changes
git add docs/ARCHITECTURE.md
git commit -m "Update Phase 2 cost estimates"

# Push (automatically deploys if using Git integration)
git push origin main
```

**GitHub Pages update time**: ~30 seconds
**Netlify/Vercel update time**: ~10 seconds

---

## Troubleshooting

### Mermaid Diagrams Not Rendering

**Solution**: Ensure you're using the Docsify CLI (`docsify serve`) not just a basic HTTP server.

Alternatively, add this to `docs/index.html`:

```html
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
  mermaid.initialize({ startOnLoad: true });
  window.mermaid = mermaid;
</script>
```

### Search Not Working

**Check**: Is the search plugin loaded in `docs/index.html`?

```html
<script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
```

### Images Not Loading

**Ensure** images are in the `docs/` folder or a subfolder like `docs/_media/`.

**Correct path**:
```markdown
![Logo](_media/logo.png)
```

**Incorrect path** (won't work):
```markdown
![Logo](../assets/logo.png)
```

### GitHub Pages 404 Error

**Check**:
1. Repository is public (or you have GitHub Pro for private repos)
2. Settings → Pages → Source is set to `/docs` folder
3. Wait 2-5 minutes after enabling (first deploy takes time)

---

## Performance Optimization

### Enable CDN Caching

Your current setup already uses CDNs for all assets (Docsify, Mermaid, plugins).

### Optimize Images

```bash
# Install imagemagick
brew install imagemagick  # macOS
sudo apt install imagemagick  # Ubuntu

# Compress images
convert input.png -quality 85 output.png
```

### Lazy Load Images

In markdown, use:

```markdown
![Alt text](image.png ':size=800x600')
```

### Lighthouse Score

Run a Lighthouse audit (Chrome DevTools):

```bash
# Target scores with current setup:
Performance: 95+
Accessibility: 90+
Best Practices: 95+
SEO: 100
```

---

## Custom Domain Setup

### GitHub Pages

1. Buy a domain (e.g., `docs.walking-tour.com`)
2. Add a `CNAME` file to `docs/` folder:
   ```
   docs.walking-tour.com
   ```
3. Configure DNS:
   - Type: `CNAME`
   - Name: `docs`
   - Value: `jules19.github.io`
4. Enable HTTPS in GitHub Settings → Pages

### Vercel

```bash
vercel domains add docs.walking-tour.com
```

Follow the DNS configuration instructions provided.

### Netlify

1. Go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Enter `docs.walking-tour.com`
4. Follow DNS configuration instructions
5. Enable HTTPS (automatic with Let's Encrypt)

---

## Backup and Version Control

### Automatic Backups

Since your documentation is in Git, every commit is a backup.

**Best practice**:
```bash
# Create a backup branch before major changes
git checkout -b backup/architecture-v1
git push origin backup/architecture-v1

# Work on main branch
git checkout main
```

### Export to PDF (Optional)

**Option 1: Browser Print**
1. Open documentation in browser
2. File → Print → Save as PDF

**Option 2: docsify-pdf-converter**
```bash
npm i -g docsify-pdf-converter

# Generate PDF
docsify-pdf ./docs --output ./architecture.pdf
```

---

## Monitoring and Analytics

### Track Page Views

Add Google Analytics (see Customization section above).

### Monitor Performance

Use [UptimeRobot](https://uptimerobot.com/) to monitor uptime (free tier: 50 monitors).

### User Feedback

Add a feedback widget:

```html
<!-- Add before closing </body> in docs/index.html -->
<script>
window.$docsify = {
  // ... existing config
  plugins: [
    function(hook, vm) {
      hook.beforeEach(function (html) {
        return html + '\n\n<hr>\n<small><em>Found an error? <a href="https://github.com/jules19/walking_tour/issues">Report it</a></em></small>';
      });
    }
  ]
}
</script>
```

---

## Next Steps

1. ✅ **Deploy locally** - Verify everything works
2. ✅ **Deploy to GitHub Pages** - Get a live URL
3. ⬜ **Share with team** - Gather feedback
4. ⬜ **Customize theme** - Match your brand
5. ⬜ **Add custom domain** - Professional URL
6. ⬜ **Set up analytics** - Track usage

---

## Resources

- [Docsify Documentation](https://docsify.js.org)
- [Mermaid Diagram Syntax](https://mermaid.js.org/intro/)
- [GitHub Pages Guide](https://docs.github.com/en/pages)
- [Vercel Documentation](https://vercel.com/docs)
- [Netlify Documentation](https://docs.netlify.com)

---

## Need Help?

- **Docsify Issues**: [GitHub Issues](https://github.com/docsifyjs/docsify/issues)
- **Project Questions**: [Create an issue](https://github.com/jules19/walking_tour/issues)

---

<p align="center">
  <strong>Your documentation website is ready! 🎉</strong><br>
  <em>Run <code>docsify serve docs</code> to see it in action</em>
</p>
