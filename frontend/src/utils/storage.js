/**
 * Storage Utility
 * Wrapper around localStorage with error handling and type safety
 */

export class StorageManager {
    /**
     * Get item from localStorage
     */
    static get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            if (item === null) {
                return defaultValue;
            }
            return JSON.parse(item);
        } catch (error) {
            console.error(`Error reading from localStorage (key: ${key}):`, error);
            return defaultValue;
        }
    }

    /**
     * Set item in localStorage
     */
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error(`Error writing to localStorage (key: ${key}):`, error);
            return false;
        }
    }

    /**
     * Remove item from localStorage
     */
    static remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error(`Error removing from localStorage (key: ${key}):`, error);
            return false;
        }
    }

    /**
     * Clear all items from localStorage
     */
    static clear() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    }

    /**
     * Check if key exists in localStorage
     */
    static has(key) {
        return localStorage.getItem(key) !== null;
    }

    /**
     * Get all keys from localStorage
     */
    static keys() {
        return Object.keys(localStorage);
    }

    /**
     * Get number of items in localStorage
     */
    static size() {
        return localStorage.length;
    }

    /**
     * Get item as string (without JSON parsing)
     */
    static getString(key, defaultValue = '') {
        try {
            const item = localStorage.getItem(key);
            return item !== null ? item : defaultValue;
        } catch (error) {
            console.error(`Error reading string from localStorage (key: ${key}):`, error);
            return defaultValue;
        }
    }

    /**
     * Set item as string (without JSON stringifying)
     */
    static setString(key, value) {
        try {
            localStorage.setItem(key, value);
            return true;
        } catch (error) {
            console.error(`Error writing string to localStorage (key: ${key}):`, error);
            return false;
        }
    }

    /**
     * Get multiple items at once
     */
    static getMultiple(keys, defaultValue = null) {
        const results = {};
        keys.forEach(key => {
            results[key] = this.get(key, defaultValue);
        });
        return results;
    }

    /**
     * Set multiple items at once
     */
    static setMultiple(items) {
        let success = true;
        Object.entries(items).forEach(([key, value]) => {
            if (!this.set(key, value)) {
                success = false;
            }
        });
        return success;
    }

    /**
     * Remove multiple items at once
     */
    static removeMultiple(keys) {
        let success = true;
        keys.forEach(key => {
            if (!this.remove(key)) {
                success = false;
            }
        });
        return success;
    }
}

// Export convenience functions
export const getItem = (key, defaultValue) => StorageManager.get(key, defaultValue);
export const setItem = (key, value) => StorageManager.set(key, value);
export const removeItem = (key) => StorageManager.remove(key);
export const clearAll = () => StorageManager.clear();
export const hasItem = (key) => StorageManager.has(key);
