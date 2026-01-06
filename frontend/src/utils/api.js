/**
 * API Client Utility
 * Handles all HTTP requests to the backend API
 */

export class ApiClient {
    constructor(baseUrl, authToken = null) {
        this.baseUrl = baseUrl;
        this.authToken = authToken;
    }

    /**
     * Set authentication token
     */
    setAuthToken(token) {
        this.authToken = token;
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        return this.authToken;
    }

    /**
     * Build headers for API requests
     */
    buildHeaders(customHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };

        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        return headers;
    }

    /**
     * Execute a query
     */
    async executeQuery(query) {
        const response = await fetch(`${this.baseUrl}/api/query`, {
            method: 'POST',
            headers: this.buildHeaders(),
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Request failed' }));
            throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Login user
     */
    async login(username, password, role = 'patient') {
        const response = await fetch(`${this.baseUrl}/api/login`, {
            method: 'POST',
            headers: this.buildHeaders(),
            body: JSON.stringify({ username, password, role })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Login failed' }));
            throw new Error(error.error || 'Authentication failed');
        }

        const data = await response.json();

        if (data.token) {
            this.setAuthToken(data.token);
        }

        return data;
    }

    /**
     * Verify authentication token
     */
    async verify() {
        const response = await fetch(`${this.baseUrl}/api/verify`, {
            method: 'GET',
            headers: this.buildHeaders()
        });

        if (!response.ok) {
            throw new Error('Token verification failed');
        }

        return response.json();
    }

    /**
     * Check system health
     */
    async checkHealth() {
        const response = await fetch(`${this.baseUrl}/api/health`, {
            method: 'GET',
            headers: this.buildHeaders()
        });

        if (!response.ok) {
            throw new Error('Health check failed');
        }

        return response.json();
    }

    /**
     * Generic GET request
     */
    async get(endpoint) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'GET',
            headers: this.buildHeaders()
        });

        if (!response.ok) {
            throw new Error(`GET ${endpoint} failed: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Generic POST request
     */
    async post(endpoint, data) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: this.buildHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`POST ${endpoint} failed: ${response.statusText}`);
        }

        return response.json();
    }
}

// Export default instance creator
export function createApiClient(baseUrl, authToken = null) {
    return new ApiClient(baseUrl, authToken);
}
