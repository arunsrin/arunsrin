const QUOTE_STORAGE_KEY = 'quotes';
const EXPIRY_STORAGE_KEY = 'quotes_expiry';
const EXPIRY_TIME = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

let loadedQuotes = null;

function fetchQuotes() {
    const base = document.querySelector('base')?.getAttribute('href') || '/';
    fetch(`${base}static/quotes.json`)
        .then(response => response.json())
        .then(data => {
            loadedQuotes = data.quotes;
            localStorage.setItem(QUOTE_STORAGE_KEY, JSON.stringify(loadedQuotes));
            localStorage.setItem(EXPIRY_STORAGE_KEY, Date.now() + EXPIRY_TIME);
            displayRandomQuote(loadedQuotes);
        })
        .catch(error => {
            console.error('Error loading quotes:', error);
            const quoteEl = document.getElementById('quote');
            if (quoteEl) quoteEl.textContent = 'Error loading quotes. Please try again later.';
        });
}

function displayRandomQuote(quotes) {
    if (!quotes || !quotes.length) return;
    const randomIndex = Math.floor(Math.random() * quotes.length);
    const randomQuote = quotes[randomIndex];
    const quoteEl = document.getElementById('quote');
    const authorEl = document.getElementById('quote-author');
    if (quoteEl) quoteEl.textContent = `"${randomQuote.text}"`;
    if (authorEl) authorEl.textContent = `— ${randomQuote.author}`;
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
        setTimeout(() => {
            if (loadedQuotes && loadedQuotes.length) {
                displayRandomQuote(loadedQuotes);
            } else {
                const stored = localStorage.getItem(QUOTE_STORAGE_KEY);
                if (stored) {
                    loadedQuotes = JSON.parse(stored);
                    displayRandomQuote(loadedQuotes);
                } else {
                    fetchQuotes();
                }
            }
            container.style.opacity = '1';
        }, 150);
    }
}

window.rerollQuote = rerollQuote;

function loadQuotes() {
    const expiry = localStorage.getItem(EXPIRY_STORAGE_KEY);
    const quotes = localStorage.getItem(QUOTE_STORAGE_KEY);

    if (!quotes || !expiry || Date.now() > expiry) {
        fetchQuotes();
    } else {
        loadedQuotes = JSON.parse(quotes);
        displayRandomQuote(loadedQuotes);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadQuotes);
} else {
    loadQuotes();
}
