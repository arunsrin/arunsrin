# arunsrin

Static site for all my snippets, notes, etc. Powered by [Hugo](https://gohugo.io/).

Currently hosted using Cloudflare Pages, at [https://www.arunsr.in](https://www.arunsr.in).

## Installation / Usage

```sh
git clone git@github.com:arunsrin/arunsrin.git
cd arunsrin
hugo server # test locally (http://localhost:1313/)
hugo build  # builds site to ./public/
```

### Testing

The test suite runs identical validation (Hugo strict build, JSON index verification, internal link check, and Cloudflare/JS safety checks) across both environments:

**Windows PowerShell:**
```powershell
./scripts/test.ps1
```

**WSL / Linux / macOS:**
```bash
./scripts/test.sh
```

### Publishing a New Post

To create a new chronological post or announcement in `/posts/`:

1. **Scaffold a new post using Hugo:**
   ```bash
   hugo new posts/my-post-title.md
   ```
   *(Or simply create a file directly under `home/posts/<post-title>.md`)*

2. **Edit the frontmatter and write your note:**
   Open `home/posts/my-post-title.md`:
   ```yaml
   ---
   title: "My Post Title"
   date: 2026-09-21T14:00:00+05:30
   description: "A short summary or excerpt for the card snippet."
   tags:
     - meta
   ---

   Write your post here using standard Markdown...
   ```

3. **Verify and build:**
   ```bash
   hugo server   # Preview live at http://localhost:1313/posts/
   ./scripts/test.ps1  # Run tests before committing
   ```

### Python Scripts
All scripts (`scripts/check_links.py`, `scripts/site_sprint.py`) rely strictly on the standard library with zero external pip dependencies. Virtual environments (`.venv`) are optional.
