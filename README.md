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

### Python Scripts
All scripts (`scripts/check_links.py`, `scripts/site_sprint.py`) rely strictly on the standard library with zero external pip dependencies. Virtual environments (`.venv`) are optional.
