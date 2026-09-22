#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

let passedTests = 0;
let totalTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passedTests++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    Error: ${err.message}`);
    process.exitCode = 1;
  }
}

async function runAsyncTest(name, fn) {
  totalTests++;
  try {
    await fn();
    console.log(`  ✓ ${name}`);
    passedTests++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    Error: ${err.message}`);
    process.exitCode = 1;
  }
}

console.log('--- JavaScript & Template Safety Tests ---');

// 1. Static JS File Syntax Validation
console.log('\n1. Validating Standalone JavaScript Files:');
const jsFiles = [
  'home/static/quotes.js',
  'home/static/iconify-icon.min.js'
];

jsFiles.forEach(relPath => {
  runTest(`Syntax check: ${relPath}`, () => {
    const fullPath = path.resolve(relPath);
    assert(fs.existsSync(fullPath), `File does not exist: ${relPath}`);
    const code = fs.readFileSync(fullPath, 'utf8');
    assert(code.trim().length > 0, `File is empty: ${relPath}`);
    new vm.Script(code, { filename: relPath });
  });
});

// 2. Inline Scripts in Generated HTML Validation
console.log('\n2. Validating Inline Scripts in Generated Pages:');
runTest('Syntax check all inline scripts in public/index.html', () => {
  const indexPath = path.resolve('public/index.html');
  assert(fs.existsSync(indexPath), 'public/index.html does not exist. Run hugo first.');
  const html = fs.readFileSync(indexPath, 'utf8');
  const scriptRegex = /<script(?:\s+[^>]*)?>([\s\S]*?)<\/script>/gi;
  let match, count = 0;
  while ((match = scriptRegex.exec(html)) !== null) {
    const scriptCode = match[1].trim();
    if (scriptCode.length > 0) {
      new vm.Script(scriptCode, { filename: `index.html:script[${count}]` });
      count++;
    }
  }
  assert(count > 0, 'Expected at least one inline script in public/index.html');
});

// 3. Cloudflare Rocket Loader & Inline Handler Anti-Pattern Linter
console.log('\n3. Cloudflare Rocket Loader Anti-Pattern Check:');
runTest('Verify ZERO inline event handlers (onclick, onload, etc.) across all generated HTML', () => {
  function walkDir(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach(file => {
      const full = path.join(dir, file);
      const stat = fs.statSync(full);
      if (stat && stat.isDirectory()) {
        results = results.concat(walkDir(full));
      } else if (file.endsWith('.html')) {
        results.push(full);
      }
    });
    return results;
  }

  const htmlFiles = walkDir(path.resolve('public'));
  const inlineHandlerRegex = /\s(on[a-z]+)\s*=\s*["'][^"']*["']/gi;
  const violations = [];

  htmlFiles.forEach(filePath => {
    const content = fs.readFileSync(filePath, 'utf8');
    let match;
    while ((match = inlineHandlerRegex.exec(content)) !== null) {
      violations.push({
        file: path.relative(process.cwd(), filePath),
        handler: match[1]
      });
    }
  });

  if (violations.length > 0) {
    const sample = violations.slice(0, 5).map(v => `${v.file}: ${v.handler}`).join(', ');
    throw new Error(`Found ${violations.length} inline event handlers! Cloudflare Rocket Loader will intercept these: ${sample}`);
  }
});

