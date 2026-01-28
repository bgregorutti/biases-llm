/**
 * Comparison View Renderer for displaying side-by-side results
 */

const ComparisonView = {
    currentResults: null,

    /**
     * Render comparison results
     * @param {Object} data - Comparison response from API
     */
    render(data) {
        this.currentResults = data;

        // Update prompt display
        document.getElementById('result-prompt').textContent = data.prompt;

        // Render response cards
        const grid = document.getElementById('responses-grid');
        grid.innerHTML = '';

        data.responses.forEach(response => {
            const card = this.createResponseCard(response);
            grid.appendChild(card);
        });

        // Show results container
        UIManager.showResults();
        UIManager.scrollToResults();
    },

    /**
     * Create a response card for a single model
     * @param {Object} response - Model response object
     * @returns {HTMLElement} Card element
     */
    createResponseCard(response) {
        const card = document.createElement('div');
        card.className = 'border rounded-lg p-4 bg-white shadow-sm';

        const hasError = response.error !== null;
        const borderColor = hasError ? 'border-red-300' : 'border-green-300';
        card.classList.add(borderColor);

        // Header with model name and latency
        const header = document.createElement('div');
        header.className = 'flex justify-between items-start mb-3';
        header.innerHTML = `
            <div>
                <h3 class="font-semibold text-gray-800">${response.model_name}</h3>
                <p class="text-xs text-gray-500">${response.model_id}</p>
            </div>
            <div class="text-right">
                <p class="text-sm font-medium ${hasError ? 'text-red-600' : 'text-green-600'}">
                    ${hasError ? 'Failed' : response.latency_ms + ' ms'}
                </p>
            </div>
        `;
        card.appendChild(header);

        // Response content or error
        const content = document.createElement('div');

        if (hasError) {
            content.className = 'bg-red-50 border border-red-200 rounded p-3';
            content.innerHTML = `
                <p class="text-sm text-red-800 font-medium mb-1">Error:</p>
                <p class="text-sm text-red-700">${response.error}</p>
            `;
        } else {
            content.className = 'bg-gray-50 rounded p-3';

            // Parse markdown and sanitize
            const markdownHtml = DOMPurify.sanitize(marked.parse(response.response, { breaks: true }));

            content.innerHTML = `
                <div class="text-sm text-gray-800 prose prose-sm max-w-none">${markdownHtml}</div>
            `;

            // Apply bias highlighting to the rendered HTML
            this.highlightBiasIndicatorsInDOM(content);
        }

        card.appendChild(content);

        return card;
    },

    /**
     * Highlight potential bias indicators in rendered HTML DOM
     * @param {HTMLElement} element - The DOM element containing rendered markdown
     */
    highlightBiasIndicatorsInDOM(element) {
        const genderPronouns = ['he', 'him', 'his', 'she', 'her', 'hers'];
        const genderWords = ['man', 'woman', 'male', 'female', 'boy', 'girl'];

        // Create a combined regex pattern for all bias indicators
        const allWords = [...genderPronouns, ...genderWords];
        const pattern = new RegExp(`\\b(${allWords.join('|')})\\b`, 'gi');

        // Walk through text nodes and highlight matches
        this.highlightTextInNode(element, pattern);
    },

    /**
     * Recursively highlight text in DOM nodes
     * @param {Node} node - DOM node to process
     * @param {RegExp} pattern - Pattern to match
     */
    highlightTextInNode(node, pattern) {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent;
            const matches = text.match(pattern);

            if (matches) {
                const fragment = document.createDocumentFragment();
                let lastIndex = 0;

                // Use matchAll to properly iterate through matches
                const matchIterator = text.matchAll(pattern);
                for (const matchResult of matchIterator) {
                    const match = matchResult[0];
                    const offset = matchResult.index;

                    // Add text before match
                    if (offset > lastIndex) {
                        fragment.appendChild(document.createTextNode(text.substring(lastIndex, offset)));
                    }

                    // Add highlighted match
                    const span = document.createElement('span');
                    const lowerMatch = match.toLowerCase();

                    if (['he', 'him', 'his', 'she', 'her', 'hers'].includes(lowerMatch)) {
                        span.className = 'bg-yellow-200 px-1 rounded';
                        span.title = 'Gendered pronoun';
                    } else {
                        span.className = 'bg-pink-200 px-1 rounded';
                        span.title = 'Gender-specific term';
                    }
                    span.textContent = match;
                    fragment.appendChild(span);

                    lastIndex = offset + match.length;
                }

                // Add remaining text
                if (lastIndex < text.length) {
                    fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
                }

                node.parentNode.replaceChild(fragment, node);
            }
        } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
            // Process child nodes
            Array.from(node.childNodes).forEach(child => {
                this.highlightTextInNode(child, pattern);
            });
        }
    },

    /**
     * Export results as CSV
     */
    exportAsCSV() {
        if (!this.currentResults) {
            alert('No results to export');
            return;
        }

        const rows = [
            ['Prompt', 'Model ID', 'Model Name', 'Response', 'Latency (ms)', 'Error']
        ];

        this.currentResults.responses.forEach(response => {
            rows.push([
                this.currentResults.prompt,
                response.model_id,
                response.model_name,
                response.response || '',
                response.latency_ms,
                response.error || ''
            ]);
        });

        const csvContent = rows.map(row =>
            row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
        ).join('\n');

        this.downloadFile(csvContent, 'bias-test-results.csv', 'text/csv');
    },

    /**
     * Export results as JSON
     */
    exportAsJSON() {
        if (!this.currentResults) {
            alert('No results to export');
            return;
        }

        const jsonContent = JSON.stringify(this.currentResults, null, 2);
        this.downloadFile(jsonContent, 'bias-test-results.json', 'application/json');
    },

    /**
     * Download file to user's computer
     * @param {string} content - File content
     * @param {string} filename - Filename
     * @param {string} mimeType - MIME type
     */
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(url);
    }
};
