/**
 * Main Application Controller
 */

class App {
    constructor() {
        this.models = [];
        this.biasPrompts = [];
        this.currentPrompt = '';
        this.currentTemperature = 0.7;
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing LLM Bias Testing Tool...');

        try {
            // Load models and prompts
            await this.loadModels();
            await this.loadBiasPrompts();

            // Setup event listeners
            this.setupEventListeners();

            console.log('Application initialized successfully');
        } catch (error) {
            console.error('Error initializing application:', error);
            UIManager.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    /**
     * Load available models from backend
     */
    async loadModels() {
        try {
            this.models = await ApiClient.fetchModels();
            UIManager.renderModelSelection(this.models);
            console.log(`Loaded ${this.models.length} models`);
        } catch (error) {
            console.error('Error loading models:', error);
            UIManager.showError('Failed to load models. Please check backend connection.');
            throw error;
        }
    }

    /**
     * Load bias test prompts from backend
     */
    async loadBiasPrompts() {
        try {
            this.biasPrompts = await ApiClient.fetchBiasPrompts();
            UIManager.renderBiasPrompts(this.biasPrompts);
            console.log(`Loaded ${this.biasPrompts.length} bias test prompts`);
        } catch (error) {
            console.error('Error loading bias prompts:', error);
            // Don't throw - prompts are optional
        }
    }

    /**
     * Setup event listeners for UI interactions
     */
    setupEventListeners() {
        // Temperature slider
        const temperatureSlider = document.getElementById('temperature-slider');
        temperatureSlider.addEventListener('input', (e) => {
            this.currentTemperature = parseFloat(e.target.value);
            UIManager.updateTemperatureDisplay(this.currentTemperature);
        });

        // Bias prompt buttons
        const biasPromptsContainer = document.getElementById('bias-prompts');
        biasPromptsContainer.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON' && e.target.dataset.promptText) {
                this.loadBiasPrompt(e.target.dataset.promptText);
            }
        });

        // Submit button
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.addEventListener('click', () => {
            this.handleSubmit();
        });

        // Export buttons
        const exportCsvBtn = document.getElementById('export-csv-btn');
        exportCsvBtn.addEventListener('click', () => {
            ComparisonView.exportAsCSV();
        });

        const exportJsonBtn = document.getElementById('export-json-btn');
        exportJsonBtn.addEventListener('click', () => {
            ComparisonView.exportAsJSON();
        });

        // Prompt input (allow Enter key to submit)
        const promptInput = document.getElementById('prompt-input');
        promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.handleSubmit();
            }
        });
    }

    /**
     * Load a bias prompt into the input field
     * @param {string} promptText - The prompt text to load
     */
    loadBiasPrompt(promptText) {
        const promptInput = document.getElementById('prompt-input');
        promptInput.value = promptText;
        this.currentPrompt = promptText;

        // Scroll to prompt input
        promptInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        promptInput.focus();
    }

    /**
     * Handle form submission
     */
    async handleSubmit() {
        // Get prompt
        const promptInput = document.getElementById('prompt-input');
        const prompt = promptInput.value.trim();

        if (!prompt) {
            UIManager.showError('Please enter a prompt');
            return;
        }

        // Get selected models
        const selectedModels = UIManager.getSelectedModels();

        if (selectedModels.length === 0) {
            UIManager.showError('Please select at least one model');
            return;
        }

        // Show loading state
        UIManager.showLoading();

        try {
            // Submit query to backend
            console.log(`Querying ${selectedModels.length} models with prompt: "${prompt}"`);
            const results = await ApiClient.submitQuery(prompt, selectedModels, this.currentTemperature);

            // Hide loading and show results
            UIManager.hideLoading();
            ComparisonView.render(results);

            console.log('Query completed successfully');
        } catch (error) {
            console.error('Error submitting query:', error);
            UIManager.hideLoading();
            UIManager.showError(error.message || 'Failed to query models. Please try again.');
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});
