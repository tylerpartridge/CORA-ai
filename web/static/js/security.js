/**
 * Security utilities for CORA frontend
 * Prevents XSS attacks by sanitizing user input
 */

// HTML entity mapping for common characters
const htmlEntities = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
};

/**
 * Sanitize HTML string to prevent XSS
 * @param {string} str - String to sanitize
 * @returns {string} - Sanitized string
 */
function sanitizeHtml(str) {
    if (typeof str !== 'string') {
        return String(str);
    }
    
    return str.replace(/[&<>"'/]/g, function(match) {
        return htmlEntities[match];
    });
}

/**
 * Safely set innerHTML with sanitized content
 * @param {HTMLElement} element - DOM element
 * @param {string} content - HTML content to set
 */
function safeInnerHTML(element, content) {
    if (element && content) {
        element.innerHTML = sanitizeHtml(content);
    }
}

/**
 * Create safe HTML from template with sanitized data
 * @param {string} template - HTML template string
 * @param {Object} data - Data object with values to sanitize
 * @returns {string} - Safe HTML string
 */
function createSafeHTML(template, data) {
    let safeHTML = template;
    
    // Replace all ${variable} with sanitized values
    for (const [key, value] of Object.entries(data)) {
        const placeholder = `\${${key}}`;
        const sanitizedValue = sanitizeHtml(value);
        safeHTML = safeHTML.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), sanitizedValue);
    }
    
    return safeHTML;
}

/**
 * Safely create table rows from user data
 * @param {Array} users - Array of user objects
 * @returns {string} - Safe HTML for table rows
 */
