import { HealthcareQueryApp } from './app.js';

// CONFIG is loaded via script tag in index.html from /config.js
// We'll access it from the global window object
// (config.js will be updated to export properly in the next step)

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HealthcareQueryApp();
});
