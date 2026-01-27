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

            // Detect and highlight potential bias indicators
            const highlightedText = this.highlightBiasIndicators(response.response);

            content.innerHTML = `
                <p class="text-sm text-gray-800 whitespace-pre-wrap">${highlightedText}</p>
            `;
        }

        card.appendChild(content);

        return card;
    },

    /**
     * Highlight potential bias indicators in text
     * @param {string} text - Response text
     * @returns {string} HTML with highlighted indicators
     */
    highlightBiasIndicators(text) {
        if (!text) return '';

        // Escape HTML
        let escapedText = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');

        // Highlight gendered pronouns
        const genderPronouns = ['he', 'him', 'his', 'she', 'her', 'hers', 'He', 'Him', 'His', 'She', 'Her', 'Hers'];
        genderPronouns.forEach(pronoun => {
            const regex = new RegExp(`\\b${pronoun}\\b`, 'g');
            escapedText = escapedText.replace(
                regex,
                `<span class="bg-yellow-200 px-1 rounded" title="Gendered pronoun">${pronoun}</span>`
            );
        });

        // Highlight gender-specific words
        const genderWords = ['man', 'woman', 'male', 'female', 'boy', 'girl', 'Man', 'Woman', 'Male', 'Female', 'Boy', 'Girl'];
        genderWords.forEach(word => {
            const regex = new RegExp(`\\b${word}\\b`, 'g');
            escapedText = escapedText.replace(
                regex,
                `<span class="bg-pink-200 px-1 rounded" title="Gender-specific term">${word}</span>`
            );
        });

        return escapedText;
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
