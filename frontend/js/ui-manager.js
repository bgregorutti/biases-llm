/**
 * UI Manager for handling DOM manipulation and UI updates
 */

const UIManager = {
    /**
     * Render model selection checkboxes
     * @param {Array} models - List of model configurations
     */
    renderModelSelection(models) {
        const container = document.getElementById('model-selection');
        container.innerHTML = '';

        if (!models || models.length === 0) {
            container.innerHTML = '<div class="text-gray-500 italic">No models available</div>';
            return;
        }

        models.forEach(model => {
            const checkbox = document.createElement('div');
            checkbox.className = 'flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition';

            const isDisabled = !model.available;
            const disabledClass = isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

            checkbox.innerHTML = `
                <input
                    type="checkbox"
                    id="model-${model.id}"
                    value="${model.id}"
                    class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                    ${isDisabled ? 'disabled' : ''}
                >
                <label for="model-${model.id}" class="ml-2 text-sm font-medium text-gray-900 ${disabledClass} flex-1">
                    ${model.name}
                    ${isDisabled ? '<span class="text-xs text-red-500 ml-2">(Unavailable)</span>' : ''}
                </label>
            `;

            container.appendChild(checkbox);
        });
    },

    /**
     * Render bias prompt quick-select buttons
     * @param {Array} prompts - List of bias test prompts
     */
    renderBiasPrompts(prompts) {
        const container = document.getElementById('bias-prompts');
        container.innerHTML = '';

        if (!prompts || prompts.length === 0) {
            container.innerHTML = '<div class="text-gray-500 italic">No test prompts available</div>';
            return;
        }

        // Group prompts by category
        const categories = {};
        prompts.forEach(prompt => {
            if (!categories[prompt.category]) {
                categories[prompt.category] = [];
            }
            categories[prompt.category].push(prompt);
        });

        // Create buttons grouped by category
        Object.entries(categories).forEach(([category, categoryPrompts]) => {
            // Category label
            const categoryLabel = document.createElement('div');
            categoryLabel.className = 'w-full mt-2 mb-1';
            categoryLabel.innerHTML = `
                <span class="text-xs font-semibold text-gray-600 uppercase">${category.replace('_', ' ')}</span>
            `;
            container.appendChild(categoryLabel);

            // Prompt buttons
            categoryPrompts.forEach(prompt => {
                const button = document.createElement('button');
                button.className = 'px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition border border-blue-200';
                button.textContent = prompt.title;
                button.title = prompt.description;
                button.dataset.promptId = prompt.id;
                button.dataset.promptText = prompt.prompt;

                container.appendChild(button);
            });
        });
    },

    /**
     * Get selected model IDs
     * @returns {Array<string>} Array of selected model IDs
     */
    getSelectedModels() {
        const checkboxes = document.querySelectorAll('#model-selection input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    },

    /**
     * Show loading state
     */
    showLoading() {
        document.getElementById('loading-indicator').classList.remove('hidden');
        document.getElementById('results-container').classList.add('hidden');
        document.getElementById('error-display').classList.add('hidden');
        document.getElementById('submit-btn').disabled = true;
    },

    /**
     * Hide loading state
     */
    hideLoading() {
        document.getElementById('loading-indicator').classList.add('hidden');
        document.getElementById('submit-btn').disabled = false;
    },

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    showError(message) {
        const errorDisplay = document.getElementById('error-display');
        const errorMessage = document.getElementById('error-message');

        errorMessage.textContent = message;
        errorDisplay.classList.remove('hidden');

        // Hide after 5 seconds
        setTimeout(() => {
            errorDisplay.classList.add('hidden');
        }, 5000);
    },

    /**
     * Show results container
     */
    showResults() {
        document.getElementById('results-container').classList.remove('hidden');
    },

    /**
     * Scroll to results
     */
    scrollToResults() {
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    /**
     * Update temperature display value
     * @param {number} value - Temperature value
     */
    updateTemperatureDisplay(value) {
        document.getElementById('temperature-value').textContent = value;
    }
};
