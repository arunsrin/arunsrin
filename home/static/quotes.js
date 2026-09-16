const QUOTE_STORAGE_KEY = 'quotes';
const EXPIRY_STORAGE_KEY = 'quotes_expiry';
const EXPIRY_TIME = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

let loadedQuotes = null;
let currentQuoteIndex = -1;

function displayRandomQuote(quotes) {
    if (!Array.isArray(quotes) || quotes.length === 0) return;
    let newIndex = Math.floor(Math.random() * quotes.length);
    if (quotes.length > 1 && newIndex === currentQuoteIndex) {
        newIndex = (newIndex + 1) % quotes.length;
    }
    currentQuoteIndex = newIndex;
    const randomQuote = quotes[newIndex];
    const quoteEl = document.getElementById('quote');
    const authorEl = document.getElementById('quote-author');
    if (quoteEl) quoteEl.textContent = `"${randomQuote.text}"`;
    if (authorEl) authorEl.textContent = randomQuote.author ? `— ${randomQuote.author}` : '';
}

function fetchQuotes(cb) {
    fetch('/static/quotes.json')
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            if (data && Array.isArray(data.quotes) && data.quotes.length > 0) {
                loadedQuotes = data.quotes;
                try {
                    localStorage.setItem(QUOTE_STORAGE_KEY, JSON.stringify(loadedQuotes));
                    localStorage.setItem(EXPIRY_STORAGE_KEY, String(Date.now() + EXPIRY_TIME));
                } catch (e) {}
                displayRandomQuote(loadedQuotes);
            }
            if (cb) cb();
        })
        .catch(error => {
            console.error('Error loading quotes:', error);
            const quoteEl = document.getElementById('quote');
            if (quoteEl && !quoteEl.textContent) {
                quoteEl.textContent = '"The woods are lovely, dark and deep, but I have promises to keep."';
                const authorEl = document.getElementById('quote-author');
                if (authorEl) authorEl.textContent = '— Robert Frost';
            }
            if (cb) cb();
        });
}

function rerollQuote() {
    const dice = document.querySelector('.dice-icon');
    if (dice) {
        dice.classList.add('dice-spin');
        setTimeout(() => dice.classList.remove('dice-spin'), 600);
    }
    const container = document.getElementById('quote-container');
    if (container) {
        container.style.opacity = '0.5';
    }
    setTimeout(() => {
        if (Array.isArray(loadedQuotes) && loadedQuotes.length > 0) {
            displayRandomQuote(loadedQuotes);
            if (container) container.style.opacity = '1';
        } else {
            const stored = localStorage.getItem(QUOTE_STORAGE_KEY);
            if (stored) {
                try {
                    loadedQuotes = JSON.parse(stored);
                } catch (e) {
                    loadedQuotes = null;
                }
            }
            if (Array.isArray(loadedQuotes) && loadedQuotes.length > 0) {
                displayRandomQuote(loadedQuotes);
                if (container) container.style.opacity = '1';
            } else {
                fetchQuotes(() => {
                    if (container) container.style.opacity = '1';
                });
            }
        }
    }, 150);
}

window.rerollQuote = rerollQuote;

function initQuotes() {
    const btn = document.getElementById('fortune-reroll-btn');
    if (btn) {
        btn.addEventListener('click', rerollQuote);
    }
    const expiry = localStorage.getItem(EXPIRY_STORAGE_KEY);
    const quotes = localStorage.getItem(QUOTE_STORAGE_KEY);

    if (!quotes || !expiry || Date.now() > Number(expiry)) {
        fetchQuotes();
    } else {
        try {
            loadedQuotes = JSON.parse(quotes);
            displayRandomQuote(loadedQuotes);
        } catch (e) {
            fetchQuotes();
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initQuotes);
} else {
    initQuotes();
}
