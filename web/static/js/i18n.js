/**
 * CORA Internationalization (i18n)
 * Provides Spanish language support for contractor-facing features
 */

class CORAI18n {
    constructor() {
        this.currentLocale = 'en';
        this.translations = {
            en: this.getEnglishTranslations(),
            es: this.getSpanishTranslations()
        };
        
        this.init();
    }
    
    init() {
        this.detectUserLanguage();
        this.createLanguageSwitcher();
        this.translatePage();
        this.addI18nStyles();
    }
    
    detectUserLanguage() {
        // Check for saved preference
        const savedLocale = localStorage.getItem('cora_locale');
        if (savedLocale && this.translations[savedLocale]) {
            this.currentLocale = savedLocale;
            return;
        }
        
        // Check browser language
        const browserLang = navigator.language || navigator.userLanguage;
        if (browserLang.startsWith('es')) {
            this.currentLocale = 'es';
        }
    }
    
    createLanguageSwitcher() {
        // Add language switcher to header
        const header = document.querySelector('.header-actions');
        if (header) {
            const langSwitcher = document.createElement('div');
            langSwitcher.className = 'language-switcher';
            langSwitcher.innerHTML = `
                <button class="lang-btn" onclick="coraI18n.toggleLanguage()">
                    <span class="lang-icon">🌐</span>
                    <span class="lang-text">${this.currentLocale.toUpperCase()}</span>
                </button>
            `;
            
            header.appendChild(langSwitcher);
        }
    }
    
    toggleLanguage() {
        this.currentLocale = this.currentLocale === 'en' ? 'es' : 'en';
        localStorage.setItem('cora_locale', this.currentLocale);
        
        // Update language switcher
        const langText = document.querySelector('.lang-text');
        if (langText) {
            langText.textContent = this.currentLocale.toUpperCase();
        }
        
        // Re-translate the page
        this.translatePage();
        
        // Show notification
        this.showLanguageNotification();
    }
    
    translatePage() {
        // Translate common elements
        this.translateElement('[data-i18n]');
        this.translateElement('[data-i18n-placeholder]', 'placeholder');
        this.translateElement('[data-i18n-title]', 'title');
        this.translateElement('[data-i18n-aria-label]', 'aria-label');
        
        // Translate dynamic content
        this.translateDynamicContent();
    }
    