// 4. Cloudflare _headers Caching Safety
console.log('\n4. Cloudflare _headers Cache Safety Check:');
runTest('Verify static_root/_headers does NOT use immutable on unhashed /css/* or wildcard /static/*', () => {
  const headersPath = path.resolve('static_root/_headers');
  assert(fs.existsSync(headersPath), 'static_root/_headers does not exist');
  const headers = fs.readFileSync(headersPath, 'utf8');
  
  const cssMatch = headers.match(/\/css\/\*\s+Cache-Control:[^\n]+/i);
  assert(cssMatch, 'Expected /css/* Cache-Control rule in static_root/_headers');
  if (cssMatch[0].includes('immutable')) {
    throw new Error('Forbidden "immutable" directive found for /css/* in static_root/_headers. Unhashed CSS files must use stale-while-revalidate.');
  }

  // Ensure /css/* has at least 48h (172800s) max-age for performance and YSlow/Pingdom compliance
  const cssMaxAgeMatch = cssMatch[0].match(/max-age=(\d+)/i);
  assert(cssMaxAgeMatch, 'Expected max-age in /css/* Cache-Control');
  const cssMaxAge = parseInt(cssMaxAgeMatch[1], 10);
  assert(cssMaxAge >= 172800, `Expected /css/* max-age >= 172800 (48 hours), got ${cssMaxAge}`);

  // Ensure /static/* wildcard does not collide with quotes.json / quotes.js by adding immutable to all static files
  const staticWildcardMatch = headers.match(/\/static\/\*\s+Cache-Control:[^\n]+/i);
  if (staticWildcardMatch && staticWildcardMatch[0].includes('immutable')) {
    throw new Error('Forbidden wildcard "/static/*" with immutable found. Explicitly name immutable assets to avoid colliding with quotes.json.');
  }

  const quotesJsonMatch = headers.match(/\/static\/quotes\.json\s+Cache-Control:[^\n]+/i);
  assert(quotesJsonMatch, 'Expected explicit Cache-Control for /static/quotes.json');
  assert(!quotesJsonMatch[0].includes('immutable'), 'quotes.json must not be immutable');

  const quotesJsMatch = headers.match(/\/static\/quotes\.js\s+Cache-Control:[^\n]+/i);
  assert(quotesJsMatch, 'Expected explicit Cache-Control for /static/quotes.js');
  assert(!quotesJsMatch[0].includes('immutable'), 'quotes.js must not be immutable');
});

// 5. Unclosed HTML Tag Checker in Content Markdown
console.log('\n5. Content Markdown HTML Structure Check:');
runTest('Verify opening <div class="grid cards" tags match closing </div> tags', () => {
  function walkDir(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach(file => {
      const full = path.join(dir, file);
      const stat = fs.statSync(full);
      if (stat && stat.isDirectory()) {
        results = results.concat(walkDir(full));
      } else if (file.endsWith('.md')) {
        results.push(full);
      }
    });
    return results;
  }

  const mdFiles = walkDir(path.resolve('home'));
  mdFiles.forEach(filePath => {
    const content = fs.readFileSync(filePath, 'utf8');
    const openDivs = (content.match(/<div\b[^>]*>/gi) || []).length;
    const closeDivs = (content.match(/<\/div>/gi) || []).length;
    assert.strictEqual(
      openDivs,
      closeDivs,
      `Unbalanced <div> tags in ${path.relative(process.cwd(), filePath)}: ${openDivs} open vs ${closeDivs} close`
    );
  });
});