function createSafeUserRows(users) {
    if (!users || users.length === 0) {
        return '<tr><td colspan="6" class="text-center">No users found</td></tr>';
    }
    
    return users.map(user => {
        const safeEmail = sanitizeHtml(user.email);
        const safeCreatedAt = sanitizeHtml(new Date(user.created_at).toLocaleDateString());
        const isActive = user.is_active === 'true';
        const statusClass = isActive ? 'bg-success' : 'bg-secondary';
        const statusText = isActive ? 'Active' : 'Inactive';
        
        return `
            <tr>
                <td>${safeEmail}</td>
                <td>-</td>
                <td>
                    <span class="badge ${statusClass}">
                        ${statusText}
                    </span>
                </td>
                <td>${safeCreatedAt}</td>
                <td>-</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewUser('${safeEmail}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Safely create feedback cards from feedback data
 * @param {Array} feedback - Array of feedback objects
 * @returns {string} - Safe HTML for feedback cards
 */
function createSafeFeedbackCards(feedback) {
    if (!feedback || feedback.length === 0) {
        return '<div class="alert alert-info">No feedback submitted yet</div>';
    }
    
    return feedback.map(item => {
        const safeCategory = sanitizeHtml(item.category);
        const safeMessage = sanitizeHtml(item.message);
        const safeUserEmail = sanitizeHtml(item.user_email);
        const safeCreatedAt = sanitizeHtml(new Date(item.created_at).toLocaleDateString());
        const rating = item.rating || 0;
        const stars = '★'.repeat(rating) + '☆'.repeat(5 - rating);
        
        return `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title">${safeCategory}</h6>
                            <p class="card-text">${safeMessage}</p>
                            <small class="text-muted">By: ${safeUserEmail}</small>
                        </div>
                        <div class="text-end">
                            ${rating > 0 ? `<div class="text-warning">${stars}</div>` : ''}
                            <small class="text-muted">${safeCreatedAt}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Safely create expense cards from expense data
 * @param {Array} expenses - Array of expense objects
 * @returns {string} - Safe HTML for expense cards
 */
function createSafeExpenseCards(expenses) {
    if (!expenses || expenses.length === 0) {
        return '<div class="alert alert-info">No expenses found</div>';
    }
    
    return expenses.map(expense => {
        const safeDescription = sanitizeHtml(expense.description);
        const safeVendor = sanitizeHtml(expense.vendor);
        const safeAmount = sanitizeHtml(expense.amount);
        const safeDate = sanitizeHtml(new Date(expense.date).toLocaleDateString());
        const safeCategory = sanitizeHtml(expense.category);
        
        return `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title">${safeDescription}</h6>
                            <p class="card-text">${safeVendor}</p>
                            <small class="text-muted">Category: ${safeCategory}</small>
                        </div>
                        <div class="text-end">
                            <h5 class="text-primary">$${safeAmount}</h5>
                            <small class="text-muted">${safeDate}</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Safely create transaction rows from transaction data
 * @param {Array} transactions - Array of transaction objects
 * @returns {string} - Safe HTML for transaction rows
 */
function createSafeTransactionRows(transactions) {
    if (!transactions || transactions.length === 0) {
        return '<tr><td colspan="5" class="text-center">No transactions found</td></tr>';
    }
    
    return transactions.map(transaction => {
        const safeId = sanitizeHtml(transaction.id);
        const safeAmount = sanitizeHtml(transaction.amount);
        const safeDescription = sanitizeHtml(transaction.description);
        const safeDate = sanitizeHtml(new Date(transaction.date).toLocaleDateString());
        const safeStatus = sanitizeHtml(transaction.status);
        
        return `
            <tr>
                <td>${safeId}</td>
                <td>$${safeAmount}</td>
                <td>${safeDescription}</td>
                <td>${safeDate}</td>
                <td><span class="badge bg-${safeStatus === 'completed' ? 'success' : 'warning'}">${safeStatus}</span></td>
            </tr>
        `;
    }).join('');
}

/**
 * Safely create account rows from account data
 * @param {Array} accounts - Array of account objects
 * @returns {string} - Safe HTML for account rows
 */
function createSafeAccountRows(accounts) {
    if (!accounts || accounts.length === 0) {
        return '<tr><td colspan="4" class="text-center">No accounts found</td></tr>';
    }
    
    return accounts.map(account => {
        const safeName = sanitizeHtml(account.name);
        const safeType = sanitizeHtml(account.type);
        const safeBalance = sanitizeHtml(account.balance);
        const safeMask = sanitizeHtml(account.mask);
        
        return `
            <tr>
                <td>${safeName}</td>
                <td>${safeType}</td>
                <td>$${safeBalance}</td>
                <td>****${safeMask}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Safely create sync history entries
 * @param {Array} history - Array of sync history objects
 * @returns {string} - Safe HTML for sync history
 */
function createSafeSyncHistory(history) {
    if (!history || history.length === 0) {
        return '<div class="alert alert-info">No sync history found</div>';
    }
    
    return history.map(entry => {
        const safeDate = sanitizeHtml(new Date(entry.date).toLocaleString());
        const safeStatus = sanitizeHtml(entry.status);
        const safeRecords = sanitizeHtml(entry.records_processed);
        
        return `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span>${safeDate}</span>
                <span class="badge bg-${safeStatus === 'success' ? 'success' : 'danger'}">${safeStatus}</span>
                <span>${safeRecords} records</span>
            </div>
        `;
    }).join('');
}

/**
 * Safely create error list
 * @param {Array} errors - Array of error strings
 * @returns {string} - Safe HTML for error list
 */
function createSafeErrorList(errors) {
    if (!errors || errors.length === 0) {
        return '<div class="alert alert-info">No errors found</div>';
    }
    
    return errors.map(error => {
        const safeError = sanitizeHtml(error);
        return `<div>• ${safeError}</div>`;
    }).join('');
}

/**
 * Safely create activity log rows
 * @param {Array} logs - Array of activity log objects
 * @returns {string} - Safe HTML for activity log rows
 */
function createSafeActivityRows(logs) {
    if (!logs || logs.length === 0) {
        return '<tr><td colspan="4" class="text-center">No activity found</td></tr>';
    }
    
    return logs.map(log => {
        const safeAction = sanitizeHtml(log.action);
        const safeUserEmail = sanitizeHtml(log.user_email);
        const safeTimestamp = sanitizeHtml(new Date(log.timestamp).toLocaleString());
        const safeDetails = sanitizeHtml(log.details);
        
        return `
            <tr>
                <td>${safeAction}</td>
                <td>${safeUserEmail}</td>
                <td>${safeTimestamp}</td>
                <td>${safeDetails}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Safely create backup list
 * @param {Array} backups - Array of backup objects
 * @returns {string} - Safe HTML for backup list
 */
function createSafeBackupList(backups) {
    if (!backups || backups.length === 0) {
        return '<div class="alert alert-info">No backups found</div>';
    }
    
    return backups.map(backup => {
        const safeFilename = sanitizeHtml(backup.filename);
        const safeSize = sanitizeHtml(backup.size);
        const safeDate = sanitizeHtml(new Date(backup.created_at).toLocaleString());
        const safeStatus = sanitizeHtml(backup.status);
        
        return `
            <tr>
                <td>${safeFilename}</td>
                <td>${safeSize}</td>
                <td>${safeDate}</td>
                <td><span class="badge bg-${safeStatus === 'completed' ? 'success' : 'warning'}">${safeStatus}</span></td>
            </tr>
        `;
    }).join('');
}

// Export functions for global use
window.CORASecurity = {
    sanitizeHtml,
    safeInnerHTML,
    createSafeHTML,
    createSafeUserRows,
    createSafeFeedbackCards,
    createSafeExpenseCards,
    createSafeTransactionRows,
    createSafeAccountRows,
    createSafeSyncHistory,
    createSafeErrorList,
    createSafeActivityRows,
    createSafeBackupList
}; 