/**
 * Healthcare Security Research Project
 * Created for Boston University CS 674 Database Security Fall 2025
 * Author: Sarah Sund-Lussier (SarahSL@bu.edu)
 * GitHub: https://github.com/sarahsl-prog/Database_Security_TestApp
 *
 * Healthcare Database Application Configuration
 * This file contains all host and service configurations
 * Configuration values can be overridden by creating a config.local.js file
 */

// Helper function to load environment variables (for Vite/build tools)
const getEnvVar = (key, defaultValue) => {
    // In browser, environment variables are not available
    // Just return the default value
    return defaultValue;
};

// Detect if we're in development mode (running on localhost/Vite dev server)
const isDevelopmentMode = () => {
    return window.location.hostname === 'localhost' ||
           window.location.hostname === '127.0.0.1' ||
           window.location.port === '3000';
};

const CONFIG = {
    // Service host definitions
    // These can be overridden by environment variables or config.local.js
    hosts: {
        WEB: {
            name: "Backend API Server",
            host: getEnvVar('VITE_BACKEND_HOST', getEnvVar('BACKEND_HOST', 'localhost')),
            port: parseInt(getEnvVar('VITE_BACKEND_PORT', getEnvVar('BACKEND_PORT', "5000"))),
            protocol: getEnvVar('VITE_BACKEND_PROTOCOL', "http")
        },
        DB: {
            name: "PostgreSQL Database",
            host: getEnvVar('VITE_DB_HOST', getEnvVar('DB_HOST', 'localhost')),
            port: parseInt(getEnvVar('VITE_DB_PORT', getEnvVar('DB_PORT', "5432"))),
            protocol: "postgresql",
            database: getEnvVar('VITE_DB_NAME', getEnvVar('DB_NAME', "healthcare_security"))
        },
        LLM: {
            name: "Ollama LLM Service",
            host: getEnvVar('VITE_LLM_HOST', getEnvVar('LLM_HOST', 'localhost')),
            port: parseInt(getEnvVar('VITE_LLM_PORT', getEnvVar('LLM_PORT', "11434"))),
            protocol: "http"
        }
    },

    // API endpoints for backend service
    api: {
        login: "/api/login",
        verify: "/api/verify",
        query: "/api/query",
        health: "/api/health"
    },

    // Timeout configurations (in milliseconds)
    timeouts: {
        authentication: 10000,  // 10 seconds
        query: 30000,          // 30 seconds  
        health_check: 5000     // 5 seconds
    },

    // Application settings
    app: {
        name: "Healthcare Database Security Research Platform",
        version: "1.0.0",
        max_query_history: 50,
        auto_health_check_interval: 30000  // 30 seconds
    }
};

// Helper functions to build URLs
CONFIG.getUrl = function(hostKey, path = "") {
    const host = this.hosts[hostKey];
    if (!host) {
        throw new Error(`Unknown host key: ${hostKey}`);
    }
    
    let url = `${host.protocol}://${host.host}:${host.port}`;
    if (path) {
        url += path.startsWith('/') ? path : '/' + path;
    }
    return url;
};

CONFIG.getBackendUrl = function(endpoint = "") {
    // In development mode with Vite dev server, use relative URLs for proxy
    if (isDevelopmentMode()) {
        // Just return the endpoint path - Vite proxy will handle routing
        return endpoint || "";
    }
    // In production, build full URL
    return this.getUrl('WEB', endpoint);
};

CONFIG.getHealthUrls = function() {
    // In development mode, use proxy for backend health check
    if (isDevelopmentMode()) {
        return {
            backend: this.api.health,  // Use relative URL for proxy
            database: `${this.hosts.DB.protocol}://${this.hosts.DB.host}:${this.hosts.DB.port}`,
            llm: `${this.hosts.LLM.protocol}://${this.hosts.LLM.host}:${this.hosts.LLM.port}/health`
        };
    }
    // In production, use full URLs
    return {
        backend: this.getUrl('WEB', this.api.health),
        database: `${this.hosts.DB.protocol}://${this.hosts.DB.host}:${this.hosts.DB.port}`,
        llm: this.getUrl('LLM', '/health')
    };
};

// Validate configuration on load
CONFIG.validate = function() {
    const requiredHosts = ['WEB', 'DB', 'LLM'];
    for (const hostKey of requiredHosts) {
        if (!this.hosts[hostKey]) {
            throw new Error(`Missing required host configuration: ${hostKey}`);
        }
        const host = this.hosts[hostKey];
        if (!host.host || !host.port || !host.protocol) {
            throw new Error(`Invalid host configuration for ${hostKey}: missing host, port, or protocol`);
        }
    }
    return true;
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// Make available globally in browser
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}

// Validate configuration on load
try {
    CONFIG.validate();
    console.log('✅ Configuration loaded and validated successfully');
    console.log(`Backend API: ${CONFIG.getBackendUrl()}`);
} catch (error) {
    console.error('❌ Configuration validation failed:', error.message);
}