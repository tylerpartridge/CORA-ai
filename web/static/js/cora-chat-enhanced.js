/**
 * CORA Chat Enhanced - Advanced AI Assistant
 * Enhanced with smart notifications, context awareness, and improved UX
 * 
 * Features:
 * - Smart notifications and alerts
 * - Context-aware responses
 * - Voice input support
 * - File upload capabilities
 * - Conversation history
 * - Quick actions and shortcuts
 * - Accessibility enhancements
 */

class CoraChatEnhanced {
    constructor() {
        this.messagesRemaining = 10;
        this.messages = [];
        this.isOpen = false;
        this.conversationId = this.generateConversationId();
        this.context = {
            currentPage: window.location.pathname,
            userPreferences: {},
            recentActions: [],
            businessContext: null
        };
        this.notifications = [];
        this.voiceRecognition = null;
        this.isListening = false;
        
        this.initializeElements();
        this.appendToDOM();
        this.bindEvents();
        this.setupSmartNotifications();
        this.showWelcomeMessage();
        this.loadConversationHistory();
    }

    initializeElements() {
        // Enhanced chat bubble with notification indicator
        this.chatBubble = document.createElement('div');
        this.chatBubble.className = 'cora-chat-bubble enhanced';
        this.chatBubble.innerHTML = `
            <div class="chat-bubble-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3 .97 4.29L1 23l6.71-1.97C9 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.41 0-2.73-.36-3.88-.99l-.28-.15-2.91.85.85-2.91-.15-.28C4.36 14.73 4 13.41 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/>
                    <circle cx="8.5" cy="12" r="1.5"/>
                    <circle cx="12" cy="12" r="1.5"/>
                    <circle cx="15.5" cy="12" r="1.5"/>
                </svg>
            </div>
            <div class="notification-indicator" id="notification-indicator" style="display: none;">
                <span class="notification-count">0</span>
            </div>
        `;
        this.chatBubble.setAttribute('aria-label', 'Chat with CORA - Enhanced AI Assistant');
        this.chatBubble.setAttribute('role', 'button');
        this.chatBubble.setAttribute('tabindex', '0');

        // Create chat window markup
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'cora-chat-window enhanced';
        this.chatWindow.innerHTML = `
            <div class="cora-chat-header enhanced">
                <div class="header-content">
                    <div class="cora-avatar">
                        <div class="avatar-circle"><span>C</span></div>
                    </div>
                    <div class="header-info">
                        <h3>CORA AI Assistant</h3>
                        <div class="subtitle">Enhanced Intelligence for Contractors</div>
                        <div class="status-indicator">
                            <span class="status-dot online"></span>
                            <span class="status-text">Online</span>
                        </div>
                    </div>
                </div>
                <div class="header-actions">
                    <button class="action-btn minimize-btn" aria-label="Minimize chat" title="Minimize">−</button>
                    <button class="action-btn voice-btn" aria-label="Voice input" title="Voice input">🎤</button>
                    <button class="action-btn file-btn" aria-label="Upload file" title="Upload file">📎</button>
                    <button class="action-btn history-btn" aria-label="Conversation history" title="History">🕘</button>
                    <button class="cora-close-btn enhanced" aria-label="Close chat">×</button>
                </div>
            </div>
            <div class="cora-chat-messages enhanced show" role="log" aria-live="polite">
                <div class="messages-container"></div>
            </div>
            <div class="cora-chat-input enhanced">
                <div class="input-container">
                    <form class="cora-input-group enhanced">
                        <div class="input-wrapper">
                            <input type="text" placeholder="Ask CORA anything..." aria-label="Chat message input" class="enhanced-input">
                            <div class="input-actions">
                                <button type="button" class="emoji-btn" aria-label="Add emoji" title="Emoji">😊</button>
                                <button type="submit" class="send-btn enhanced" aria-label="Send message">➤</button>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="chat-footer">
                    <div class="messages-remaining enhanced"><span class="remaining-count">${this.messagesRemaining}</span> messages remaining</div>
                    <div class="quick-actions">
                        <button class="quick-action" data-action="expense-help">💡 Expense Help</button>
                        <button class="quick-action" data-action="profit-tips">📈 Profit Tips</button>
                        <button class="quick-action" data-action="voice-expense">🎤 Voice Expense</button>
                    </div>
                </div>
            </div>
        `;

        // Cache important refs now that markup exists
        this.messagesContainer = this.chatWindow.querySelector('.messages-container');
        this.inputField = this.chatWindow.querySelector('.enhanced-input');
        this.sendButton = this.chatWindow.querySelector('.send-btn');
        this.closeButton = this.chatWindow.querySelector('.cora-close-btn');
        this.voiceButton = this.chatWindow.querySelector('.voice-btn');
        this.fileButton = this.chatWindow.querySelector('.file-btn');
        this.historyButton = this.chatWindow.querySelector('.history-btn');
        this.minimizeButton = this.chatWindow.querySelector('.minimize-btn');
        this.notificationIndicator = document.getElementById('notification-indicator');
    }

