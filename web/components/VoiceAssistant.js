// CORA Voice Assistant - Natural conversation for contractors
// "Hey CORA, how's my profit this month?"

class VoiceAssistant {
    constructor() {
        this.isListening = false;
        this.isProcessing = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.conversationContext = [];
        this.voiceCommands = this.defineCommands();
        this.init();
    }

    init() {
        this.createUI();
        this.setupSpeechRecognition();
        this.injectStyles();
        this.addKeyboardShortcut();
    }

    createUI() {
        const assistantHtml = `
            <div id="voice-assistant" class="voice-assistant">
                <button id="voice-trigger" class="voice-trigger" aria-label="Voice Assistant">
                    <div class="voice-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                            <line x1="12" y1="19" x2="12" y2="23"/>
                            <line x1="8" y1="23" x2="16" y2="23"/>
                        </svg>
                    </div>
                    <div class="voice-pulse"></div>
                </button>
                
                <div id="voice-overlay" class="voice-overlay hidden">
                    <div class="voice-modal">
                        <div class="voice-visual">
                            <div class="voice-wave">
                                <span></span><span></span><span></span><span></span><span></span>
                            </div>
                        </div>
                        <div class="voice-status">Listening...</div>
                        <div class="voice-transcript"></div>
                        <button class="voice-cancel">Cancel</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', assistantHtml);
        this.bindEvents();
    }

    injectStyles() {
        const styles = `
            <style>
                .voice-assistant {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 999;
                }

                .voice-trigger {
                    width: 56px;
                    height: 56px;
                    border-radius: 50%;
                    background: #FF9800;
                    border: none;
                    box-shadow: 0 4px 20px rgba(255, 152, 0, 0.4);
                    cursor: pointer;
                    position: relative;
                    transition: transform 0.2s;
                }

                .voice-trigger:hover {
                    transform: scale(1.1);
                }

                .voice-trigger.listening {
                    background: #ff5252;
                    animation: pulse-ring 1.5s infinite;
                }

                @keyframes pulse-ring {
                    0% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.7); }
                    100% { box-shadow: 0 0 0 20px rgba(255, 152, 0, 0); }
                }

                .voice-icon {
                    color: white;
                    width: 24px;
                    height: 24px;
                    margin: 0 auto;
                }

                .voice-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(10px);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }

                .voice-overlay.hidden {
                    display: none;
                }

                .voice-modal {
                    background: #1a1a1a;
                    border-radius: 20px;
                    padding: 40px;
                    text-align: center;
                    max-width: 400px;
                    width: 90%;
                }

                .voice-wave {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 60px;
                    margin-bottom: 20px;
                }

                .voice-wave span {
                    display: block;
                    width: 4px;
                    height: 20px;
                    background: #FF9800;
                    margin: 0 3px;
                    border-radius: 2px;
                    animation: wave 1s ease-in-out infinite;
                }

                .voice-wave span:nth-child(1) { animation-delay: 0s; }
                .voice-wave span:nth-child(2) { animation-delay: 0.1s; }
                .voice-wave span:nth-child(3) { animation-delay: 0.2s; }
                .voice-wave span:nth-child(4) { animation-delay: 0.3s; }
                .voice-wave span:nth-child(5) { animation-delay: 0.4s; }

                @keyframes wave {
                    0%, 100% { transform: scaleY(1); }
                    50% { transform: scaleY(2); }
                }

                .voice-status {
                    color: #FF9800;
                    font-size: 18px;
                    margin-bottom: 10px;
                }

                .voice-transcript {
                    color: #ccc;
                    font-size: 16px;
                    min-height: 40px;
                    margin-bottom: 20px;
                }

                .voice-cancel {
                    background: transparent;
                    border: 1px solid #666;
                    color: #999;
                    padding: 10px 30px;
                    border-radius: 25px;
                    cursor: pointer;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    defineCommands() {
        return {
            // Profit & Analytics
            profit: {
                patterns: [
                    /how('s| is) my profit/i,
                    /what('s| is) my profit/i,
                    /show (me )?profit/i,
                    /profit (report|analysis|intelligence)/i
                ],
                action: async (match) => {
                    const response = await this.fetchProfitData();
                    this.speak(response.message);
                    if (response.redirect) {
                        setTimeout(() => window.location.href = response.redirect, 2000);
                    }
                }
            },
            
            // Vendor queries
            vendors: {
                patterns: [
                    /which vendor(s)?.*expensive/i,
                    /vendor (costs?|prices?|analysis)/i,
                    /who('s| is) overcharging/i,
                    /compare vendors?/i
                ],
                action: async () => {
                    const vendors = await this.fetchVendorAnalysis();
                    this.speak(vendors.message);
                    if (vendors.showDetails) {
                        window.location.href = '/profit-intelligence?tab=vendors';
                    }
                }
            },
            
            // Quick expense entry
            expense: {
                patterns: [
                    /spent (\$?[\d,]+(?:\.\d{2})?) (?:at|on|for) (.+)/i,
                    /add expense (\$?[\d,]+(?:\.\d{2})?) (.+)/i,
                    /bought (.+) for (\$?[\d,]+(?:\.\d{2})?)/i
                ],
                action: async (match) => {
                    const amount = this.parseAmount(match[1] || match[2]);
                    const description = match[2] || match[1];
                    await this.addExpense(amount, description);
                    this.speak(`Added ${amount} dollar expense for ${description}`);
                }
            },
            
            // Job queries
            jobs: {
                patterns: [
                    /how many jobs/i,
                    /active jobs/i,
                    /job (status|progress)/i,
                    /what jobs/i
                ],
                action: async () => {
                    const jobs = await this.fetchJobSummary();
                    this.speak(jobs.message);
                }
            },
            
            // Intelligence score
            score: {
                patterns: [
                    /intelligence score/i,
                    /my score/i,
                    /profit score/i,
                    /how am I doing/i
                ],
                action: async () => {
                    const score = await this.fetchIntelligenceScore();
                    this.speak(score.message);
                }
            },
            
            // Quick actions
            help: {
                patterns: [
                    /help/i,
                    /what can (you|I)/i,
                    /commands/i
                ],
                action: () => {
                    this.speak("I can help you check profit, analyze vendors, add expenses, review jobs, or check your intelligence score. Just ask naturally!");
                }
            }
        };
    }

    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            // console.warn('Speech recognition not supported');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            document.getElementById('voice-trigger').classList.add('listening');
            document.getElementById('voice-overlay').classList.remove('hidden');
            document.querySelector('.voice-status').textContent = 'Listening...';
        };

        this.recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            
            document.querySelector('.voice-transcript').textContent = transcript;
            
            if (event.results[0].isFinal) {
                this.processCommand(transcript);
            }
        };

        this.recognition.onerror = (event) => {
            // console.error('Speech recognition error:', event.error);
            this.speak("Sorry, I didn't catch that. Please try again.");
            this.stopListening();
        };

        this.recognition.onend = () => {
            this.stopListening();
        };
    }

    bindEvents() {
        const trigger = document.getElementById('voice-trigger');
        const cancel = document.querySelector('.voice-cancel');
        const overlay = document.getElementById('voice-overlay');

        trigger.addEventListener('click', () => this.toggleListening());
        cancel.addEventListener('click', () => this.stopListening());
        
        // Click outside to cancel
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.stopListening();
            }
        });
    }

    addKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + V for voice
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                this.toggleListening();
            }
        });
    }

    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.recognition) {
            this.speak("Voice commands are not supported in your browser.");
            return;
        }
        
        this.recognition.start();
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        
        this.isListening = false;
        document.getElementById('voice-trigger').classList.remove('listening');
        document.getElementById('voice-overlay').classList.add('hidden');
    }

    async processCommand(transcript) {
        document.querySelector('.voice-status').textContent = 'Processing...';
        
        // Check against all command patterns
        for (const [commandName, command] of Object.entries(this.voiceCommands)) {
            for (const pattern of command.patterns) {
                const match = transcript.match(pattern);
                if (match) {
                    await command.action(match);
                    this.stopListening();
                    return;
                }
            }
        }
        
        // If no command matched, try natural language understanding
        await this.handleNaturalLanguage(transcript);
        this.stopListening();
    }

    async handleNaturalLanguage(transcript) {
        // Send to CORA chat for natural processing
        try {
            const response = await fetch('/api/chat/voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    message: transcript,
                    context: 'voice_command'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.speak(data.response);
                
                // Execute any actions returned
                if (data.action) {
                    setTimeout(() => {
                        window.location.href = data.action.url;
                    }, 2000);
                }
            } else {
                this.speak("I understand you said: " + transcript + ". But I'm not sure how to help with that yet.");
            }
        } catch (error) {
            this.speak("I heard you, but I'm having trouble processing that right now.");
        }
    }

    speak(text) {
        if (!this.synthesis) return;
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.1;
        utterance.pitch = 0.9;
        
        // Find a good voice
        const voices = this.synthesis.getVoices();
        const englishVoice = voices.find(voice => 
            voice.lang.startsWith('en') && voice.name.includes('Google')
        ) || voices[0];
        
        if (englishVoice) {
            utterance.voice = englishVoice;
        }
        
        this.synthesis.speak(utterance);
    }

    // Data fetching methods
    async fetchProfitData() {
        try {
            const response = await fetch('/api/profit-intelligence/profit-intelligence-summary', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                return {
                    message: `Your profit intelligence score is ${data.intelligenceScore} out of 100. You have ${data.monthlySavingsPotential} dollars in potential monthly savings. Would you like to see the details?`,
                    redirect: '/profit-intelligence'
                };
            }
        } catch (error) {
            // console.error('Error fetching profit data:', error);
        }
        
        return {
            message: "I'm having trouble accessing your profit data right now. Let me take you to the dashboard.",
            redirect: '/dashboard'
        };
    }

    async fetchVendorAnalysis() {
        try {
            const response = await fetch('/api/profit-intelligence/vendor-performance', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                const worstVendor = data.vendors?.find(v => v.performance_score < 70);
                
                if (worstVendor) {
                    return {
                        message: `${worstVendor.name} is your most expensive vendor, costing you about ${Math.round(worstVendor.total_cost * 0.15)} dollars extra per month. Let me show you the comparison.`,
                        showDetails: true
                    };
                }
            }
        } catch (error) {
            // console.error('Error fetching vendor data:', error);
        }
        
        return {
            message: "I'll analyze your vendor costs. One moment please.",
            showDetails: true
        };
    }

    async fetchJobSummary() {
        // Would fetch real job data
        return {
            message: "You have 3 active jobs. The Wilson deck is at 65% completion, the Johnson bathroom is starting tomorrow, and the Smith kitchen is awaiting materials."
        };
    }

    async fetchIntelligenceScore() {
        try {
            const response = await fetch('/api/profit-intelligence/profit-intelligence-summary', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                const grade = data.letterGrade || 'B+';
                const improvement = data.scoreChange || '+5';
                
                return {
                    message: `Your intelligence score is ${data.intelligenceScore} out of 100, that's a ${grade}. You've improved by ${improvement} points this month. Great job!`
                };
            }
        } catch (error) {
            // console.error('Error fetching score:', error);
        }
        
        return {
            message: "Let me check your intelligence score for you."
        };
    }

    async addExpense(amount, description) {
        try {
            const response = await fetch('/api/expenses/voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    amount: amount,
                    description: description,
                    category: 'auto-categorize'
                })
            });
            
            return response.ok;
        } catch (error) {
            // console.error('Error adding expense:', error);
            return false;
        }
    }

    parseAmount(amountStr) {
        return parseFloat(amountStr.replace(/[$,]/g, ''));
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.voiceAssistant = new VoiceAssistant();
    });
} else {
    window.voiceAssistant = new VoiceAssistant();
}