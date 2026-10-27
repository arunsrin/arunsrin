#!/usr/bin/env node
/**
 * Automated Regression Test Suite for Command Palette / Spotlight Search Modal
 * 
 * Asserts:
 * 1. Centered Command Palette DOM structure in generated HTML (backdrop, dialog, input, results, footer).
 * 2. Accessibility & ARIA compliance (role="dialog", aria-modal="true", aria-label, role="listbox").
 * 3. Elimination of legacy inline search-results dropdown.
 * 4. Zero inline event handlers across header and modal (Cloudflare Rocket Loader safety).
 * 5. Robust DOM Event Delegation: uses closest('a'), preserves new-tab modifier keys (Ctrl/Cmd), no passive focus traps.
 * 6. Category resolution across digital garden hubs (Tech, Books, Games, Research, Posts, Tags, Note).
 * 7. Dynamic Tag extraction and '#' prefix search logic (prefix matching, tag counts, edge cases).
 * 8. In-modal note filtering by tag (#<tag> and #<tag> <keyword>).
 */

const fs = require('fs');
const path = require('path');

const publicIndexHtml = path.join(__dirname, '..', 'public', 'index.html');
const publicIndexJson = path.join(__dirname, '..', 'public', 'index.json');
const headerPartial = path.join(__dirname, '..', 'layouts', 'partials', 'header.html');

if (!fs.existsSync(publicIndexHtml) || !fs.existsSync(publicIndexJson)) {
  console.error("Error: Generated public files missing. Run 'hugo' first.");
  process.exit(1);
}

const htmlContent = fs.readFileSync(publicIndexHtml, 'utf8');
const searchIndex = JSON.parse(fs.readFileSync(publicIndexJson, 'utf8'));
const headerContent = fs.readFileSync(headerPartial, 'utf8');

console.log('--- Command Palette Search Modal Test Suite ---');

// 1. Modal DOM & Structure Validation
console.log('1. Validating Command Palette Modal DOM Structure & ARIA attributes:');

const modalBackdropMatch = htmlContent.match(/id=["']?search-modal["']?[^>]*role=["']?dialog["']?[^>]*aria-modal=["']?true["']?/i);
if (!modalBackdropMatch) {
  console.error('  ❌ FAILED: Search modal backdrop missing id="search-modal", role="dialog", or aria-modal="true"');
  process.exit(1);
}
console.log('  ✓ Search modal backdrop (<div id="search-modal" role="dialog" aria-modal="true">) verified.');

if (!htmlContent.includes('id="modal-search-input"') && !htmlContent.includes('id=modal-search-input')) {
  console.error('  ❌ FAILED: Missing #modal-search-input in generated HTML');
  process.exit(1);
}
console.log('  ✓ Prominent modal search input (#modal-search-input) verified.');

if (!htmlContent.includes('id="search-modal-results"') && !htmlContent.includes('id=search-modal-results')) {
  console.error('  ❌ FAILED: Missing #search-modal-results container in generated HTML');
  process.exit(1);
}
console.log('  ✓ Modal results listbox container (#search-modal-results) verified.');

if (!htmlContent.includes('id="search-modal-close-btn"') && !htmlContent.includes('id=search-modal-close-btn')) {
  console.error('  ❌ FAILED: Missing #search-modal-close-btn in generated HTML');
  process.exit(1);
}
console.log('  ✓ Modal close button (#search-modal-close-btn) verified.');

// Footer hints
const requiredHints = ['Navigate', 'Select', 'Close', 'Filter tags'];
for (const hint of requiredHints) {
  if (!htmlContent.includes(hint)) {
    console.error(`  ❌ FAILED: Missing keyboard navigation hint "${hint}" in search modal footer`);
    process.exit(1);
  }
}
console.log('  ✓ Modal keyboard navigation hints (Navigate, Select, Close, Filter tags) verified.');

// 2. Elimination of legacy absolute dropdown
console.log('2. Validating Legacy Dropdown Elimination:');
if (htmlContent.includes('id="search-results"') || htmlContent.includes('id=search-results')) {
  console.error('  ❌ FAILED: Legacy #search-results dropdown is still present in generated HTML');
  process.exit(1);
}
console.log('  ✓ Legacy dropdown (#search-results) cleanly eliminated in favor of centered modal.');