    appendToDOM() {
        document.body.appendChild(this.chatBubble);
        document.body.appendChild(this.chatWindow);
    }

    bindEvents() {
        // Chat bubble events
        this.chatBubble.addEventListener('click', () => this.openChat());
        this.chatBubble.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.openChat();
            }
        });

        // Close button
        this.closeButton.addEventListener('click', () => this.closeChat());
        if (this.minimizeButton) this.minimizeButton.addEventListener('click', () => this.toggleMinimize());

        // Form submission
        this.chatWindow.querySelector('form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Voice button
        this.voiceButton.addEventListener('click', () => this.toggleVoiceInput());

        // File upload
        this.fileButton.addEventListener('click', () => this.triggerFileUpload());

        // History button
        this.historyButton.addEventListener('click', () => this.showConversationHistory());

        // Quick actions
        this.chatWindow.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            });
        });

        // Input focus and typing
        this.inputField.addEventListener('focus', () => this.onInputFocus());
        this.inputField.addEventListener('input', () => this.onInputChange());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Context awareness
        this.updateContext();
        window.addEventListener('popstate', () => this.updateContext());
        this.setupDrag();
    }

    setupSmartNotifications() {
        // Monitor for important events
        this.monitorSystemEvents();
        
        // Set up notification polling
        setInterval(() => this.checkForNotifications(), 30000); // Check every 30 seconds
        
        // Listen for custom events
        document.addEventListener('cora-notification', (e) => {
            this.addNotification(e.detail);
        });
    }

    monitorSystemEvents() {
        // Monitor expense creation
        document.addEventListener('expense-created', (e) => {
            this.addNotification({
                type: 'success',
                title: 'Expense Added',
                message: 'Your expense has been successfully recorded.',
                action: 'view-expense',
                data: e.detail
            });
        });

        // Monitor profit alerts
        document.addEventListener('profit-alert', (e) => {
            this.addNotification({
                type: 'warning',
                title: 'Profit Alert',
                message: e.detail.message,
                action: 'view-profit',
                data: e.detail
            });
        });

        // Monitor system errors
        document.addEventListener('system-error', (e) => {
            this.addNotification({
                type: 'error',
                title: 'System Issue',
                message: 'We detected an issue. CORA is here to help!',
                action: 'help-support',
                data: e.detail
            });
        });
    }

    addNotification(notification) {
        this.notifications.push({
            ...notification,
            id: this.generateNotificationId(),
            timestamp: new Date(),
            read: false
        });

        this.updateNotificationIndicator();
        this.showNotificationToast(notification);
    }

    updateNotificationIndicator() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        
        if (unreadCount > 0) {
            this.notificationIndicator.style.display = 'block';
            this.notificationIndicator.querySelector('.notification-count').textContent = unreadCount;
        } else {
            this.notificationIndicator.style.display = 'none';
        }
    }

    showNotificationToast(notification) {
        const toast = document.createElement('div');
        toast.className = `cora-notification-toast ${notification.type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">${this.getNotificationIcon(notification.type)}</div>
                <div class="toast-text">
                    <div class="toast-title">${notification.title}</div>
                    <div class="toast-message">${notification.message}</div>
                </div>
                <button class="toast-close" aria-label="Close notification">×</button>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            warning: '⚠️',
            error: '❌',
            info: 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage('user', message);
        this.inputField.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Get enhanced context
            const enhancedContext = await this.getEnhancedContext();
            
            // Call CORA API with context
            const response = await this.callCoraAPI(message, enhancedContext);
            
            // Add CORA response
            this.addMessage('cora', response);
            
            // Update context with this interaction
            this.updateContextWithInteraction(message, response);
            
            // Check for actionable items
            this.processResponseForActions(response);
            
        } catch (error) {
            this.addMessage('cora', 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.');
            // console.error('CORA API Error:', error);
        }

        this.hideTypingIndicator();
        this.updateRemainingCount();
    }

    async getEnhancedContext() {
        return {
            currentPage: window.location.pathname,
            userAgent: navigator.userAgent,
            screenSize: `${window.innerWidth}x${window.innerHeight}`,
            timeOfDay: new Date().toLocaleTimeString(),
            recentMessages: this.messages.slice(-5), // Last 5 messages
            notifications: this.notifications.filter(n => !n.read),
            businessContext: this.context.businessContext
        };
    }

    async callCoraAPI(message, context) {
        // Use Enhanced CORA endpoint with cookies for auth (if present)
        const response = await fetch('/api/cora-chat-v2/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                message,
                conversation_id: this.conversationId,
                metadata: context
            })
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
        }

        const data = await response.json();
        // Update remaining count from server if provided
        if (typeof data.messages_remaining === 'number') {
            this.messagesRemaining = data.messages_remaining;
            const remainingEl = this.chatWindow.querySelector('.remaining-count');
            if (remainingEl) remainingEl.textContent = this.messagesRemaining;
        }
        // Persist server-issued conversation id
        if (data.conversation_id) {
            this.conversationId = data.conversation_id;
        }
        return data.message || data.response || 'I apologize, but I couldn\'t process your request.';
    }

    addMessage(sender, text, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `cora-message ${sender}-message enhanced`;
        messageDiv.setAttribute('role', 'log');
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${sender === 'user' ? 'You' : 'CORA'}</span>
                    <span class="message-time">${timestamp}</span>
                </div>
                <div class="message-text">${this.formatMessage(text)}</div>
                ${metadata.actions ? this.renderMessageActions(metadata.actions) : ''}
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        
        // Store message
        this.messages.push({
            sender,
            text,
            timestamp: new Date(),
            metadata
        });

        // Save to local storage
        this.saveConversationHistory();
    }

    formatMessage(text) {
        // Convert URLs to links
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert markdown-style formatting
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert line breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    renderMessageActions(actions) {
        if (!actions || actions.length === 0) return '';
        
        const actionsHtml = actions.map(action => 
            `<button class="message-action" data-action="${action.type}" data-value="${action.value}">
                ${action.icon} ${action.label}
            </button>`
        ).join('');
        
        return `<div class="message-actions">${actionsHtml}</div>`;
    }

    toggleVoiceInput() {
        if (this.isListening) {
            this.stopVoiceRecognition();
        } else {
            this.startVoiceRecognition();
        }
    }

    startVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.addMessage('cora', 'Voice input is not supported in your browser. Please type your message.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.voiceRecognition = new SpeechRecognition();
        
        this.voiceRecognition.continuous = false;
        this.voiceRecognition.interimResults = false;
        this.voiceRecognition.lang = 'en-US';

        this.voiceRecognition.onstart = () => {
            this.isListening = true;
            this.voiceButton.classList.add('listening');
            this.addMessage('cora', '🎤 Listening... Please speak now.');
        };

        this.voiceRecognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.inputField.value = transcript;
            this.stopVoiceRecognition();
        };

        this.voiceRecognition.onerror = (event) => {
            this.addMessage('cora', 'Sorry, I couldn\'t understand that. Please try again or type your message.');
            this.stopVoiceRecognition();
        };

        this.voiceRecognition.onend = () => {
            this.stopVoiceRecognition();
        };

        this.voiceRecognition.start();
    }

    stopVoiceRecognition() {
        if (this.voiceRecognition) {
            this.voiceRecognition.stop();
        }
        this.isListening = false;
        this.voiceButton.classList.remove('listening');
    }

    triggerFileUpload() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,.pdf,.txt,.csv';
        input.multiple = true;
        
        input.onchange = (e) => {
            const files = Array.from(e.target.files);
            this.handleFileUpload(files);
        };
        
        input.click();
    }

    async handleFileUpload(files) {
        for (const file of files) {
            this.addMessage('user', `📎 Uploaded: ${file.name}`);
            
            try {
                // Here you would typically upload to server
                // For now, we'll just acknowledge the upload
                this.addMessage('cora', `I've received your file: ${file.name}. I can help you analyze it or extract information from it.`);
            } catch (error) {
                this.addMessage('cora', `Sorry, I couldn't process the file ${file.name}. Please try again.`);
            }
        }
    }

    handleQuickAction(action) {
        const actions = {
            'expense-help': 'How can I help you with expense tracking? I can show you how to categorize expenses, track receipts, or analyze spending patterns.',
            'profit-tips': 'Here are some quick profit optimization tips: 1) Review vendor pricing regularly, 2) Track job profitability, 3) Monitor material costs, 4) Optimize labor efficiency.',
            'voice-expense': 'Voice expense entry is available! Just say "Add expense" followed by the amount and description. For example: "Add expense 150 dollars for lumber".'
        };

        const message = actions[action];
        if (message) {
            this.addMessage('cora', message);
        }
    }

    processResponseForActions(response) {
        // Look for actionable items in CORA's response
        const actions = [];
        
        if (response.includes('expense') || response.includes('receipt')) {
            actions.push({
                type: 'add-expense',
                label: 'Add Expense',
                icon: '💰',
                value: 'expense'
            });
        }
        
        if (response.includes('profit') || response.includes('analysis')) {
            actions.push({
                type: 'view-profit',
                label: 'View Profit Analysis',
                icon: '📈',
                value: 'profit'
            });
        }
        
        if (response.includes('help') || response.includes('support')) {
            actions.push({
                type: 'get-help',
                label: 'Get Help',
                icon: '❓',
                value: 'help'
            });
        }

        if (actions.length > 0) {
            // Add actions to the last message
            const lastMessage = this.messagesContainer.lastElementChild;
            if (lastMessage && lastMessage.classList.contains('cora-message')) {
                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'message-actions';
                actionsDiv.innerHTML = actions.map(action => 
                    `<button class="message-action" data-action="${action.type}" data-value="${action.value}">
                        ${action.icon} ${action.label}
                    </button>`
                ).join('');
                lastMessage.querySelector('.message-content').appendChild(actionsDiv);
            }
        }
    }

    showConversationHistory() {
        // Create history modal
        const modal = document.createElement('div');
        modal.className = 'cora-history-modal';
        modal.innerHTML = `
            <div class="history-content">
                <div class="history-header">
                    <h3>Conversation History</h3>
                    <button class="close-history" aria-label="Close history">×</button>
                </div>
                <div class="history-list">
                    ${this.messages.map(msg => `
                        <div class="history-item ${msg.sender}-message">
                            <div class="history-time">${msg.timestamp.toLocaleString()}</div>
                            <div class="history-text">${msg.text}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close button
        modal.querySelector('.close-history').addEventListener('click', () => {
            modal.remove();
        });

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K to open chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.openChat();
        }
        
        // Escape to close chat
        if (e.key === 'Escape' && this.isOpen) {
            this.closeChat();
        }
    }

    updateContext() {
        this.context.currentPage = window.location.pathname;
        this.context.userAgent = navigator.userAgent;
        this.context.screenSize = `${window.innerWidth}x${window.innerHeight}`;
    }

    updateContextWithInteraction(userMessage, coraResponse) {
        this.context.recentActions.push({
            type: 'chat-interaction',
            userMessage,
            coraResponse,
            timestamp: new Date()
        });

        // Keep only last 10 actions
        if (this.context.recentActions.length > 10) {
            this.context.recentActions.shift();
        }
    }

    loadConversationHistory() {
        try {
            const saved = localStorage.getItem('cora-conversation-history');
            if (saved) {
                const history = JSON.parse(saved);
                this.messages = history.messages || [];
                this.context = { ...this.context, ...history.context };
            }
        } catch (error) {
            // console.warn('Could not load conversation history:', error);
        }
    }

    saveConversationHistory() {
        try {
            const history = {
                messages: this.messages.slice(-50), // Keep last 50 messages
                context: this.context,
                timestamp: new Date()
            };
            localStorage.setItem('cora-conversation-history', JSON.stringify(history));
        } catch (error) {
            // console.warn('Could not save conversation history:', error);
        }
    }

    showWelcomeMessage() {
        const welcomeMessage = "Hi! I'm CORA, your enhanced AI assistant for contractors.";
        // Version marker for debugging cache: v5.4
        
        this.addMessage('cora', welcomeMessage);
    }

    openChat() {
        this.isOpen = true;
        this.chatWindow.style.display = 'flex';
        this.chatWindow.classList.add('open');
        this.chatBubble.classList.add('hidden');
        this.inputField.focus();
        
        // Announce to screen readers
        this.announceToScreenReader('CORA chat opened');
    }

    closeChat() {
        this.isOpen = false;
        this.chatWindow.classList.remove('open');
        this.chatWindow.style.display = 'none';
        this.chatBubble.classList.remove('hidden');
        
        // Announce to screen readers
        this.announceToScreenReader('CORA chat closed');
    }

    toggleMinimize() {
        this.chatWindow.classList.toggle('minimized');
    }

    setupDrag() {
        const header = this.chatWindow.querySelector('.cora-chat-header.enhanced');
        if (!header) return;
        let dragging = false, startX = 0, startY = 0, left = 0, top = 0;

        const beginDrag = (clientX, clientY, target) => {
            if (target && target.closest && target.closest('button')) return;
            dragging = true;
            startX = clientX; startY = clientY;
            const rect = this.chatWindow.getBoundingClientRect();
            left = rect.left; top = rect.top;
            this.chatWindow.style.left = left + 'px';
            this.chatWindow.style.top = top + 'px';
            this.chatWindow.style.right = 'auto';
            this.chatWindow.style.bottom = 'auto';
            document.body.style.userSelect = 'none';
        };

        const moveDrag = (clientX, clientY) => {
            if (!dragging) return;
            const dx = clientX - startX; const dy = clientY - startY;
            let nl = left + dx; let nt = top + dy;
            const vw = window.innerWidth, vh = window.innerHeight;
            const rect = this.chatWindow.getBoundingClientRect();
            nl = Math.max(10, Math.min(nl, vw - rect.width - 10));
            nt = Math.max(10, Math.min(nt, vh - rect.height - 10));
            this.chatWindow.style.left = nl + 'px';
            this.chatWindow.style.top = nt + 'px';
        };

        const endDrag = () => {
            dragging = false;
            document.body.style.userSelect = '';
        };

        // Mouse
        header.addEventListener('mousedown', (e) => {
            if (e.button !== undefined && e.button !== 0) return;
            beginDrag(e.clientX, e.clientY, e.target);
        });
        window.addEventListener('mousemove', (e) => moveDrag(e.clientX, e.clientY));
        window.addEventListener('mouseup', endDrag);

        // Touch
        header.addEventListener('touchstart', (e) => {
            if (!e.touches || e.touches.length === 0) return;
            const t = e.touches[0];
            beginDrag(t.clientX, t.clientY, e.target);
            e.preventDefault();
        }, { passive: false });
        window.addEventListener('touchmove', (e) => {
            if (!e.touches || e.touches.length === 0) return;
            const t = e.touches[0];
            moveDrag(t.clientX, t.clientY);
            e.preventDefault();
        }, { passive: false });
        window.addEventListener('touchend', endDrag);
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'cora-typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="typing-text">CORA is typing...</span>
        `;
        typingDiv.id = 'typing-indicator';
        
        this.messagesContainer.appendChild(typingDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    updateRemainingCount() {
        this.messagesRemaining = Math.max(0, this.messagesRemaining - 1);
        this.remainingText.textContent = this.messagesRemaining;
        
        if (this.messagesRemaining <= 2) {
            this.showSignupPrompt();
        }
    }

    showSignupPrompt() {
        const signupMessage = `
            🎉 You're getting great value from CORA! 
            
            Sign up for unlimited access to:
            • Unlimited conversations
            • Advanced AI features
            • Business analytics
            • Priority support
            
            <a href="/signup" class="signup-link">Sign up now</a>
        `;
        
        this.addMessage('cora', signupMessage);
    }

    getAuthToken() {
        // Get auth token from localStorage or cookies
        return localStorage.getItem('auth_token') || '';
    }

    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    generateNotificationId() {
        return 'notif_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            announcement.remove();
        }, 1000);
    }

    // Public API methods
    addSmartNotification(notification) {
        this.addNotification(notification);
    }

    getConversationStats() {
        return {
            totalMessages: this.messages.length,
            userMessages: this.messages.filter(m => m.sender === 'user').length,
            coraMessages: this.messages.filter(m => m.sender === 'cora').length,
            unreadNotifications: this.notifications.filter(n => !n.read).length,
            messagesRemaining: this.messagesRemaining
        };
    }

    destroy() {
        // Cleanup
        if (this.voiceRecognition) {
            this.voiceRecognition.stop();
        }
        
        // Remove elements
        if (this.chatBubble.parentNode) {
            this.chatBubble.parentNode.removeChild(this.chatBubble);
        }
        if (this.chatWindow.parentNode) {
            this.chatWindow.parentNode.removeChild(this.chatWindow);
        }
    }

    /**
     * Check for new notifications
     */
    async checkForNotifications() {
        try {
            // Placeholder for notification checking
            // In the future, this could fetch notifications from the server
            // console.log('🔔 Checking for notifications...');
        } catch (error) {
            // console.error('Error checking notifications:', error);
        }
    }
}

// Expose class on window for dynamic loaders
if (typeof window !== 'undefined') {
    window.CoraChatEnhanced = CoraChatEnhanced;
}

// Initialize enhanced CORA chat when DOM is ready or immediately if ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.coraChatEnhanced) {
            window.coraChatEnhanced = new CoraChatEnhanced();
        }
    });
} else {
    if (!window.coraChatEnhanced) {
        window.coraChatEnhanced = new CoraChatEnhanced();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CoraChatEnhanced;
}