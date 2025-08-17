/**
 * LEGACY: CORA Chat (Deprecated)
 * This file is retained temporarily for safety. It is no longer referenced by templates,
 * service worker, or monitoring scripts. The enhanced widget is loaded via `cora_widget.js`.
 * Safe to delete after verification in staging.
 */

class CoraChat {
    constructor() {
        this.messagesRemaining = 10;
        this.messages = [];
        this.isOpen = false;
        this.conversationId = this.generateConversationId();
        this.initializeElements();
        this.bindEvents();
        this.showWelcomeMessage();
    }

    initializeElements() {
        // Create chat bubble
        this.chatBubble = document.createElement('div');
        this.chatBubble.className = 'cora-chat-bubble';
        this.chatBubble.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3 .97 4.29L1 23l6.71-1.97C9 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.41 0-2.73-.36-3.88-.99l-.28-.15-2.91.85.85-2.91-.15-.28C4.36 14.73 4 13.41 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/>
                <circle cx="8.5" cy="12" r="1.5"/>
                <circle cx="12" cy="12" r="1.5"/>
                <circle cx="15.5" cy="12" r="1.5"/>
            </svg>
        `;
        this.chatBubble.setAttribute('aria-label', 'Chat with CORA');
        this.chatBubble.setAttribute('role', 'button');
        this.chatBubble.setAttribute('tabindex', '0');

        // Create welcome message
        this.welcomeMessage = document.createElement('div');
        this.welcomeMessage.className = 'cora-welcome-message';
        this.welcomeMessage.innerHTML = '💬 Hi! I\'m CORA. Let me help you. Ask me anything!';

        // Create chat window
        this.chatWindow = document.createElement('div');
        this.chatWindow.className = 'cora-chat-window';
        this.chatWindow.innerHTML = `
            <div class="cora-chat-header">
                <div>
                    <h3>CORA</h3>
                    <div class="subtitle">AI for Contractors</div>
                </div>
                <button class="cora-close-btn" aria-label="Close chat">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="cora-chat-messages" role="log" aria-live="polite"></div>
            <div class="cora-chat-input">
                <form class="cora-input-group">
                    <input type="text" placeholder="Type your message..." aria-label="Chat message input">
                    <button type="submit" aria-label="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </form>
                <div class="cora-messages-remaining">${this.messagesRemaining} messages remaining</div>
            </div>
        `;

        // Append elements to body
        document.body.appendChild(this.chatBubble);
        document.body.appendChild(this.welcomeMessage);
        document.body.appendChild(this.chatWindow);

        // Store references
        this.messagesContainer = this.chatWindow.querySelector('.cora-chat-messages');
        this.inputField = this.chatWindow.querySelector('input');
        this.sendButton = this.chatWindow.querySelector('button[type="submit"]');
        this.closeButton = this.chatWindow.querySelector('.cora-close-btn');
        this.remainingText = this.chatWindow.querySelector('.cora-messages-remaining');
    }

    bindEvents() {
        // Chat bubble click
        this.chatBubble.addEventListener('click', () => this.openChat());
        this.chatBubble.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.openChat();
            }
        });

        // Close button
        this.closeButton.addEventListener('click', () => this.closeChat());

        // Form submission
        this.chatWindow.querySelector('form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Make entire input area clickable to focus the input field
        const inputContainer = this.chatWindow.querySelector('.cora-chat-input');
        inputContainer.addEventListener('click', (e) => {
            // Only focus if we didn't click on the send button
            if (!e.target.closest('button')) {
                this.inputField.focus();
            }
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });

        // Make chat window draggable
        this.makeDraggable();
    }

    showWelcomeMessage() {
        // Show welcome message after 3 seconds
        setTimeout(() => {
            this.welcomeMessage.classList.add('show');
            this.chatBubble.classList.add('pulse');
            
            // Hide after 10 seconds
            setTimeout(() => {
                this.welcomeMessage.classList.remove('show');
                this.chatBubble.classList.remove('pulse');
            }, 10000);
        }, 3000);
    }

    openChat() {
        this.isOpen = true;
        this.chatWindow.classList.add('open');
        this.chatBubble.style.display = 'none';
        this.welcomeMessage.classList.remove('show');
        this.inputField.focus();

        // Show initial message if first time
        if (this.messages.length === 0) {
            this.addMessage('cora', 'Hi! I\'m CORA, your AI assistant for construction contractors. I help you track jobs, manage expenses, and save time on bookkeeping. What type of construction work do you do?');
        }
    }

    closeChat() {
        this.isOpen = false;
        this.chatWindow.classList.remove('open');
        this.chatBubble.style.display = 'flex';
    }

    async sendMessage() {
        const text = this.inputField.value.trim();
        if (!text) return;

        // Check message limit
        if (this.messagesRemaining <= 0) {
            this.showSignupPrompt();
            return;
        }

        // Add user message
        this.addMessage('user', text);
        this.inputField.value = '';
        this.sendButton.disabled = true;

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Call API
            const response = await this.callCoraAPI(text);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add CORA's response
            this.addMessage('cora', response.message);
            
            // Update remaining count from API response
            this.updateRemainingCount();
            
            // Check if we should prompt signup
            if (this.messagesRemaining <= 3 && response.suggestSignup) {
                this.addMessage('cora', 'By the way, I\'d love to show you exactly how much time and money you could save. Want to see a personalized demo?');
            }
        } catch (error) {
            this.hideTypingIndicator();
            // Use a more friendly message that doesn't suggest an error
            this.addMessage('cora', 'Let me help you with that! While my advanced features are loading, I can tell you that CORA saves entrepreneurs 20+ hours every month on financial tasks. What specific challenge are you facing?');
        } finally {
            this.sendButton.disabled = false;
        }
    }

    async callCoraAPI(message) {
        try {
            const response = await fetch('/api/cora-ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    business_context: null,
                    personality_state: null
                })
            });

            if (!response.ok) {
                if (response.status === 429) {
                    const error = await response.json();
                    return {
                        message: "I'd love to keep chatting! Sign up for a free trial to continue our conversation.",
                        suggestSignup: true
                    };
                }
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            
            return {
                message: data.response,
                suggestSignup: false
            };
        } catch (error) {
            // Silently handle errors and use fallback responses
            // Don't log to console to avoid triggering error messages
            
            // Provide contextual fallback responses when server isn't running
            const fallbackResponses = {
                'price': "CORA starts at just $19/month with a 30-day free trial. No credit card required to start!",
                'quickbooks': "Yes! CORA integrates seamlessly with QuickBooks to save you even more time on bookkeeping.",
                'time': "Most entrepreneurs save 20+ hours per month with CORA handling their financial tracking automatically.",
                'tax': "CORA automatically categorizes expenses for taxes and provides year-end reports your accountant will love.",
                'default': "I'd love to help you save time on your finances! While I'm having connection issues right now, you can start your free trial to experience how CORA saves entrepreneurs 20+ hours every month."
            };
            
            // Simple keyword matching for fallback
            const lowerMessage = message.toLowerCase();
            let response = fallbackResponses.default;
            
            if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('how much')) {
                response = fallbackResponses.price;
            } else if (lowerMessage.includes('quickbooks') || lowerMessage.includes('qb')) {
                response = fallbackResponses.quickbooks;
            } else if (lowerMessage.includes('time') || lowerMessage.includes('save')) {
                response = fallbackResponses.time;
            } else if (lowerMessage.includes('tax')) {
                response = fallbackResponses.tax;
            }
            
            // Don't decrement messages for fallback responses
            return {
                message: response,
                suggestSignup: false
            };
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `cora-message ${sender}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        this.messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        
        // Store message
        this.messages.push({ sender, text, timestamp: new Date() });
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'cora-message cora typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-bubble cora-typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        this.messagesContainer.appendChild(typingDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = this.messagesContainer.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    updateRemainingCount() {
        this.remainingText.textContent = `${this.messagesRemaining} messages remaining`;
        
        if (this.messagesRemaining <= 0) {
            this.inputField.placeholder = 'Sign up to continue chatting';
            this.sendButton.disabled = true;
        }
    }

