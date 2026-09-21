#!/usr/bin/env pwsh
# Strict test suite for arunsrin's notes (Native PowerShell / Windows)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Refresh PATH from registry so newly installed CLI tools are immediately discoverable
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "py" }

Write-Host "=== 1. Running strict Hugo build ===" -ForegroundColor Cyan
hugo --gc --minify --panicOnWarning
if ($LASTEXITCODE -ne 0) {
    Write-Error "Hugo build failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 2. Validating JSON indexes ===" -ForegroundColor Cyan
jq . public/index.json | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "public/index.json is invalid!"
    exit $LASTEXITCODE
}
Write-Host "[OK] public/index.json is valid" -ForegroundColor Green

jq . public/static/quotes.json | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "public/static/quotes.json is invalid!"
    exit $LASTEXITCODE
}
Write-Host "[OK] public/static/quotes.json is valid" -ForegroundColor Green

Write-Host "`n=== 3. Checking internal links ===" -ForegroundColor Cyan
$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "py" }
& $pythonCmd "$PSScriptRoot/check_links.py" "$PSScriptRoot/../public"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Internal link check failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 4. Running JavaScript & Cloudflare safety tests ===" -ForegroundColor Cyan
node "$PSScriptRoot/test_js.js"
if ($LASTEXITCODE -ne 0) {
    Write-Error "JavaScript / Cloudflare safety tests failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 5. Validating Related Notes & Mentions ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_related_notes.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Related Notes & Mentions validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 6. Validating Search Relevance & Scoring ===" -ForegroundColor Cyan
node "$PSScriptRoot/test_search.js"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Search Relevance & Scoring validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 7. Validating Tech Folder Animated Emojis ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_tech_emojis.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tech Folder Animated Emojis validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 8. Validating Homepage Cards Consistency ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_homepage_cards.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Homepage Cards Consistency validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 9. Validating Mobile Sidebar & Overlay Stacking ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_mobile_sidebar.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Mobile Sidebar & Overlay validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 10. Validating GitHub CI Parity & Test Discovery ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_ci_parity.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "CI Parity validation failed! Tests in scripts/ are missing from .github/workflows/ci.yml"
    exit $LASTEXITCODE
}

Write-Host "`n=== 11. Validating Tag Taxonomy Regression ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_tags.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tag taxonomy regression validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 12. Validating Sitemap & Recently Tended Stream ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_sitemap_and_recent.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Sitemap & Recently Tended Stream validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 13. Validating Title Bar & Sidebar UX ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_title_sidebar_ux.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Title Bar & Sidebar UX validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 14. Validating ASCII Banner & HTML Source Easter Egg ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_ascii_banner.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "ASCII Banner & HTML Source Easter Egg validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 15. Validating Chronological Posts & Dispatches Space ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_posts.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Chronological Posts & Dispatches validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== 16. Validating Fill-Paragraph Prose Linter ===" -ForegroundColor Cyan
& $pythonCmd "$PSScriptRoot/test_fill_paragraph.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Fill-Paragraph Prose Linter validation failed!"
    exit $LASTEXITCODE
}

Write-Host "`n=== All checks passed successfully! ===" -ForegroundColor Green

exit 0

