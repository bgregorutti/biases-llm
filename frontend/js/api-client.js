/**
 * API Client for communicating with the backend
 */

const API_BASE_URL = '/api';

const ApiClient = {
    /**
     * Fetch available models from the backend
     * @returns {Promise<Array>} List of model configurations
     */
    async fetchModels() {
        try {
            const response = await fetch(`${API_BASE_URL}/models`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.models;
        } catch (error) {
            console.error('Error fetching models:', error);
            throw new Error(`Failed to fetch models: ${error.message}`);
        }
    },

    /**
     * Submit a query to multiple models
     * @param {string} prompt - The prompt to send
     * @param {Array<string>} models - Array of model IDs to query
     * @param {number} temperature - Temperature parameter (0.0 to 2.0)
     * @returns {Promise<Object>} Comparison response with all model results
     */
    async submitQuery(prompt, models, temperature = 0.7) {
        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    models: models,
                    temperature: temperature
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error submitting query:', error);
            throw new Error(`Failed to query models: ${error.message}`);
        }
    },

    /**
     * Fetch pre-built bias test prompts
     * @returns {Promise<Array>} List of bias test prompts
     */
    async fetchBiasPrompts() {
        try {
            const response = await fetch(`${API_BASE_URL}/bias-prompts`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.prompts;
        } catch (error) {
            console.error('Error fetching bias prompts:', error);
            // Don't throw error for prompts - just return empty array
            return [];
        }
    },

    /**
     * Check backend health
     * @returns {Promise<Object>} Health status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error checking health:', error);
            throw new Error(`Backend health check failed: ${error.message}`);
        }
    }
};
