/**
 * API Client for Backend Communication
 */

const API_BASE_URL = import.meta.env.PUBLIC_BACKEND_URL || 'http://localhost:8000';
const NETLIFY_FUNCTIONS_URL = '/.netlify/functions';

class APIClient {
  constructor() {
    this.baseURL = this.isProduction() ? NETLIFY_FUNCTIONS_URL : API_BASE_URL;
  }

  isProduction() {
    return import.meta.env.PROD || window.location.hostname !== 'localhost';
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request('/health');
  }

  // Get blog statistics
  async getStats() {
    return this.request('/api/stats');
  }

  // Get trending topics
  async getTrends(keywords = [], timeframe = 'today 3-m') {
    return this.request('/api/trends', {
      method: 'POST',
      body: JSON.stringify({ keywords, timeframe }),
    });
  }

  // Generate blog ideas
  async generateIdeas(category = 'tech') {
    return this.request('/api/generate-ideas', {
      method: 'POST',
      body: JSON.stringify({ category }),
    });
  }

  // Analyze content from URL
  async analyzeContent(url) {
    return this.request('/api/analyze-content', {
      method: 'POST',
      body: JSON.stringify({ url, extract_meta: true }),
    });
  }

  // AI Assistant
  async askAI(prompt, maxTokens = 150) {
    return this.request('/api/ai-assistant', {
      method: 'POST',
      body: JSON.stringify({ prompt, max_tokens: maxTokens }),
    });
  }
}

// Export singleton instance
export const api = new APIClient();

// Export for use in Astro components
export default api;
