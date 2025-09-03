/**
 * CORA Export Manager - Backward Compatibility Shim
 * Loads the modular ExportManager and maintains window.exportManager API
 */

// Import the modular ExportManager
import { ExportManager } from './export_manager/index.js';

// Auto-initialize when DOM is ready (backward compatibility)
document.addEventListener('DOMContentLoaded', () => {
    window.exportManager = new ExportManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExportManager;
}