// 6. Unit Tests for Fortune Quotes Client Logic (quotes.js)
console.log('\n6. Fortune Quotes Logic Unit Tests:');
(async () => {
  await runAsyncTest('quotes.js correctly displays quote and formats empty author', async () => {
    const code = fs.readFileSync('home/static/quotes.js', 'utf8');
    
    // Create mock DOM & Browser environment
    let elements = {
      'quote': { textContent: '' },
      'quote-author': { textContent: '' },
      'fortune-reroll-btn': { addEventListener: () => {} },
      'quote-container': { style: { opacity: '1' } }
    };
    
    let storage = {};
    const mockLocalStorage = {
      getItem: (k) => storage[k] || null,
      setItem: (k, v) => { storage[k] = String(v); }
    };

    const mockFetch = async () => ({
      ok: true,
      json: async () => ({
        quotes: [
          { text: 'Quote 1', author: 'Author 1' },
          { text: 'Quote 2', author: '' }
        ]
      })
    });

    const sandbox = {
      document: {
        getElementById: (id) => elements[id] || null,
        querySelector: () => null,
        addEventListener: () => {},
        readyState: 'complete'
      },
      localStorage: mockLocalStorage,
      fetch: mockFetch,
      Date: Date,
      Math: Math,
      setTimeout: (fn) => fn(),
      console: console,
      Array: Array,
      String: String,
      Number: Number,
      JSON: JSON,
      window: {}
    };

    vm.createContext(sandbox);
    vm.runInContext(code, sandbox);

    // Initial load should display a quote
    await new Promise(r => setImmediate(r));
    assert(elements['quote'].textContent.length > 0, 'Expected quote element to have text');
    
    // Call displayRandomQuote with a quote having empty author
    sandbox.displayRandomQuote([{ text: 'Solo Thought', author: '' }]);
    assert.strictEqual(elements['quote'].textContent, '"Solo Thought"');
    assert.strictEqual(elements['quote-author'].textContent, '', 'Empty author must not render a trailing dash');

    // Call displayRandomQuote with a regular quote
    sandbox.displayRandomQuote([{ text: 'Wise Words', author: 'Seneca' }]);
    assert.strictEqual(elements['quote'].textContent, '"Wise Words"');
    assert.strictEqual(elements['quote-author'].textContent, '— Seneca');
  });

  await runAsyncTest('rerollQuote avoids consecutive identical quotes when multiple exist', async () => {
    const code = fs.readFileSync('home/static/quotes.js', 'utf8');
    let elements = {
      'quote': { textContent: '' },
      'quote-author': { textContent: '' },
      'fortune-reroll-btn': { addEventListener: () => {} },
      'quote-container': { style: { opacity: '1' } }
    };
    
    let sampleQuotes = [
      { text: 'Quote A', author: 'A' },
      { text: 'Quote B', author: 'B' }
    ];

    const sandbox = {
      document: {
        getElementById: (id) => elements[id] || null,
        querySelector: () => null,
        addEventListener: () => {},
        readyState: 'complete'
      },
      localStorage: {
        getItem: (k) => (k === 'quotes' ? JSON.stringify(sampleQuotes) : String(Date.now() + 100000)),
        setItem: () => {}
      },
      fetch: async () => {},
      Date: Date,
      Math: Math,
      setTimeout: (fn) => fn(),
      console: console,
      Array: Array,
      String: String,
      Number: Number,
      JSON: JSON,
      window: {}
    };

    vm.createContext(sandbox);
    vm.runInContext(code, sandbox);

    const firstQuote = elements['quote'].textContent;
    sandbox.rerollQuote();
    const secondQuote = elements['quote'].textContent;

    assert.notStrictEqual(
      firstQuote,
      secondQuote,
      `Expected reroll to cycle to different quote (got "${firstQuote}" -> "${secondQuote}")`
    );
  });

  await runAsyncTest('quotes.js handles corrupted JSON in localStorage gracefully', async () => {
    const code = fs.readFileSync('home/static/quotes.js', 'utf8');
    let elements = {
      'quote': { textContent: '' },
      'quote-author': { textContent: '' },
      'fortune-reroll-btn': { addEventListener: () => {} },
      'quote-container': { style: { opacity: '1' } }
    };
    
    let fetchCalled = false;
    const sandbox = {
      document: {
        getElementById: (id) => elements[id] || null,
        querySelector: () => null,
        addEventListener: () => {},
        readyState: 'complete'
      },
      localStorage: {
        getItem: (k) => (k === 'quotes' ? 'INVALID_JSON{{{' : String(Date.now() + 100000)),
        setItem: () => {}
      },
      fetch: async () => {
        fetchCalled = true;
        return {
          ok: true,
          json: async () => ({ quotes: [{ text: 'Fresh', author: 'Fetched' }] })
        };
      },
      Date: Date,
      Math: Math,
      setTimeout: (fn) => fn(),
      console: console,
      Array: Array,
      String: String,
      Number: Number,
      JSON: JSON,
      window: {}
    };

    vm.createContext(sandbox);
    // Should NOT throw an exception when running with invalid JSON in localStorage
    vm.runInContext(code, sandbox);
    assert(fetchCalled, 'Expected corrupted localStorage to trigger fallback fetch');
  });

  console.log(`\nResults: ${passedTests}/${totalTests} tests passed.`);
  if (passedTests !== totalTests) {
    process.exit(1);
  }
})();
