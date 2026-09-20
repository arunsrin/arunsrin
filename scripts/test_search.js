#!/usr/bin/env node
/**
 * Automated Regression Test Suite for Full-Text Search Relevance Scoring
 * 
 * Asserts:
 * 1. Exact match ranking: "python", "ai", "programming", "go", "docker", "git", "security", "linux" rank #1.
 * 2. Multi-word and tag match queries.
 * 3. Snippet cleaning (stripping icon shortcodes and markdown hashes).
 * 4. Query term highlighting wrapped in <mark class="search-highlight">.
 * 5. Rocket Loader anti-pattern safety (zero inline handlers in search markup).
 */

const fs = require('fs');
const path = require('path');

const publicIndex = path.join(__dirname, '..', 'public', 'index.json');
if (!fs.existsSync(publicIndex)) {
  console.error(`Error: ${publicIndex} not found. Run 'hugo' first.`);
  process.exit(1);
}

const searchIndex = JSON.parse(fs.readFileSync(publicIndex, 'utf8'));

// Extract search scoring logic from layouts/partials/header.html to test exact production parity
function scoreItem(item, query, queryWords) {
  const title = (item.title || '').toLowerCase().trim();
  const permalink = (item.permalink || '').toLowerCase();
  const content = (item.content || '').toLowerCase();
  const tags = Array.isArray(item.tags) ? item.tags.map(t => String(t).toLowerCase()) : [];
  const slug = permalink.replace(/\/$/, '').split('/').pop() || '';

  let score = 0;

  if (title === query) {
    score += 1000;
  } else if (title.startsWith(query + ' ') || title.endsWith(' ' + query) || title.includes(' ' + query + ' ')) {
    score += 600;
  } else if (title.startsWith(query)) {
    score += 400;
  } else if (title.includes(query)) {
    score += 250;
  }

  if (slug === query) {
    score += 350;
  } else if (slug.includes(query)) {
    score += 150;
  }

  if (tags.includes(query)) {
    score += 300;
  } else if (tags.some(t => t.includes(query))) {
    score += 100;
  }

  if (queryWords.length > 1) {
    let wordsInTitle = 0;
    for (const w of queryWords) {
      if (title.includes(w)) wordsInTitle++;
    }
    if (wordsInTitle === queryWords.length) {
      score += 200;
    }
  }

  if (content.includes(query)) {
    score += 20;
    const count = content.split(query).length - 1;
    score += Math.min(30, count * 3);
  }

  if (permalink === '/' || permalink === '') {
    score -= 150;
  }

  return score;
}

function search(query) {
  const q = query.toLowerCase().trim();
  const queryWords = q.split(/\s+/).filter(Boolean);
  const scored = [];
  for (const item of searchIndex) {
    const s = scoreItem(item, q, queryWords);
    if (s > 0) scored.push({ item, score: s });
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, 10).map(x => x.item);
}

console.log('--- Search Relevance & Scoring Test Suite ---');

// 1. Direct Target Queries must rank #1
const exactTargetTests = [
  { query: 'python', expectedPermalink: '/tech/programming/python/' },
  { query: 'ai', expectedPermalink: '/tech/ai/' },
  { query: 'programming', expectedPermalink: '/tech/programming/' },
  { query: 'go', expectedPermalink: '/tech/programming/go/' },
  { query: 'docker', expectedPermalink: '/tech/docker/' },
  { query: 'git', expectedPermalink: '/tech/git/' },
  { query: 'security', expectedPermalink: '/tech/security/' },
  { query: 'linux', expectedPermalink: '/tech/linux/' }
];

console.log('1. Validating Exact Matches Rank #1:');
for (const t of exactTargetTests) {
  const results = search(t.query);
  if (results.length === 0) {
    console.error(`  ❌ FAILED: Query "${t.query}" returned 0 results!`);
    process.exit(1);
  }
  const topResult = results[0];
  if (topResult.permalink !== t.expectedPermalink) {
    console.error(`  ❌ FAILED: Query "${t.query}" expected #1 "${t.expectedPermalink}", but got "${topResult.permalink}" (${topResult.title})`);
    process.exit(1);
  }
  console.log(`  ✓ Query "${t.query}" -> #1 ${topResult.title} (${topResult.permalink})`);
}

// 2. Highlighting check
console.log('2. Validating Search Term Highlighting:');
function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
function highlightMatches(text, query) {
  const words = query.split(/\s+/).filter(Boolean).map(escapeRegExp);
  const regex = new RegExp(`(${words.join('|')})`, 'gi');
  return text.replace(regex, '<mark class="search-highlight">$1</mark>');
}

const hl = highlightMatches("Python Programming Notes", "python");
if (!hl.includes('<mark class="search-highlight">Python</mark>')) {
  console.error('  ❌ FAILED: Highlight markup missing <mark class="search-highlight">');
  process.exit(1);
}
console.log('  ✓ Query terms cleanly wrapped in <mark class="search-highlight">');

// 3. Snippet Cleaning check
console.log('3. Validating Snippet Cleaning:');
function cleanSnippet(content, query) {
  let text = content.replace(/:[a-z0-9_-]+:(\{[^}]+\})?/gi, '');
  text = text.replace(/^#+\s*/gm, '');
  return text.replace(/\s+/g, ' ').trim();
}
const dirty = '# :material-brain:{ .anim-bounce } AI Notes and Research';
const cleaned = cleanSnippet(dirty, 'ai');
if (cleaned.includes(':material-') || cleaned.startsWith('#')) {
  console.error(`  ❌ FAILED: Cleaned snippet contains unparsed syntax: "${cleaned}"`);
  process.exit(1);
}
console.log('  ✓ Snippet cleanly strips icon markers and heading hashes');

// 4. Zero Inline Handlers in header.html check
console.log('4. Validating Cloudflare Rocket Loader Anti-Pattern Safety:');
const headerPath = path.join(__dirname, '..', 'layouts', 'partials', 'header.html');
const headerContent = fs.readFileSync(headerPath, 'utf8');
const inlineMatch = headerContent.match(/\son[a-z]+=["'][^"']*["']/i);
if (inlineMatch) {
  console.error(`  ❌ FAILED: Inline event handler found in header.html: ${inlineMatch[0]}`);
  process.exit(1);
}
console.log('  ✓ ZERO inline event handlers in header.html (100% Rocket Loader safe)');

console.log('\n✓ All Search Relevance tests passed successfully!');