    translateElement(selector, attribute = 'textContent') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n' + (attribute !== 'textContent' ? '-' + attribute.replace('-', '') : ''));
            if (key) {
                const translation = this.t(key);
                if (translation) {
                    if (attribute === 'textContent') {
                        element.textContent = translation;
                    } else {
                        element.setAttribute(attribute, translation);
                    }
                }
            }
        });
    }
    
    translateDynamicContent() {
        // Translate voice button states
        this.translateVoiceButton();
        
        // Translate notifications
        this.translateNotifications();
        
        // Translate error messages
        this.translateErrorMessages();
    }
    
    translateVoiceButton() {
        const voiceButton = document.querySelector('.voice-button');
        if (voiceButton) {
            const state = voiceButton.getAttribute('data-state');
            if (state) {
                const translation = this.t(`voice.${state}`);
                if (translation) {
                    voiceButton.setAttribute('aria-label', translation);
                }
            }
        }
    }
    
    translateNotifications() {
        // Update notification text if they exist
        const notifications = document.querySelectorAll('.notification-text');
        notifications.forEach(notification => {
            const originalText = notification.getAttribute('data-original-text');
            if (originalText) {
                const translation = this.t(originalText);
                if (translation) {
                    notification.textContent = translation;
                }
            }
        });
    }
    
    translateErrorMessages() {
        // Update error messages
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(error => {
            const originalText = error.getAttribute('data-original-text');
            if (originalText) {
                const translation = this.t(originalText);
                if (translation) {
                    error.textContent = translation;
                }
            }
        });
    }
    
    t(key, params = {}) {
        const keys = key.split('.');
        let translation = this.translations[this.currentLocale];
        
        for (const k of keys) {
            if (translation && translation[k]) {
                translation = translation[k];
            } else {
                // Fallback to English
                translation = this.translations.en;
                for (const fallbackKey of keys) {
                    if (translation && translation[fallbackKey]) {
                        translation = translation[fallbackKey];
                    } else {
                        return key; // Return key if no translation found
                    }
                }
                break;
            }
        }
        
        // Replace parameters
        if (typeof translation === 'string' && Object.keys(params).length > 0) {
            Object.keys(params).forEach(param => {
                translation = translation.replace(`{${param}}`, params[param]);
            });
        }
        
        return translation || key;
    }
    
    showLanguageNotification() {
        const message = this.currentLocale === 'es' 
            ? 'Idioma cambiado a español' 
            : 'Language changed to English';
            
        const notification = document.createElement('div');
        notification.className = 'language-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">🌐</div>
                <div class="notification-text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    getEnglishTranslations() {
        return {
            // Voice button states
            voice: {
                idle: 'Click to start voice recording',
                recording: 'Recording... Click to stop',
                processing: 'Processing your voice input...',
                success: 'Voice input processed successfully',
                error: 'Voice input failed. Please try again.'
            },
            
            // Common UI elements
            common: {
                loading: 'Loading...',
                error: 'Error',
                success: 'Success',
                cancel: 'Cancel',
                save: 'Save',
                delete: 'Delete',
                edit: 'Edit',
                close: 'Close',
                back: 'Back',
                next: 'Next',
                previous: 'Previous',
                submit: 'Submit',
                confirm: 'Confirm',
                yes: 'Yes',
                no: 'No'
            },
            
            // Navigation
            nav: {
                dashboard: 'Dashboard',
                expenses: 'Expenses',
                jobs: 'Jobs',
                reports: 'Reports',
                settings: 'Settings',
                profile: 'Profile',
                logout: 'Logout'
            },
            
            // Dashboard sections
            dashboard: {
                overview: 'Overview',
                recentExpenses: 'Recent Expenses',
                jobProfitability: 'Job Profitability',
                voiceEntry: 'Voice Entry',
                alerts: 'Alerts',
                metrics: 'Metrics'
            },
            
            // Voice commands
            voiceCommands: {
                examples: 'Voice Command Examples',
                tip1: 'Speak clearly and at a normal pace',
                tip2: 'Include the vendor name first',
                tip3: 'Mention the amount clearly',
                tip4: 'Add the job name if applicable',
                tip5: 'Use natural language - don\'t worry about perfect grammar'
            },
            
            // Error messages
            errors: {
                networkError: 'Network error. Please check your connection.',
                serverError: 'Server error. Please try again later.',
                validationError: 'Please check your input and try again.',
                permissionError: 'Permission denied. Please check your settings.',
                timeoutError: 'Request timed out. Please try again.'
            },
            
            // Notifications
            notifications: {
                expenseAdded: 'Expense added successfully',
                expenseUpdated: 'Expense updated successfully',
                expenseDeleted: 'Expense deleted successfully',
                jobAdded: 'Job added successfully',
                jobUpdated: 'Job updated successfully',
                voiceProcessed: 'Voice input processed successfully',
                offlineMode: 'Working in offline mode. Changes will sync when online.'
            },
            
            // Export
            export: {
                title: 'Export Data',
                expenses: 'Expenses',
                jobs: 'Jobs',
                summary: 'Summary Report',
                csv: 'CSV',
                pdf: 'PDF',
                dateRange: 'Date Range',
                from: 'From',
                to: 'To',
                exportData: 'Export Data',
                exporting: 'Exporting...',
                exportSuccess: 'Export completed successfully',
                exportError: 'Export failed. Please try again.'
            }
        };
    }
    
    getSpanishTranslations() {
        return {
            // Voice button states
            voice: {
                idle: 'Haz clic para comenzar la grabación de voz',
                recording: 'Grabando... Haz clic para detener',
                processing: 'Procesando tu entrada de voz...',
                success: 'Entrada de voz procesada exitosamente',
                error: 'La entrada de voz falló. Por favor intenta de nuevo.'
            },
            
            // Common UI elements
            common: {
                loading: 'Cargando...',
                error: 'Error',
                success: 'Éxito',
                cancel: 'Cancelar',
                save: 'Guardar',
                delete: 'Eliminar',
                edit: 'Editar',
                close: 'Cerrar',
                back: 'Atrás',
                next: 'Siguiente',
                previous: 'Anterior',
                submit: 'Enviar',
                confirm: 'Confirmar',
                yes: 'Sí',
                no: 'No'
            },
            
            // Navigation
            nav: {
                dashboard: 'Panel de Control',
                expenses: 'Gastos',
                jobs: 'Trabajos',
                reports: 'Reportes',
                settings: 'Configuración',
                profile: 'Perfil',
                logout: 'Cerrar Sesión'
            },
            
            // Dashboard sections
            dashboard: {
                overview: 'Resumen',
                recentExpenses: 'Gastos Recientes',
                jobProfitability: 'Rentabilidad de Trabajos',
                voiceEntry: 'Entrada de Voz',
                alerts: 'Alertas',
                metrics: 'Métricas'
            },
            
            // Voice commands
            voiceCommands: {
                examples: 'Ejemplos de Comandos de Voz',
                tip1: 'Habla claramente y a un ritmo normal',
                tip2: 'Incluye el nombre del proveedor primero',
                tip3: 'Menciona el monto claramente',
                tip4: 'Agrega el nombre del trabajo si aplica',
                tip5: 'Usa lenguaje natural - no te preocupes por la gramática perfecta'
            },
            
            // Error messages
            errors: {
                networkError: 'Error de red. Por favor verifica tu conexión.',
                serverError: 'Error del servidor. Por favor intenta más tarde.',
                validationError: 'Por favor verifica tu entrada e intenta de nuevo.',
                permissionError: 'Permiso denegado. Por favor verifica tu configuración.',
                timeoutError: 'Tiempo de espera agotado. Por favor intenta de nuevo.'
            },
            
            // Notifications
            notifications: {
                expenseAdded: 'Gasto agregado exitosamente',
                expenseUpdated: 'Gasto actualizado exitosamente',
                expenseDeleted: 'Gasto eliminado exitosamente',
                jobAdded: 'Trabajo agregado exitosamente',
                jobUpdated: 'Trabajo actualizado exitosamente',
                voiceProcessed: 'Entrada de voz procesada exitosamente',
                offlineMode: 'Trabajando en modo sin conexión. Los cambios se sincronizarán cuando estés en línea.'
            },
            
            // Export
            export: {
                title: 'Exportar Datos',
                expenses: 'Gastos',
                jobs: 'Trabajos',
                summary: 'Reporte de Resumen',
                csv: 'CSV',
                pdf: 'PDF',
                dateRange: 'Rango de Fechas',
                from: 'Desde',
                to: 'Hasta',
                exportData: 'Exportar Datos',
                exporting: 'Exportando...',
                exportSuccess: 'Exportación completada exitosamente',
                exportError: 'La exportación falló. Por favor intenta de nuevo.'
            }
        };
    }
    
    addI18nStyles() {
        const styleId = 'i18n-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .language-switcher {
                margin-left: 8px;
            }
            
            .lang-btn {
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .lang-btn:hover {
                background: #e5e7eb;
                transform: translateY(-1px);
            }
            
            .lang-icon {
                font-size: 14px;
            }
            
            .lang-text {
                font-weight: 600;
                color: #374151;
            }
            
            .language-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 12px 16px;
                z-index: 10001;
                animation: slideInRight 0.3s ease;
                max-width: 300px;
                border-left: 4px solid #9B6EC8;
            }
            
            .language-notification .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .language-notification .notification-icon {
                font-size: 16px;
            }
            
            .language-notification .notification-text {
                font-size: 14px;
                color: #374151;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @media (max-width: 768px) {
                .lang-btn {
                    padding: 4px 8px;
                    font-size: 11px;
                }
                
                .lang-text {
                    display: none; /* Hide text on mobile, show only icon */
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    // Public API for other modules
    getCurrentLocale() {
        return this.currentLocale;
    }
    
    isSpanish() {
        return this.currentLocale === 'es';
    }
    
    // Format currency based on locale
    formatCurrency(amount, currency = 'USD') {
        const options = {
            style: 'currency',
            currency: currency
        };
        
        if (this.currentLocale === 'es') {
            options.locale = 'es-US';
        } else {
            options.locale = 'en-US';
        }
        
        return new Intl.NumberFormat(options.locale, options).format(amount);
    }
    
    // Format date based on locale
    formatDate(date) {
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        if (this.currentLocale === 'es') {
            options.locale = 'es-US';
        } else {
            options.locale = 'en-US';
        }
        
        return new Intl.DateTimeFormat(options.locale, options).format(new Date(date));
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.coraI18n = new CORAI18n();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CORAI18n;
} 