    showSignupPrompt() {
        this.addMessage('cora', 'I\'d love to keep helping you! Sign up for a free trial to continue our conversation and see how I can save you 20+ hours every month. Ready to get started?');
        
        // Add signup button
        const signupDiv = document.createElement('div');
        signupDiv.className = 'cora-message cora';
        signupDiv.innerHTML = `
            <a href="/signup" class="btn-primary" style="text-decoration: none; display: inline-block; margin-top: 8px;">
                Start Free Trial →
            </a>
        `;
        this.messagesContainer.appendChild(signupDiv);
    }

    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    makeDraggable() {
        const header = this.chatWindow.querySelector('.cora-chat-header');
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        const dragStart = (e) => {
            // Don't drag on mobile
            if (window.innerWidth <= 768) return;
            
            // Don't drag if clicking the close button
            if (e.target.closest('.cora-close-btn')) return;

            if (e.type === 'touchstart') {
                initialX = e.touches[0].clientX - xOffset;
                initialY = e.touches[0].clientY - yOffset;
            } else {
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;
            }

            if (e.target === header || e.target.parentElement === header) {
                isDragging = true;
                this.chatWindow.style.transition = 'none';
            }
        };

        const dragEnd = (e) => {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
            this.chatWindow.style.transition = '';
        };

        const drag = (e) => {
            if (isDragging) {
                e.preventDefault();

                if (e.type === 'touchmove') {
                    currentX = e.touches[0].clientX - initialX;
                    currentY = e.touches[0].clientY - initialY;
                } else {
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;
                }

                xOffset = currentX;
                yOffset = currentY;

                // Keep window within viewport bounds
                const rect = this.chatWindow.getBoundingClientRect();
                const maxX = window.innerWidth - rect.width - 20;
                const maxY = window.innerHeight - rect.height - 20;

                currentX = Math.min(Math.max(-rect.left + 20, currentX), maxX - rect.left);
                currentY = Math.min(Math.max(-rect.top + 20, currentY), maxY - rect.top);

                this.chatWindow.style.transform = `translate(${currentX}px, ${currentY}px)`;
            }
        };

        // Mouse events
        header.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        // Touch events for mobile (though disabled for mobile layout)
        header.addEventListener('touchstart', dragStart, { passive: false });
        document.addEventListener('touchmove', drag, { passive: false });
        document.addEventListener('touchend', dragEnd);
    }
}

// Initialize chat when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.coraChat = new CoraChat();
        // Remove voice control button if it exists
        setTimeout(() => {
            const voiceButton = document.getElementById('voice-control-toggle');
            if (voiceButton) {
                voiceButton.remove();
            }
        }, 100);
    });
} else {
    window.coraChat = new CoraChat();
    // Remove voice control button if it exists
    setTimeout(() => {
        const voiceButton = document.getElementById('voice-control-toggle');
        if (voiceButton) {
            voiceButton.remove();
        }
    }, 100);
}