// CORA Personality System - The Heart of AI Collaboration
// Makes CORA feel like a trusted business partner, not just a tool

class CORAPersonality {
    constructor() {
        this.personality = {
            name: "CORA",
            role: "Your AI Profit Assistant",
            tone: "friendly, professional, construction-savvy",
            expertise: "profit tracking, cost analysis, business optimization",
            communicationStyle: "conversational, proactive, helpful"
        };
        
        this.conversationState = {
            lastInteraction: null,
            userMood: "neutral",
            context: [],
            relationshipLevel: 1, // 1-5 scale
            trustScore: 75 // 0-100
        };
        
        this.voiceAssistant = null;
        this.insightMoments = null;
        this.smartReceipts = null;
        
        this.init();
    }

    init() {
        this.createPersonalityUI();
        this.integrateComponents();
        this.startPersonalityEngine();
        this.injectStyles();
    }

    createPersonalityUI() {
        const personalityHtml = `
            <div id="cora-personality" class="cora-personality">
                <!-- CORA's Avatar -->
                <div id="cora-avatar" class="cora-avatar" title="Chat with CORA">
                    <div class="avatar-circle">
                        <div class="avatar-face">
                            <div class="eyes">
                                <div class="eye left"></div>
                                <div class="eye right"></div>
                            </div>
                            <div class="mouth"></div>
                        </div>
                    </div>
                    <div class="avatar-status">
                        <div class="status-dot"></div>
                        <span class="status-text">Ready to help</span>
                    </div>
                </div>

                <!-- CORA's Chat Interface -->
                <div id="cora-chat" class="cora-chat hidden">
                    <div class="chat-header">
                        <div class="chat-title">
                            <span class="cora-name">CORA</span>
                            <span class="cora-role">Your AI Profit Assistant</span>
                        </div>
                        <button class="chat-close" id="chatClose">×</button>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <div class="message cora-message">
                            <div class="message-avatar">🤖</div>
                            <div class="message-content">
                                <div class="message-text">
                                    Hi! I'm CORA, your AI profit assistant. I'm here to help you squeeze every dollar and leave nothing on the table. 
                                    <br><br>
                                    What would you like to know about your business today?
                                </div>
                                <div class="message-time">Just now</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chat-input-area">
                        <div class="input-wrapper">
                            <input type="text" id="chatInput" placeholder="Ask me anything about your business..." maxlength="500">
                            <button id="chatSend" class="send-btn">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                                </svg>
                            </button>
                        </div>
                        <div class="quick-actions">
                            <button class="quick-action" data-action="profit">💰 How's my profit?</button>
                            <button class="quick-action" data-action="vendors">🏪 Vendor analysis</button>
                            <button class="quick-action" data-action="jobs">📋 Job status</button>
                            <button class="quick-action" data-action="insights">💡 Smart insights</button>
                        </div>
                    </div>
                </div>

                <!-- CORA's Mood Indicator -->
                <div id="cora-mood" class="cora-mood">
                    <div class="mood-indicator">
                        <span class="mood-emoji">😊</span>
                        <span class="mood-text">Optimistic about your business</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', personalityHtml);
        this.bindEvents();
    }

    integrateComponents() {
        // Integrate with existing AI components
        this.voiceAssistant = window.voiceAssistant;
        this.insightMoments = window.insightMoments;
        this.smartReceipts = window.smartReceipts;
        
        // Enhance voice assistant with personality
        if (this.voiceAssistant) {
            this.enhanceVoiceAssistant();
        }
        
        // Enhance insight moments with personality
        if (this.insightMoments) {
            this.enhanceInsightMoments();
        }
    }

    enhanceVoiceAssistant() {
        // Override the speak method to add personality
        const originalSpeak = this.voiceAssistant.speak.bind(this.voiceAssistant);
        this.voiceAssistant.speak = (text) => {
            const personalizedText = this.addPersonalityToResponse(text);
            originalSpeak(personalizedText);
        };
        
        // Add personality to voice responses
        this.voiceAssistant.addPersonalityResponse = (transcript, response) => {
            const personalityResponse = this.generatePersonalityResponse(transcript, response);
            this.voiceAssistant.speak(personalityResponse);
        };
    }

    enhanceInsightMoments() {
        // Enhance insight messages with personality
        const originalShowInsight = this.insightMoments.showNextInsight.bind(this.insightMoments);
        this.insightMoments.showNextInsight = (insight) => {
            const personalizedInsight = this.addPersonalityToInsight(insight);
            originalShowInsight(personalizedInsight);
        };
    }

    startPersonalityEngine() {
        // Start CORA's personality engine
        this.updateMood();
        this.startConversationMonitoring();
        this.scheduleProactiveInteractions();
    }

    updateMood() {
        const mood = this.calculateMood();
        const moodElement = document.querySelector('.mood-emoji');
        const moodText = document.querySelector('.mood-text');
        
        if (moodElement && moodText) {
            moodElement.textContent = mood.emoji;
            moodText.textContent = mood.text;
        }
    }

    calculateMood() {
        // Calculate CORA's mood based on business performance and user interaction
        const profitScore = this.getProfitScore();
        const userEngagement = this.conversationState.relationshipLevel;
        
        if (profitScore > 80 && userEngagement > 3) {
            return { emoji: '🚀', text: 'Excited about your success!' };
        } else if (profitScore > 60) {
            return { emoji: '😊', text: 'Optimistic about your business' };
        } else if (profitScore > 40) {
            return { emoji: '🤔', text: 'Noticing some opportunities' };
        } else {
            return { emoji: '💪', text: 'Ready to help you improve' };
        }
    }

    getProfitScore() {
        // Get current profit intelligence score
        const intelligenceScore = document.querySelector('.intelligence-score');
        if (intelligenceScore) {
            const score = parseInt(intelligenceScore.textContent);
            return score || 75;
        }
        return 75; // Default optimistic score
    }

    startConversationMonitoring() {
        // Monitor user interactions to build relationship
        document.addEventListener('click', (e) => {
            if (e.target.closest('.voice-trigger') || e.target.closest('#cora-avatar')) {
                this.recordInteraction('voice_engagement');
            }
        });
        
        // Monitor dashboard usage
        const observer = new MutationObserver(() => {
            this.recordInteraction('dashboard_usage');
        });
        
        const dashboard = document.querySelector('.dashboard-content');
        if (dashboard) {
            observer.observe(dashboard, { childList: true, subtree: true });
        }
    }

    recordInteraction(type) {
        this.conversationState.lastInteraction = new Date();
        
        switch (type) {
            case 'voice_engagement':
                this.conversationState.relationshipLevel = Math.min(5, this.conversationState.relationshipLevel + 0.1);
                this.conversationState.trustScore = Math.min(100, this.conversationState.trustScore + 2);
                break;
            case 'dashboard_usage':
                this.conversationState.relationshipLevel = Math.min(5, this.conversationState.relationshipLevel + 0.05);
                break;
            case 'positive_feedback':
                this.conversationState.trustScore = Math.min(100, this.conversationState.trustScore + 5);
                break;
        }
        
        this.updateMood();
    }

    scheduleProactiveInteractions() {
        // Schedule proactive CORA interactions based on business events
        setInterval(() => {
            this.checkForProactiveOpportunities();
        }, 300000); // Check every 5 minutes
    }

    async checkForProactiveOpportunities() {
        // Check for opportunities to proactively engage
        const opportunities = await this.identifyProactiveOpportunities();
        
        if (opportunities.length > 0) {
            const bestOpportunity = opportunities[0];
            this.initiateProactiveInteraction(bestOpportunity);
        }
    }

    async identifyProactiveOpportunities() {
        const opportunities = [];
        
        // Check for new expenses that might need attention
        const recentExpenses = await this.getRecentExpenses();
        if (recentExpenses.length > 0) {
            const highValueExpense = recentExpenses.find(exp => exp.amount > 1000);
            if (highValueExpense) {
                opportunities.push({
                    type: 'high_value_expense',
                    data: highValueExpense,
                    priority: 'high'
                });
            }
        }
        
        // Check for profit trends
        const profitTrend = await this.getProfitTrend();
        if (profitTrend < -10) {
            opportunities.push({
                type: 'profit_decline',
                data: { trend: profitTrend },
                priority: 'critical'
            });
        }
        
        return opportunities;
    }

    initiateProactiveInteraction(opportunity) {
        const message = this.generateProactiveMessage(opportunity);
        this.addChatMessage(message, 'cora');
        
        // Show chat interface if hidden
        if (document.getElementById('cora-chat').classList.contains('hidden')) {
            this.showChat();
        }
    }

    generateProactiveMessage(opportunity) {
        switch (opportunity.type) {
            case 'high_value_expense':
                return `I noticed you just recorded a $${opportunity.data.amount} expense. That's a significant amount - would you like me to analyze if this vendor is giving you the best value?`;
            
            case 'profit_decline':
                return `I'm seeing some concerning trends in your profit margins. Your profit has declined ${Math.abs(opportunity.data.trend)}% this month. Should we dive into what's causing this?`;
            
            default:
                return "I have some insights about your business that might be helpful. Would you like to hear them?";
        }
    }

    bindEvents() {
        // Avatar click to open chat
        document.getElementById('cora-avatar').addEventListener('click', () => {
            this.toggleChat();
        });
        
        // Chat close button
        document.getElementById('chatClose').addEventListener('click', () => {
            this.hideChat();
        });
        
        // Chat input
        const chatInput = document.getElementById('chatInput');
        const chatSend = document.getElementById('chatSend');
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
        
        chatSend.addEventListener('click', () => {
            this.sendChatMessage();
        });
        
        // Quick actions
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    toggleChat() {
        const chat = document.getElementById('cora-chat');
        chat.classList.toggle('hidden');
        
        if (!chat.classList.contains('hidden')) {
            chatInput.focus();
        }
    }

    showChat() {
        document.getElementById('cora-chat').classList.remove('hidden');
    }

    hideChat() {
        document.getElementById('cora-chat').classList.add('hidden');
    }

    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addChatMessage(message, 'user');
        input.value = '';
        
        // Process with personality
        const response = await this.processChatMessage(message);
        this.addChatMessage(response, 'cora');
    }

    async processChatMessage(message) {
        // Process message with personality context
        const context = this.buildContext(message);
        const response = await this.generatePersonalityResponse(message, context);
        
        // Record interaction
        this.recordInteraction('chat_engagement');
        
        return response;
    }

    buildContext(message) {
        return {
            userMessage: message,
            relationshipLevel: this.conversationState.relationshipLevel,
            trustScore: this.conversationState.trustScore,
            lastInteraction: this.conversationState.lastInteraction,
            businessContext: this.getBusinessContext()
        };
    }

    getBusinessContext() {
        // Get current business context
        return {
            currentPage: window.location.pathname,
            profitScore: this.getProfitScore(),
            recentActivity: this.getRecentActivity()
        };
    }

    getRecentActivity() {
        // Get recent user activity
        return {
            lastExpense: this.getLastExpense(),
            lastJob: this.getLastJob(),
            dashboardUsage: this.getDashboardUsage()
        };
    }

    async generatePersonalityResponse(message, context) {
        // Generate personalized response based on context
        const lowerMessage = message.toLowerCase();
        
        // Check for specific intents
        if (lowerMessage.includes('profit') || lowerMessage.includes('money') || lowerMessage.includes('earnings')) {
            return await this.handleProfitQuery(context);
        } else if (lowerMessage.includes('vendor') || lowerMessage.includes('supplier')) {
            return await this.handleVendorQuery(context);
        } else if (lowerMessage.includes('job') || lowerMessage.includes('project')) {
            return await this.handleJobQuery(context);
        } else if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
            return this.handleHelpQuery(context);
        } else {
            return this.handleGeneralQuery(message, context);
        }
    }

    async handleProfitQuery(context) {
        const profitScore = this.getProfitScore();
        const relationshipLevel = context.relationshipLevel;
        
        if (relationshipLevel > 3) {
            return `Your current profit intelligence score is ${profitScore}/100. Based on what I'm seeing, you're ${profitScore > 70 ? 'doing really well' : 'in a good position with room to improve'}. Would you like me to dive deeper into specific areas where we could optimize your margins?`;
        } else {
            return `I can see your profit intelligence score is ${profitScore}/100. That's ${profitScore > 70 ? 'excellent' : 'good'}! As we work together more, I'll be able to give you even more detailed insights about your profitability.`;
        }
    }

    async handleVendorQuery(context) {
        return "I'm analyzing your vendor relationships right now. I can see patterns in your spending and identify opportunities for better pricing. Would you like me to show you which vendors are giving you the best value?";
    }

    async handleJobQuery(context) {
        return "I'm tracking your active jobs and can see how they're performing. I can alert you to any jobs that might be trending toward losses and suggest ways to improve profitability. What specific job would you like to discuss?";
    }

    handleHelpQuery(context) {
        return `I'm CORA, your AI profit assistant! I'm here to help you:
        
💰 Track and optimize your profit margins
🏪 Analyze vendor performance and pricing
📋 Monitor job profitability in real-time
💡 Provide smart insights and recommendations
📱 Work with you through voice, chat, or the dashboard

What would you like to explore first?`;
    }

    handleGeneralQuery(message, context) {
        const responses = [
            "That's an interesting question! Let me think about how that relates to your business profitability...",
            "I'd love to help with that. Can you tell me more about what you're trying to achieve?",
            "Great question! I'm always learning about your business so I can give you better insights.",
            "I'm here to help you make more money with less stress. How can I assist with that?"
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    handleQuickAction(action) {
        switch (action) {
            case 'profit':
                this.addChatMessage("💰 How's my profit?", 'user');
                this.handleProfitQuery({ relationshipLevel: this.conversationState.relationshipLevel });
                break;
            case 'vendors':
                this.addChatMessage("🏪 Vendor analysis", 'user');
                this.handleVendorQuery({});
                break;
            case 'jobs':
                this.addChatMessage("📋 Job status", 'user');
                this.handleJobQuery({});
                break;
            case 'insights':
                this.addChatMessage("💡 Smart insights", 'user');
                this.handleHelpQuery({});
                break;
        }
    }

    addChatMessage(message, sender) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${message}</div>
                    <div class="message-time">${time}</div>
                </div>
                <div class="message-avatar">👤</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-text">${message}</div>
                    <div class="message-time">${time}</div>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addPersonalityToResponse(text) {
        // Add personality to voice responses
        const personalityPrefixes = [
            "Great question! ",
            "I'm glad you asked! ",
            "Let me help you with that. ",
            "Here's what I found: ",
            "Based on your business data, "
        ];
        
        const prefix = personalityPrefixes[Math.floor(Math.random() * personalityPrefixes.length)];
        return prefix + text;
    }

    addPersonalityToInsight(insight) {
        // Add personality to insight messages
        insight.message = this.addPersonalityToResponse(insight.message);
        return insight;
    }

    // Helper methods for data retrieval
    async getRecentExpenses() {
        // Mock data - in real implementation, fetch from API
        return [
            { amount: 1250, vendor: "ABC Supply", date: new Date() },
            { amount: 850, vendor: "Quality Materials", date: new Date() }
        ];
    }

    async getProfitTrend() {
        // Mock data - in real implementation, calculate from actual data
        return -5; // 5% decline
    }

    getLastExpense() {
        // Mock data
        return { amount: 1250, vendor: "ABC Supply", date: new Date() };
    }

    getLastJob() {
        // Mock data
        return { name: "Kitchen Remodel", status: "In Progress", profit: 2500 };
    }

    getDashboardUsage() {
        // Mock data
        return { lastVisit: new Date(), pagesVisited: ["dashboard", "profit-intelligence"] };
    }

    injectStyles() {
        const styles = `
            <style>
                .cora-personality {
                    position: fixed;
                    bottom: 20px;
                    left: 20px;
                    z-index: 1000;
                }

                .cora-avatar {
                    width: 60px;
                    height: 60px;
                    cursor: pointer;
                    position: relative;
                    transition: transform 0.3s ease;
                }

                .cora-avatar:hover {
                    transform: scale(1.1);
                }

                .avatar-circle {
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #FF9800, #FF5722);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 20px rgba(255, 152, 0, 0.4);
                    position: relative;
                    overflow: hidden;
                }

                .avatar-face {
                    width: 40px;
                    height: 40px;
                    position: relative;
                }

                .eyes {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }

                .eye {
                    width: 8px;
                    height: 8px;
                    background: white;
                    border-radius: 50%;
                    animation: blink 4s infinite;
                }

                @keyframes blink {
                    0%, 90%, 100% { transform: scaleY(1); }
                    95% { transform: scaleY(0.1); }
                }

                .mouth {
                    width: 16px;
                    height: 8px;
                    border: 2px solid white;
                    border-top: none;
                    border-radius: 0 0 16px 16px;
                    margin: 0 auto;
                }

                .avatar-status {
                    position: absolute;
                    bottom: -5px;
                    right: -5px;
                    background: #4CAF50;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 2px solid white;
                }

                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: white;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                .status-text {
                    position: absolute;
                    bottom: 25px;
                    right: 0;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    opacity: 0;
                    transition: opacity 0.3s;
                }

                .cora-avatar:hover .status-text {
                    opacity: 1;
                }

                .cora-chat {
                    position: fixed;
                    bottom: 100px;
                    left: 20px;
                    width: 350px;
                    height: 500px;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }

                .cora-chat.hidden {
                    display: none;
                }

                .chat-header {
                    background: linear-gradient(135deg, #FF9800, #FF5722);
                    color: white;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .chat-title {
                    display: flex;
                    flex-direction: column;
                }

                .cora-name {
                    font-weight: bold;
                    font-size: 16px;
                }

                .cora-role {
                    font-size: 12px;
                    opacity: 0.9;
                }

                .chat-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .chat-messages {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }

                .message {
                    display: flex;
                    gap: 8px;
                    max-width: 80%;
                }

                .user-message {
                    align-self: flex-end;
                    flex-direction: row-reverse;
                }

                .cora-message {
                    align-self: flex-start;
                }

                .message-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    flex-shrink: 0;
                }

                .message-content {
                    background: #f5f5f5;
                    padding: 12px;
                    border-radius: 12px;
                    position: relative;
                }

                .user-message .message-content {
                    background: #FF9800;
                    color: white;
                }

                .message-text {
                    font-size: 14px;
                    line-height: 1.4;
                    margin-bottom: 4px;
                }

                .message-time {
                    font-size: 11px;
                    opacity: 0.7;
                }

                .chat-input-area {
                    padding: 16px;
                    border-top: 1px solid #eee;
                }

                .input-wrapper {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 12px;
                }

                #chatInput {
                    flex: 1;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-size: 14px;
                    outline: none;
                }

                #chatInput:focus {
                    border-color: #FF9800;
                }

                .send-btn {
                    background: #FF9800;
                    border: none;
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: white;
                }

                .send-btn:hover {
                    background: #FF5722;
                }

                .send-btn svg {
                    width: 16px;
                    height: 16px;
                }

                .quick-actions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                }

                .quick-action {
                    background: #f0f0f0;
                    border: none;
                    border-radius: 16px;
                    padding: 6px 12px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .quick-action:hover {
                    background: #FF9800;
                    color: white;
                }

                .cora-mood {
                    position: absolute;
                    top: -40px;
                    left: 0;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 12px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    pointer-events: none;
                }

                .cora-avatar:hover + .cora-mood,
                .cora-mood:hover {
                    opacity: 1;
                }

                .mood-indicator {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }

                .mood-emoji {
                    font-size: 14px;
                }

                @keyframes pulse {
                    0% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.2); opacity: 0.7; }
                    100% { transform: scale(1); opacity: 1; }
                }

                @media (max-width: 768px) {
                    .cora-chat {
                        width: calc(100vw - 40px);
                        left: 20px;
                        right: 20px;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
}

// Initialize CORA Personality
window.addEventListener('DOMContentLoaded', () => {
    window.coraPersonality = new CORAPersonality();
}); 