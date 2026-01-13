/**
 * SDRF-Proteomics Documentation Search
 * Uses Lunr.js for client-side full-text search
 */

let searchIndex = null;
let searchData = null;

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
});

async function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (!searchInput) return;

    // Load search index - try multiple methods for compatibility
    try {
        // Method 1: Check if SEARCH_INDEX was loaded via script tag
        if (typeof SEARCH_INDEX !== 'undefined') {
            searchData = SEARCH_INDEX;
        } else {
            // Method 2: Try fetch (works on server)
            const basePath = getBasePath();
            const response = await fetch(basePath + 'search-index.json');
            searchData = await response.json();
        }

        // Build Lunr index
        searchIndex = lunr(function() {
            this.ref('id');
            this.field('title', { boost: 10 });
            this.field('content');
            this.field('section', { boost: 5 });
            this.field('keywords', { boost: 8 });

            searchData.forEach((doc, idx) => {
                this.add({
                    id: idx,
                    title: doc.title,
                    content: doc.content,
                    section: doc.section,
                    keywords: doc.keywords
                });
            });
        });

        searchInput.disabled = false;
        searchInput.placeholder = 'Search documentation...';
    } catch (error) {
        console.error('Failed to load search index:', error);
        searchInput.placeholder = 'Search unavailable';
    }

    function getBasePath() {
        // Determine base path for loading resources
        const path = window.location.pathname;
        if (path.includes('/conventions/') || path.includes('/templates/')) {
            return '../';
        }
        return '';
    }

    // Search on input
    let debounceTimer;
    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            performSearch(e.target.value);
        }, 200);
    });

    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeSearch();
        }
    });

    // Close search when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            closeSearch();
        }
    });
}

function performSearch(query) {
    const searchResults = document.getElementById('search-results');

    if (!searchIndex || !query || query.length < 2) {
        searchResults.innerHTML = '';
        searchResults.classList.remove('active');
        return;
    }

    try {
        // Add wildcards for partial matching
        const searchTerms = query.split(' ')
            .filter(term => term.length > 1)
            .map(term => `${term}* ${term}~1`)
            .join(' ');

        const results = searchIndex.search(searchTerms);
        displayResults(results, query);
    } catch (error) {
        // Fallback to simple search if Lunr query fails
        const results = searchIndex.search(query);
        displayResults(results, query);
    }
}

function displayResults(results, query) {
    const searchResults = document.getElementById('search-results');

    if (results.length === 0) {
        searchResults.innerHTML = '<div class="no-results">No results found</div>';
        searchResults.classList.add('active');
        return;
    }

    const html = results.slice(0, 10).map(result => {
        const doc = searchData[result.ref];
        const snippet = getSnippet(doc, query);

        return `
            <a href="${doc.url}" class="search-result-item">
                <div class="result-title">${highlightText(doc.title, query)}</div>
                <div class="result-section">${doc.section}</div>
                <div class="result-snippet">${highlightText(snippet, query)}</div>
            </a>
        `;
    }).join('');

    searchResults.innerHTML = html;
    searchResults.classList.add('active');
}

function getSnippet(doc, query) {
    const words = query.toLowerCase().split(' ').filter(w => w.length > 1);
    const content = doc.content || '';
    const keywords = doc.keywords || '';
    const contentLower = content.toLowerCase();
    const keywordsLower = keywords.toLowerCase();

    // Find the first occurrence of any search term in content
    let bestIndex = -1;
    let matchedWord = '';
    for (const word of words) {
        const index = contentLower.indexOf(word);
        if (index !== -1 && (bestIndex === -1 || index < bestIndex)) {
            bestIndex = index;
            matchedWord = word;
        }
    }

    // If found in content, extract snippet around the match
    if (bestIndex !== -1) {
        const start = Math.max(0, bestIndex - 40);
        const end = Math.min(content.length, bestIndex + 120);
        let snippet = content.slice(start, end);

        if (start > 0) snippet = '...' + snippet;
        if (end < content.length) snippet = snippet + '...';

        return snippet;
    }

    // If not in content, check if it's in keywords and show relevant info
    for (const word of words) {
        if (keywordsLower.includes(word)) {
            // Show beginning of content with note about keyword match
            let snippet = content.slice(0, 120);
            if (content.length > 120) snippet += '...';
            return snippet + ` [Matches keyword: ${word}]`;
        }
    }

    // Fallback: return beginning of content
    return content.slice(0, 150) + '...';
}

function highlightText(text, query) {
    if (!query) return text;

    const words = query.split(' ').filter(w => w.length > 1);
    let result = text;

    words.forEach(word => {
        const regex = new RegExp(`(${escapeRegex(word)})`, 'gi');
        result = result.replace(regex, '<mark>$1</mark>');
    });

    return result;
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function closeSearch() {
    const searchResults = document.getElementById('search-results');
    if (searchResults) {
        searchResults.classList.remove('active');
    }
}

// Keyboard shortcut to focus search (Ctrl/Cmd + K)
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
});
