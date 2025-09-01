/**
 * CORA Weekly Insights Validation Messages
 * Client-side validation messages for weekly insights report
 */

// Validation message templates for UI
const WEEKLY_INSIGHTS_VALIDATION_MESSAGES = {
    need_more_expenses: {
        title: "Not Enough Data Yet",
        message: "You need at least {needed} expenses to generate insights. You currently have {count}.",
        action: "Add more expenses to unlock insights",
        icon: "📊"
    },
    need_time_range: {
        title: "Building Your History",
        message: "We need at least {needed} days of expense data to spot trends. You've been tracking for {days} days.",
        action: "Keep tracking daily for better insights",
        icon: "📈"
    },
    no_recent_activity: {
        title: "No Recent Activity",
        message: "No expense activity in the last {window} days. Add some expenses to generate insights!",
        action: "Track today's expenses",
        icon: "💡"
    },
    sufficient_data: {
        title: "Ready for Insights!",
        message: "Great! You have enough data for meaningful weekly insights.",
        action: "Generate Report",
        icon: "✅"
    }
};

// Helper function to format validation messages
function formatValidationMessage(reason, context) {
    const template = WEEKLY_INSIGHTS_VALIDATION_MESSAGES[reason];
    if (!template) return null;
    
    let message = template.message;
    
    // Replace placeholders with context values
    if (context.needed) {
        message = message.replace('{needed}', context.needed);
    }
    if (context.expense_count !== undefined) {
        message = message.replace('{count}', context.expense_count);
    }
    if (context.days_active !== undefined) {
        message = message.replace('{days}', context.days_active);
    }
    if (context.window_days !== undefined) {
        message = message.replace('{window}', context.window_days);
    }
    
    return {
        title: template.title,
        message: message,
        action: template.action,
        icon: template.icon
    };
}

// Function to check if weekly insights can be generated
async function validateWeeklyInsights(window = '7d') {
    try {
        const response = await fetch(`/api/weekly/validate?window=${window}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to validate data');
        }
        
        const data = await response.json();
        return {
            valid: data.valid,
            reason: data.reason,
            formatted: formatValidationMessage(data.reason, data.context),
            context: data.context
        };
        
    } catch (error) {
        console.error('Validation error:', error);
        return {
            valid: false,
            reason: 'error',
            formatted: {
                title: "Validation Error",
                message: "Unable to validate data at this time. Please try again.",
                action: "Retry",
                icon: "⚠️"
            }
        };
    }
}

// Function to show validation UI
function showValidationMessage(validation) {
    const messageContainer = document.getElementById('weekly-insights-validation');
    if (!messageContainer) {
        console.warn('Weekly insights validation container not found');
        return;
    }
    
    const formatted = validation.formatted;
    
    // Create message HTML
    const messageHTML = `
        <div class="validation-message ${validation.valid ? 'valid' : 'invalid'}">
            <div class="validation-icon">${formatted.icon}</div>
            <div class="validation-content">
                <h4 class="validation-title">${formatted.title}</h4>
                <p class="validation-text">${formatted.message}</p>
                ${validation.valid ? 
                    `<button class="btn-primary" onclick="generateWeeklyInsights()">
                        ${formatted.action}
                    </button>` :
                    `<span class="validation-action">${formatted.action}</span>`
                }
            </div>
        </div>
    `;
    
    messageContainer.innerHTML = messageHTML;
    messageContainer.style.display = 'block';
}

// Function to generate weekly insights (if validation passes)
async function generateWeeklyInsights(window = '7d', sendEmail = true) {
    try {
        // First validate
        const validation = await validateWeeklyInsights(window);
        
        if (!validation.valid) {
            showValidationMessage(validation);
            return;
        }
        
        // Show loading state
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Generating...';
        button.disabled = true;
        
        // Generate the report
        const response = await fetch('/api/weekly/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                window: window,
                send_email: sendEmail
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.message || 'Failed to generate report');
        }
        
        const data = await response.json();
        
        // Show success message
        showSuccessMessage('Weekly insights generated successfully!', data.report);
        
        // Reset button
        button.textContent = originalText;
        button.disabled = false;
        
    } catch (error) {
        console.error('Generation error:', error);
        showErrorMessage(error.message);
        
        // Reset button
        if (button) {
            button.textContent = originalText;
            button.disabled = false;
        }
    }
}

// Success message display
function showSuccessMessage(message, report) {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">✅</div>
            <div class="notification-text">
                <strong>${message}</strong>
                ${report ? `
                    <div class="report-summary">
                        <small>
                            Total: $${report.metrics.total_spent.toFixed(2)} | 
                            ${report.metrics.expense_count} expenses | 
                            ${report.email_sent ? 'Email sent' : 'Email disabled'}
                        </small>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Error message display
function showErrorMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'notification error';
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">❌</div>
            <div class="notification-text">${message}</div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Auto-check validation on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Only run on dashboard or insights pages
    if (window.location.pathname.includes('dashboard') || 
        window.location.pathname.includes('insights')) {
        
        // Check if user can generate weekly insights
        const validation = await validateWeeklyInsights();
        
        // Update UI based on validation
        const insightsButton = document.getElementById('generate-weekly-insights');
        if (insightsButton) {
            insightsButton.disabled = !validation.valid;
            if (!validation.valid) {
                insightsButton.title = validation.formatted.message;
            }
        }
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        WEEKLY_INSIGHTS_VALIDATION_MESSAGES,
        formatValidationMessage,
        validateWeeklyInsights,
        generateWeeklyInsights
    };
}