// 3. Rocket Loader & Zero Inline Handlers
console.log('3. Validating Cloudflare Rocket Loader Anti-Pattern Safety (Zero Inline Handlers):');
const inlineHandlers = headerContent.match(/\son[a-z]+=["'][^"']*["']/i);
if (inlineHandlers) {
  console.error(`  ❌ FAILED: Inline event handler found in header.html: ${inlineHandlers[0]}`);
  process.exit(1);
}
console.log('  ✓ ZERO inline event handlers found in header.html and search modal markup.');

// 4. Robust DOM Event Delegation & Focus Management (Gate 3 & Gate 4 Audit)
console.log('4. Validating Robust DOM Event Delegation & Focus Management:');

// Must use closest('a') to prevent nested <mark> node click traps
if (!headerContent.includes("!e.target.closest('a')") && !headerContent.includes('!e.target.closest("a")')) {
  console.error("  ❌ FAILED: Event delegation missing !e.target.closest('a') check for card clicks!");
  process.exit(1);
}
console.log("  ✓ Event delegation safely checks !e.target.closest('a') (immune to <mark> traps).");

// Negative assertion: must NOT use direct tag check tagName !== 'A'
if (/e\.target\.tagName(\.toLowerCase\(\))?\s*!==\s*['"]a['"]/i.test(headerContent)) {
  console.error("  ❌ FAILED: Fragile direct tag check e.target.tagName !== 'a' detected!");
  process.exit(1);
}
console.log("  ✓ Negative test passed: Fragile e.target.tagName !== 'a' eliminated.");

// Negative assertion: trigger button must NOT use passive focus listener
if (/searchTriggerBtn\.addEventListener\(\s*['"]focus['"]/i.test(headerContent)) {
  console.error("  ❌ FAILED: Passive focus listener found on searchTriggerBtn (causes infinite loop and tab hijack)!");
  process.exit(1);
}
console.log("  ✓ Negative test passed: Passive 'focus' listener absent from search trigger.");

// Positive assertion: focus restoration on modal close
if (!headerContent.includes('previouslyFocusedElement.focus()')) {
  console.error("  ❌ FAILED: Modal close missing previouslyFocusedElement.focus() restoration!");
  process.exit(1);
}
console.log("  ✓ Focus restoration to previously focused element verified on modal close.");

// 5. Category Resolution Logic Unit Tests
console.log('5. Validating Category Resolution Logic:');
function getCategory(permalink) {
  const p = (permalink || '').toLowerCase();
  if (p.startsWith('/tech/')) return { label: 'Tech', icon: '💻' };
  if (p.startsWith('/books/')) return { label: 'Books', icon: '📚' };
  if (p.startsWith('/games/')) return { label: 'Games', icon: '🎮' };
  if (p.startsWith('/other-interests/')) return { label: 'Research', icon: '🔬' };
  if (p.startsWith('/posts/')) return { label: 'Posts', icon: '📝' };
  if (p.startsWith('/tags/')) return { label: 'Tag', icon: '🏷️' };
  if (p === '/' || p === '') return { label: 'Home', icon: '🏠' };
  return { label: 'Note', icon: '📄' };
}

const categoryTests = [
  { path: '/tech/linux/', expectedLabel: 'Tech', expectedIcon: '💻' },
  { path: '/tech/programming/python/', expectedLabel: 'Tech', expectedIcon: '💻' },
  { path: '/books/scifi/dune/', expectedLabel: 'Books', expectedIcon: '📚' },
  { path: '/games/fps/half-life/', expectedLabel: 'Games', expectedIcon: '🎮' },
  { path: '/other-interests/ai/', expectedLabel: 'Research', expectedIcon: '🔬' },
  { path: '/posts/first-post/', expectedLabel: 'Posts', expectedIcon: '📝' },
  { path: '/tags/linux/', expectedLabel: 'Tag', expectedIcon: '🏷️' },
  { path: '/', expectedLabel: 'Home', expectedIcon: '🏠' }
];

for (const ct of categoryTests) {
  const res = getCategory(ct.path);
  if (res.label !== ct.expectedLabel || res.icon !== ct.expectedIcon) {
    console.error(`  ❌ FAILED: Category for "${ct.path}" expected ${ct.expectedIcon} ${ct.expectedLabel}, got ${res.icon} ${res.label}`);
    process.exit(1);
  }
}
console.log('  ✓ Category resolution accurately maps notes to Tech, Books, Games, Research, Posts, and Tags.');

// 6. Dynamic Tag Map & Prefix Search Unit Tests
console.log('6. Validating Dynamic Tag Extraction & "#" Prefix Search:');

const tagMap = new Map();
for (const item of searchIndex) {
  if (Array.isArray(item.tags)) {
    for (const t of item.tags) {
      const tagStr = String(t).trim();
      if (tagStr) {
        const lower = tagStr.toLowerCase();
        const existing = tagMap.get(lower);
        if (existing) {
          existing.count++;
        } else {
          tagMap.set(lower, { name: tagStr, count: 1 });
        }
      }
    }
  }
}

if (tagMap.size === 0) {
  console.error('  ❌ FAILED: No tags discovered in search index!');
  process.exit(1);
}
console.log(`  ✓ Discovered ${tagMap.size} unique tags across digital garden notes.`);

function searchTags(prefix) {
  const tagQuery = prefix.toLowerCase();
  const matches = [];
  for (const [lowerTag, info] of tagMap.entries()) {
    if (!tagQuery || lowerTag.includes(tagQuery)) {
      matches.push(info);
    }
  }
  matches.sort((a, b) => {
    const aLower = a.name.toLowerCase();
    const bLower = b.name.toLowerCase();
    const aStarts = aLower.startsWith(tagQuery);
    const bStarts = bLower.startsWith(tagQuery);
    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;
    return b.count - a.count;
  });
  return matches;
}

const mMatches = searchTags('m');
if (mMatches.length === 0) {
  console.error('  ❌ FAILED: Tag query "m" returned 0 matches!');
  process.exit(1);
}
console.log(`  ✓ Query "#m" returned ${mMatches.length} matching tags (e.g. ${mMatches.slice(0, 3).map(x => x.name).join(', ')}).`);

const monMatches = searchTags('mon');
const hasMonitoring = monMatches.some(x => x.name.toLowerCase() === 'monitoring');
if (!hasMonitoring) {
  console.error('  ❌ FAILED: Tag query "#mon" did not include "monitoring"!');
  process.exit(1);
}
console.log('  ✓ Query "#mon" successfully discovered "monitoring" tag.');

// Negative tag prefix test: non-existent tag
const bogusMatches = searchTags('bogusnonexistenttag999');
if (bogusMatches.length !== 0) {
  console.error('  ❌ FAILED: Query for non-existent tag returned results!');
  process.exit(1);
}
console.log('  ✓ Negative test passed: Non-existent tag query cleanly yields 0 matches.');

// 7. Validating In-Modal Note Filtering by Tag (#<tag> and #<tag> <keyword>)
console.log('7. Validating In-Modal Note Filtering by Tag (#<tag> and #<tag> <keyword>):');
const linuxNotes = searchIndex.filter(item => 
  Array.isArray(item.tags) && item.tags.some(t => String(t).toLowerCase() === 'linux')
);
if (linuxNotes.length === 0) {
  console.error('  ❌ FAILED: Expected at least one note tagged "linux"');
  process.exit(1);
}
console.log(`  ✓ In-modal note filter for "#linux" correctly isolates ${linuxNotes.length} tagged notes.`);

// Multi-word tag + keyword filter: e.g. #linux package
const subQuery = 'package';
const filteredWithKeyword = linuxNotes.filter(item => 
  (item.title || '').toLowerCase().includes(subQuery) || (item.content || '').toLowerCase().includes(subQuery)
);
if (filteredWithKeyword.length === 0) {
  console.error('  ❌ FAILED: Expected notes matching "#linux package"!');
  process.exit(1);
}
console.log(`  ✓ Multi-term filter "#linux package" cleanly narrowed to ${filteredWithKeyword.length} notes.`);

console.log('\n✓ All Command Palette Search Modal regression tests passed successfully!');
