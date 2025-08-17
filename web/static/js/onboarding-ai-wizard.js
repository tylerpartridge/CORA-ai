/**
 * AI-Powered Onboarding Wizard
 * CORA is alive and dynamic, not scripted
 */

class AIOnboardingWizard {
    constructor() {
        this.conversationId = `onboarding_${Date.now()}`;
        this.userData = {
            rawConversation: [],
            extractedData: {}
        };
        this.currentPhase = 'greeting';
        this.messageArea = document.getElementById('messageArea');
        this.inputArea = document.getElementById('inputArea');
        this.isProcessing = false;
        this.emailInputShown = false; // Flag to prevent duplicate email inputs
        this.autoScrollEnabled = true;
        this.nearBottomThreshold = 60; // px from bottom counts as "near"
        this.jumpToLatestButton = null;
        this.scrollSentinel = null;
        
        // Progress tracking
        // Align progress steps with linear phases used by the wizard
        this.progressSteps = [
            'greeting',
            'business_discovery',
            'years_experience',
            'business_size',
            'service_area',
            'customer_type',
            'current_tracking',
            'busy_season',
            'main_challenge',
            'business_goal',
            'completion'
        ];
        this.currentStepIndex = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupScrollAnchoring();
        // Start fresh unless explicitly resuming via URL param
        this.startConversation();
    }

    setupScrollAnchoring() {
        const area = this.messageArea;
        if (!area) return;

        // Simple scroll tracking
        area.addEventListener('scroll', () => {
            const isNear = this.isNearBottom();
            this.autoScrollEnabled = isNear;
            this.toggleJumpToLatest(!isNear);
        }, { passive: true });
        
        // Start with auto-scroll enabled
        this.autoScrollEnabled = true;
    }

    // Removed ensureSentinelAtEnd - not needed

    isNearBottom() {
        const area = this.messageArea;
        if (!area) return true;
        const distance = area.scrollHeight - area.scrollTop - area.clientHeight;
        return distance <= this.nearBottomThreshold;
    }

    toggleJumpToLatest(show) {
        if (!this.jumpToLatestButton) {
            const btn = document.createElement('button');
            btn.className = 'jump-to-latest';
            btn.type = 'button';
            btn.textContent = 'Jump to latest';
            btn.addEventListener('click', () => {
                this.autoScrollEnabled = true;
                this.scrollToBottom(true);
                this.toggleJumpToLatest(false);
            });
            document.body.appendChild(btn);
            this.jumpToLatestButton = btn;
        }
        this.jumpToLatestButton.style.display = show ? 'flex' : 'none';
    }

    scrollToBottomIfAppropriate() {
        if (this.autoScrollEnabled || this.isNearBottom()) {
            // Small delay to let content render
            requestAnimationFrame(() => {
                this.scrollToBottom();
            });
        }
    }
    
    setupEventListeners() {
        // Text input
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (userInput) {
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.isProcessing) {
                    this.handleTextInput();
                }
            });
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                if (!this.isProcessing) {
                    this.handleTextInput();
                }
            });
        }
        
        // Skip link
        const skipLink = document.getElementById('skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('Skip getting to know CORA? You can always chat with her later.')) {
                    window.location.href = '/dashboard';
                }
            });
        }
    }
    
    async startConversation() {
        // Always clear old progress unless explicitly resuming
        const params = new URLSearchParams(window.location.search);
        const shouldResume = params.get('resume') === '1';
        
        if (!shouldResume) {
            // Clear ALL onboarding data for fresh start
            try { 
                localStorage.removeItem('onboardingProgress');
                localStorage.removeItem('coraUserData');
            } catch (e) {}
        } else if (this.resumeFromProgress()) {
            return; // Resumed intentionally
        }

        // Fresh start from greeting
        this.currentPhase = 'greeting';
        this.currentStepIndex = 0;
        this.userData = {
            rawConversation: [],
            extractedData: {}
        };
        this.updatePhase();
        this.updateProgressUI();
    }
    
    async sendToAI(userMessage, context = {}) {
        // DISABLED - Using linear flow only to prevent duplicates
        return;
        this.isProcessing = true;
        
        // Add user message to conversation
        if (userMessage) {
            this.userData.rawConversation.push({
                role: 'user',
                content: userMessage
            });
        }
        
        // Show typing indicator
        this.showTyping();
        
        // Debug logging
        // console.log('🔍 DEBUG: Sending to AI with message:', userMessage);
        // console.log('🔍 DEBUG: Context:', context);
        // console.log('🔍 DEBUG: Current phase:', this.currentPhase);
        
        try {
            const response = await fetch('/api/cora-chat-v2/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    conversation_id: this.conversationId,
                    metadata: {
                        onboarding: true,
                        phase: this.currentPhase,
                        ...context,
                        instructions: this.getPhaseInstructions(),
                        collectedData: this.userData.extractedData
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Debug logging
            // console.log('🔍 DEBUG: Received AI response:', data);
            // console.log('🔍 DEBUG: AI message:', data.message);
            
            // Add CORA's response to conversation
            this.userData.rawConversation.push({
                role: 'assistant',
                content: data.message
            });
            
            // Extract data from conversation FIRST
            this.extractDataFromConversation();
            
            // Update phase based on what we've collected
            // But don't update if this is the first message (greeting)
            if (userMessage || this.currentPhase !== 'greeting') {
                this.updatePhase();
            }
            
            // Process and display response (with updated phase)
            this.hideTyping();
            await this.processAIResponse(data.message);
            
        } catch (error) {
            // console.error('AI communication error:', error);
            this.hideTyping();
            this.showMessage("Hmm, my connection hiccuped. Let's try that again!", 'cora');
        }
        
        this.isProcessing = false;
    }
    
    async processAIResponse(message) {
        // console.log('🚨 DEBUG: processAIResponse called');
        // console.log('🚨 DEBUG: AI message:', message);
        // console.log('🚨 DEBUG: Current phase:', this.currentPhase);
        // console.log('🚨 DEBUG: Extracted data:', this.userData.extractedData);
        
        // Look for special patterns in CORA's response that indicate UI needs
        const patterns = {
            businessTypes: /\[business_types\]/i,
            yearsInBusiness: /\[years_in_business\]/i,
            businessSizes: /\[business_sizes\]/i,
            serviceAreas: /\[service_areas\]/i,
            customerTypes: /\[customer_types\]/i,
            trackingMethods: /\[tracking_methods\]/i,
            painPoints: /\[pain_points\]/i,
            busySeasons: /\[busy_seasons\]/i,
            businessGoals: /\[business_goals\]/i,
            completeOnboarding: /\[complete_onboarding\]/i
        };
        
        // Clean message of any control patterns
        let displayMessage = message;
        // Remove control tags
        displayMessage = displayMessage.replace(/\[business_types\]/gi, '');
        displayMessage = displayMessage.replace(/\[years_in_business\]/gi, '');
        displayMessage = displayMessage.replace(/\[business_sizes\]/gi, '');
        displayMessage = displayMessage.replace(/\[service_areas\]/gi, '');
        displayMessage = displayMessage.replace(/\[customer_types\]/gi, '');
        displayMessage = displayMessage.replace(/\[tracking_methods\]/gi, '');
        displayMessage = displayMessage.replace(/\[pain_points\]/gi, '');
        displayMessage = displayMessage.replace(/\[busy_seasons\]/gi, '');
        displayMessage = displayMessage.replace(/\[business_goals\]/gi, '');
        displayMessage = displayMessage.replace(/\[complete_onboarding\]/gi, '');
        
        // Show CORA's message
        this.showMessage(displayMessage, 'cora');
        
        // Debug: Check what patterns are in the message
        // console.log('🚨 DEBUG: Checking for patterns in message');
        for (const [patternName, pattern] of Object.entries(patterns)) {
            if (pattern.test(message)) {
                // console.log(`🚨 DEBUG: Found pattern: ${patternName}`);
            }
        }
        
        // Check if we need special UI elements
        if (patterns.completeOnboarding.test(message)) {
            // Show completion button instead of auto-completing
            this.currentPhase = 'completion';
            this.showCompletionButton();
        } else if (patterns.businessTypes.test(message)) {
            // console.log('🔍 DEBUG: Detected business_types tag, current phase:', this.currentPhase);
            // Only show business types if we're actually in the business_discovery phase
            if (this.currentPhase === 'business_discovery') {
                await this.showBusinessTypeOptions();
            } else {
                // console.log('🔍 DEBUG: Ignoring business_types tag in wrong phase');
                // Show appropriate UI for current phase
                await this.autoShowPhaseUI();
            }
        } else if (patterns.yearsInBusiness.test(message)) {
            // console.log('🔍 DEBUG: Detected years_in_business tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'years_experience') {
                await this.showYearsInBusinessOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.businessSizes.test(message)) {
            // console.log('🔍 DEBUG: Detected business_sizes tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'business_size') {
                await this.showBusinessSizeOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.serviceAreas.test(message)) {
            // console.log('🔍 DEBUG: Detected service_areas tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'service_area') {
                await this.showServiceAreaOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.customerTypes.test(message)) {
            // console.log('🔍 DEBUG: Detected customer_types tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'customer_type') {
                await this.showCustomerTypeOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.trackingMethods.test(message)) {
            // console.log('🔍 DEBUG: Detected tracking_methods tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'current_tracking') {
                await this.showTrackingMethodOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.painPoints.test(message)) {
            // console.log('🔍 DEBUG: Detected pain_points tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'main_challenge') {
                await this.showPainPointOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.busySeasons.test(message)) {
            // console.log('🔍 DEBUG: Detected busy_seasons tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'busy_season') {
                await this.showBusySeasonOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else if (patterns.businessGoals.test(message)) {
            // console.log('🔍 DEBUG: Detected business_goals tag, current phase:', this.currentPhase);
            if (this.currentPhase === 'business_goal') {
                await this.showBusinessGoalOptions();
            } else {
                await this.autoShowPhaseUI();
            }
        } else {
            // Auto-show appropriate UI based on current phase (fallback)
            // console.log('🔍 DEBUG: No specific tag detected, auto-showing UI for phase:', this.currentPhase);
            // Only auto-show UI if we're past the greeting phase
            // Greeting phase should just show text input by default
            if (this.currentPhase !== 'greeting') {
                await this.autoShowPhaseUI();
            } else {
                // For greeting phase, ensure text input is shown
                this.showTextInput('What should I call you?');
            }
        }
    }
    
    async autoShowPhaseUI() {
        // Auto-show appropriate UI based on current phase if AI doesn't send tags
        // console.log('Auto-showing UI for phase:', this.currentPhase);
        
        switch(this.currentPhase) {
            case 'greeting':
                // console.log('Greeting phase - showing text input for name');
                this.showTextInput('What should I call you?');
                break;
            case 'business_discovery':
                // console.log('Showing business type options');
                await this.showBusinessTypeOptions();
                break;
            case 'years_experience':
                // console.log('Showing years in business options');
                await this.showYearsInBusinessOptions();
                break;
            case 'business_size':
                // console.log('Showing business size options');
                await this.showBusinessSizeOptions();
                break;
            case 'service_area':
                // console.log('Showing service area options');
                await this.showServiceAreaOptions();
                break;
            case 'customer_type':
                // console.log('Showing customer type options');
                await this.showCustomerTypeOptions();
                break;
            case 'current_tracking':
                // console.log('Showing tracking method options');
                await this.showTrackingMethodOptions();
                break;
            case 'main_challenge':
                // console.log('Showing pain point options');
                await this.showPainPointOptions();
                break;
            case 'busy_season':
                // console.log('Showing busy season options');
                await this.showBusySeasonOptions();
                break;
            case 'business_goal':
                // console.log('Showing business goal options');
                await this.showBusinessGoalOptions();
                break;
            case 'completion':
                // console.log('Completion phase - showing completion button');
                this.showCompletionButton();
                break;
            default:
                // console.log('Unknown phase, showing text input:', this.currentPhase);
                this.showTextInput();
                break;
        }
    }
    
    showMessage(text, sender = 'cora') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message ${sender === 'cora' ? 'primary' : ''}`;
        messageDiv.textContent = text;
        
        // Fade older messages
        this.messageArea.querySelectorAll('.cora-message, .user-message').forEach(msg => {
            msg.classList.remove('primary');
        });
        
        this.messageArea.appendChild(messageDiv);
        // Delay scroll to let DOM settle
        requestAnimationFrame(() => {
            this.scrollToBottomIfAppropriate();
        });
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        this.messageArea.appendChild(typingDiv);
        requestAnimationFrame(() => {
            this.scrollToBottomIfAppropriate();
        });
    }
    
    hideTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    }
    
    showTextInput(placeholder = 'Type your answer...') {
        // Hide other inputs
        const choices = document.getElementById('choicesContainer') || document.getElementById('choiceCardsContainer');
        if (choices) choices.style.display = 'none';
        const multi = document.getElementById('multiSelectInfo');
        if (multi) multi.style.display = 'none';
        
        // Show text input
        const textContainer = document.getElementById('textInputContainer');
        textContainer.style.display = 'flex';
        
        const input = document.getElementById('userInput');
        input.value = '';
        input.type = 'text'; // Reset to text type
        input.placeholder = placeholder;
        input.focus();

        // Update spacing and scroll after DOM settles
        requestAnimationFrame(() => {
            this.updateBottomSpace();
            this.scrollToBottom(true);
        });
    }
    
    showEmailInput() {
        // console.log('🔍 DEBUG: showEmailInput called, current email:', this.userData.extractedData.email);
        // console.log('🔍 DEBUG: emailInputShown flag:', this.emailInputShown);
        
        // Don't show email input if we already have an email OR if already shown
        if (this.userData.extractedData.email) {
            // console.log('🔍 DEBUG: Email already exists, not showing email input again');
            return;
        }
        
        if (this.emailInputShown) {
            // console.log('🔍 DEBUG: Email input already shown, preventing duplicate');
            return;
        }
        
        this.emailInputShown = true;
        // console.log('🔍 DEBUG: Showing email input for the first time');
        
        // Hide other inputs
        document.getElementById('choicesContainer').style.display = 'none';
        document.getElementById('multiSelectInfo').style.display = 'none';
        
        // Show text input configured for email
        const textContainer = document.getElementById('textInputContainer');
        textContainer.style.display = 'flex';
        
        const input = document.getElementById('userInput');
        input.value = '';
        input.type = 'email';
        input.placeholder = 'your@email.com';
        input.focus();

        requestAnimationFrame(() => {
            this.updateBottomSpace();
            this.scrollToBottom(true);
        });
    }
    
    showPasswordInput() {
        // Hide other inputs
        const choicesContainer = document.getElementById('choiceCardsContainer');
        if (choicesContainer) choicesContainer.style.display = 'none';
        const multiSelectInfo = document.getElementById('multiSelectInfo');
        if (multiSelectInfo) multiSelectInfo.style.display = 'none';
        
        // Show text input configured for password
        const textContainer = document.getElementById('textInputContainer');
        textContainer.style.display = 'flex';
        
        const input = document.getElementById('userInput');
        input.value = '';
        input.type = 'password';
        input.placeholder = 'Create a secure password...';
        input.focus();

        requestAnimationFrame(() => {
            this.updateBottomSpace();
            this.scrollToBottom(true);
        });
    }
    
    showCompletionButton() {
        // Hide all inputs
        document.getElementById('textInputContainer').style.display = 'none';
        document.getElementById('choicesContainer').style.display = 'none';
        document.getElementById('multiSelectInfo').style.display = 'none';
        
        // Show a completion button
        const completionHtml = `
            <div style="text-align: center; margin-top: 30px;">
                <button id="completeOnboardingBtn" style="
                    background: var(--cora-blue);
                    color: white;
                    border: none;
                    padding: 16px 40px;
                    font-size: 18px;
                    border-radius: 30px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                ">Complete Setup & Go to Dashboard</button>
            </div>
        `;
        
        this.inputArea.innerHTML = completionHtml;
        
        document.getElementById('completeOnboardingBtn').addEventListener('click', () => {
            this.completeOnboarding();
        });
    }
    
    async showBusinessTypeOptions() {
        const options = [
            { emoji: '🏗️', title: 'General Contractor', desc: 'I manage multiple trades', value: 'general' },
            { emoji: '🔧', title: 'Plumbing', desc: 'Water, pipes, fixtures', value: 'plumbing' },
            { emoji: '⚡', title: 'Electrical', desc: 'Wiring, panels, lighting', value: 'electrical' },
            { emoji: '❄️', title: 'HVAC', desc: 'Heating & cooling systems', value: 'hvac' },
            { emoji: '🏠', title: 'Remodeling', desc: 'Kitchens, baths, additions', value: 'remodeling' },
            { emoji: '🪜', title: 'Roofing', desc: 'Shingles, repairs, gutters', value: 'roofing' },
            { emoji: '🧱', title: 'Concrete', desc: 'Foundations, driveways, slabs', value: 'concrete' },
            { emoji: '🎨', title: 'Painting', desc: 'Interior & exterior', value: 'painting' },
            { emoji: '🪵', title: 'Framing', desc: 'Rough carpentry, structures', value: 'framing' }
        ];
        
        // Allow multi-select for business types since contractors often do multiple
        this.showChoiceOptions(options, true);
    }
    
    async showYearsInBusinessOptions() {
        // console.log('🔍 DEBUG: showYearsInBusinessOptions called');
        const options = [
            { emoji: '🌱', title: 'Just Starting', desc: 'Less than 1 year', value: 'new' },
            { emoji: '🌿', title: 'Getting Established', desc: '1-3 years', value: 'establishing' },
            { emoji: '🌳', title: 'Experienced', desc: '4-10 years', value: 'experienced' },
            { emoji: '🏛️', title: 'Industry Veteran', desc: 'Over 10 years', value: 'veteran' }
        ];
        
        // console.log('🔍 DEBUG: Calling showChoiceOptions with options:', options);
        this.showChoiceOptions(options, false);
    }
    
    async showBusinessSizeOptions() {
        const options = [
            { emoji: '👤', title: 'Just Me', desc: 'Solo contractor', value: 'solo' },
            { emoji: '👥', title: 'Small Crew', desc: '2-5 people', value: 'small_crew' },
            { emoji: '🏢', title: 'Growing Company', desc: '6-10 people', value: 'growing' },
            { emoji: '🏗️', title: 'Established Company', desc: '10+ people', value: 'established' }
        ];
        
        this.showChoiceOptions(options, false);
    }
    
    async showServiceAreaOptions() {
        const options = [
            { emoji: '🏘️', title: 'Local Only', desc: 'Within 40 km', value: 'local' },
            { emoji: '🗺️', title: 'Regional', desc: 'Multiple cities', value: 'regional' },
            { emoji: '📍', title: 'Province-wide', desc: 'Entire province', value: 'statewide' },
            { emoji: '🌎', title: 'Multi-Province', desc: 'Several provinces', value: 'multistate' }
        ];
        
        this.showChoiceOptions(options, false);
    }
    
    async showCustomerTypeOptions() {
        const options = [
            { emoji: '🏠', title: 'Homeowners', desc: 'Residential work', value: 'residential' },
            { emoji: '🏢', title: 'Businesses', desc: 'Commercial work', value: 'commercial' },
            { emoji: '🏭', title: 'Industrial', desc: 'Factories & plants', value: 'industrial' },
            { emoji: '🏛️', title: 'Government', desc: 'Municipal & provincial', value: 'government' }
        ];
        
        // Multi-select - many contractors work with multiple customer types
        this.showChoiceOptions(options, true);
    }
    
    async showTrackingMethodOptions() {
        const options = [
            { emoji: '📝', title: 'Paper & Folders', desc: 'Old school filing', value: 'paper' },
            { emoji: '📊', title: 'Spreadsheets', desc: 'Excel or Google Sheets', value: 'spreadsheets' },
            { emoji: '💻', title: 'QuickBooks', desc: 'Or similar software', value: 'quickbooks' },
            { emoji: '🤷', title: 'Wing It', desc: 'No real system', value: 'none' }
        ];
        
        // Multi-select - contractors often use multiple tracking methods
        this.showChoiceOptions(options, true);
    }
    
    async showBusySeasonOptions() {
        const options = [
            { emoji: '🌸', title: 'Spring', desc: 'March - May', value: 'spring' },
            { emoji: '☀️', title: 'Summer', desc: 'June - August', value: 'summer' },
            { emoji: '🍂', title: 'Fall', desc: 'September - November', value: 'fall' },
            { emoji: '❄️', title: 'Winter', desc: 'December - February', value: 'winter' }
        ];
        
        this.showChoiceOptions(options, true); // Allow multiple for busy seasons
    }
    
    async showBusinessGoalOptions() {
        const options = [
            { emoji: '📈', title: 'Grow Revenue', desc: 'More jobs & income', value: 'grow_revenue' },
            { emoji: '💰', title: 'Increase Profits', desc: 'Better margins', value: 'increase_profits' },
            { emoji: '👥', title: 'Hire & Expand', desc: 'Build my team', value: 'expand_team' },
            { emoji: '⚖️', title: 'Work-Life Balance', desc: 'Less stress, more life', value: 'balance' }
        ];
        
        this.showChoiceOptions(options, true);
    }
    
    async showPainPointOptions() {
        const options = [
            { emoji: '📊', title: "Can't track profits", desc: 'Never sure if I made money', value: 'profit_tracking' },
            { emoji: '📝', title: 'Paperwork chaos', desc: 'Drowning in receipts', value: 'paperwork' },
            { emoji: '💰', title: 'Missing tax deductions', desc: 'Leaving money on table', value: 'taxes' },
            { emoji: '⏰', title: 'No time for books', desc: 'Too busy working', value: 'time' },
            { emoji: '💸', title: 'Cash flow issues', desc: "Don't know who owes me", value: 'cashflow' },
            { emoji: '📱', title: 'Too many apps', desc: 'Nothing talks to each other', value: 'tools' }
        ];
        
        // Multi-select - contractors often have multiple pain points
        this.showChoiceOptions(options, true);
    }
    
    
    showChoiceOptions(options, allowMultiple = false) {
        // console.log('🔍 DEBUG: showChoiceOptions called with options:', options, 'allowMultiple:', allowMultiple);
        
        // Hide text input
        document.getElementById('textInputContainer').style.display = 'none';
        
        // Show choices
        const container = document.getElementById('choicesContainer');
        container.innerHTML = '';
        container.style.display = 'grid';
        container.style.position = 'relative';
        
        // Set grid layout based on number of options
        if (options.length <= 4) {
            container.className = 'choices-container grid-2';
        } else if (options.length <= 6) {
            container.className = 'choices-container grid-3';
        } else {
            container.className = 'choices-container grid-3';
        }
        
        options.forEach(option => {
            const choiceDiv = document.createElement('div');
            choiceDiv.className = 'choice-option';
            choiceDiv.dataset.value = option.value;
            choiceDiv.innerHTML = `
                <span class="choice-emoji">${option.emoji}</span>
                <div class="choice-text">
                    <div class="choice-title">${option.title}</div>
                    ${option.desc ? `<div class="choice-desc">${option.desc}</div>` : ''}
                </div>
            `;
            
            choiceDiv.addEventListener('click', () => {
                // console.log('🔍 DEBUG: Choice clicked:', option.title, 'value:', option.value);
                if (allowMultiple) {
                    choiceDiv.classList.toggle('selected');
                    this.updateMultiSelectButton();
                } else {
                    // Single select - auto advance
                    container.querySelectorAll('.choice-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    choiceDiv.classList.add('selected');
                    
                    // console.log('🔍 DEBUG: Single select - calling handleChoiceSelection in 300ms');
                    setTimeout(() => {
                        // console.log('🔍 DEBUG: Executing handleChoiceSelection now');
                        this.handleChoiceSelection([{
                            value: option.value,
                            title: option.title,
                            amount: option.amount || null
                        }]);
                    }, 300);
                }
            });
            
            container.appendChild(choiceDiv);
        });
        
        // Show multi-select controls if needed
        if (allowMultiple) {
            const multiInfo = document.getElementById('multiSelectInfo');
            multiInfo.style.display = 'flex';
            
            // Update the span text to be clearer
            const infoSpan = multiInfo.querySelector('span');
            if (infoSpan) {
                infoSpan.textContent = 'Select all that apply';
            }
            
            const continueBtn = document.getElementById('continueChoices');
            continueBtn.disabled = true;
            
            // Remove any existing listeners first
            const newBtn = continueBtn.cloneNode(true);
            continueBtn.parentNode.replaceChild(newBtn, continueBtn);
            
            // Add fresh listener
            newBtn.addEventListener('click', () => {
                const selected = this.getSelectedChoices();
                if (selected.length > 0) {
                    this.handleChoiceSelection(selected);
                }
            });
            
            // Update reference
            this.updateMultiSelectButton();
        } else {
            // Hide multi-select info for single select
            const multiInfo = document.getElementById('multiSelectInfo');
            multiInfo.style.display = 'none';
        }

        // After choices render, update space and scroll once DOM settles
        requestAnimationFrame(() => {
            this.updateBottomSpace();
            this.scrollToBottom(true);
        });
    }
    
    updateMultiSelectButton() {
        const selected = document.querySelectorAll('.choice-option.selected');
        const continueBtn = document.getElementById('continueChoices');
        if (continueBtn) {
            continueBtn.disabled = selected.length === 0;
        }
    }
    
    getSelectedChoices() {
        const selected = [];
        document.querySelectorAll('.choice-option.selected').forEach(opt => {
            selected.push({
                value: opt.dataset.value,
                title: opt.querySelector('.choice-title').textContent
            });
        });
        return selected;
    }
    
    async handleChoiceSelection(choices) {
        // console.log('🔍 DEBUG: handleChoiceSelection called with choices:', choices);
        // console.log('🔍 DEBUG: Current phase:', this.currentPhase);
        // console.log('🔍 DEBUG: Current extracted data:', this.userData.extractedData);
        
        // Hide choice UI
        document.getElementById('choicesContainer').style.display = 'none';
        document.getElementById('multiSelectInfo').style.display = 'none';
        
        // Store data based on choice value (more reliable than phase)
        // console.log('🔍 DEBUG: Storing choice data. Current phase:', this.currentPhase);
        // console.log('🔍 DEBUG: Choice value:', choices[0]?.value, 'Choice title:', choices[0]?.title);
        
        if (choices.length === 1) {
            // Check what type of choice this is based on the choice value
            const choiceValue = choices[0].value;
            
            if (choiceValue === 'new' || choiceValue === 'establishing' || choiceValue === 'experienced' || choiceValue === 'veteran') {
                // This is a years in business choice
                this.userData.extractedData.yearsInBusiness = choiceValue;
                // console.log('🔍 DEBUG: Set yearsInBusiness to:', choiceValue);
            } else if (choiceValue === 'solo' || choiceValue === 'small_crew' || choiceValue === 'growing' || choiceValue === 'established') {
                // This is a business size choice
                this.userData.extractedData.businessSize = choiceValue;
                // console.log('🔍 DEBUG: Set businessSize to:', choiceValue);
            } else if (choiceValue === 'local' || choiceValue === 'regional' || choiceValue === 'statewide' || choiceValue === 'multistate') {
                // This is a service area choice
                this.userData.extractedData.serviceArea = choiceValue;
                // console.log('🔍 DEBUG: Set serviceArea to:', choiceValue);
            } else if (choiceValue === 'residential' || choiceValue === 'commercial' || choiceValue === 'industrial' || choiceValue === 'government') {
                // This is a customer type choice
                this.userData.extractedData.customerType = [choiceValue];
                // console.log('🔍 DEBUG: Set customerType to:', [choiceValue]);
            } else if (choiceValue === 'paper' || choiceValue === 'spreadsheets' || choiceValue === 'quickbooks' || choiceValue === 'none') {
                // This is a tracking method choice
                this.userData.extractedData.trackingMethod = [choiceValue];
                // console.log('🔍 DEBUG: Set trackingMethod to:', [choiceValue]);
            } else if (choiceValue === 'profit_tracking' || choiceValue === 'paperwork' || choiceValue === 'taxes' || choiceValue === 'time' || choiceValue === 'cashflow' || choiceValue === 'tools') {
                // This is a main challenge choice
                this.userData.extractedData.mainChallenge = [choiceValue];
                // console.log('🔍 DEBUG: Set mainChallenge to:', [choiceValue]);
            } else if (choiceValue === 'grow_revenue' || choiceValue === 'increase_profits' || choiceValue === 'expand_team' || choiceValue === 'balance') {
                // This is a business goal choice
                this.userData.extractedData.businessGoal = [choiceValue];
                // console.log('🔍 DEBUG: Set businessGoal to:', [choiceValue]);
            } else if (choiceValue === 'spring' || choiceValue === 'summer' || choiceValue === 'fall' || choiceValue === 'winter') {
                // This is a busy season choice
                this.userData.extractedData.busySeason = choiceValue;
                // console.log('🔍 DEBUG: Set busySeason to:', choiceValue);
            } else if (choiceValue === 'general' || choiceValue === 'plumbing' || choiceValue === 'electrical' || choiceValue === 'hvac' || choiceValue === 'remodeling' || choiceValue === 'roofing' || choiceValue === 'concrete' || choiceValue === 'painting' || choiceValue === 'framing') {
                // This is a business type choice
                this.userData.extractedData.businessType = [choiceValue];
                // console.log('🔍 DEBUG: Set businessType to:', [choiceValue]);
            } else {
                // console.log('🔍 DEBUG: Unknown choice value:', choiceValue);
            }
        } else if (choices.length > 1) {
            // Handle multi-select fields
            const choiceValues = choices.map(c => c.value);
            
            if (choiceValues.some(v => ['general', 'plumbing', 'electrical', 'hvac', 'remodeling', 'roofing', 'concrete', 'painting', 'framing'].includes(v))) {
                // This is a business type multi-select
                this.userData.extractedData.businessType = choiceValues;
                // console.log('🔍 DEBUG: Set businessType to:', choiceValues);
            } else if (choiceValues.some(v => ['residential', 'commercial', 'industrial', 'government'].includes(v))) {
                // This is a customer type multi-select
                this.userData.extractedData.customerType = choiceValues;
                // console.log('🔍 DEBUG: Set customerType to:', choiceValues);
            } else if (choiceValues.some(v => ['paper', 'spreadsheets', 'quickbooks', 'none'].includes(v))) {
                // This is a tracking method multi-select
                this.userData.extractedData.trackingMethod = choiceValues;
                // console.log('🔍 DEBUG: Set trackingMethod to:', choiceValues);
            } else if (choiceValues.some(v => ['profit_tracking', 'paperwork', 'taxes', 'time', 'cashflow', 'tools'].includes(v))) {
                // This is a main challenge multi-select
                this.userData.extractedData.mainChallenge = choiceValues;
                // console.log('🔍 DEBUG: Set mainChallenge to:', choiceValues);
            } else if (choiceValues.some(v => ['spring', 'summer', 'fall', 'winter'].includes(v))) {
                // This is a busy season multi-select
                this.userData.extractedData.busySeason = choiceValues;
                // console.log('🔍 DEBUG: Set busySeason to:', choiceValues);
            } else if (choiceValues.some(v => ['grow_revenue', 'increase_profits', 'expand_team', 'balance'].includes(v))) {
                // This is a business goal multi-select
                this.userData.extractedData.businessGoal = choiceValues;
                // console.log('🔍 DEBUG: Set businessGoal to:', choiceValues);
            } else {
                // console.log('🔍 DEBUG: Unknown multi-select values:', choiceValues);
            }
        }
        
        // Build natural message from choices
        let message;
        if (choices.length === 1) {
            message = choices[0].title;
        } else {
            const titles = choices.map(c => c.title);
            message = titles.slice(0, -1).join(', ') + ' and ' + titles[titles.length - 1];
        }
        
        // Show as user message
        this.showMessage(message, 'user');
        
        // Advance to the NEXT phase after a selection to avoid repeating the same question
        this.advanceToNextPhase();
    }
    
    async handleTextInput() {
        const input = document.getElementById('userInput');
        const message = input.value.trim();
        if (!message) return;

        // Show user message immediately
        this.showMessage(message, 'user');

        // Clear input
        input.value = '';

        // Capture answer for the current phase without complex validation
        this.captureAnswerForCurrentPhase(message);

        // Send to AI (non-blocking for phase advancement)
        try {
            await this.sendToAI(message);
        } catch (e) {
            // Swallow errors here; flow should remain linear
        }

        // ALWAYS advance to the next phase after user input
        this.advanceToNextPhase();
    }

    captureAnswerForCurrentPhase(answer) {
        const data = this.userData.extractedData;
        switch (this.currentPhase) {
            case 'greeting':
                if (!data.name) data.name = answer;
                break;
            case 'business_discovery':
                data.businessType = Array.isArray(data.businessType) ? data.businessType : [];
                if (!data.businessType.length) data.businessType = [answer];
                break;
            case 'years_experience':
                data.yearsInBusiness = answer;
                break;
            case 'business_size':
                data.businessSize = answer;
                break;
            case 'service_area':
                data.serviceArea = answer;
                break;
            case 'customer_type':
                data.customerType = Array.isArray(data.customerType) ? data.customerType : [];
                if (!data.customerType.length) data.customerType = [answer];
                break;
            case 'current_tracking':
                data.trackingMethod = Array.isArray(data.trackingMethod) ? data.trackingMethod : [];
                if (!data.trackingMethod.length) data.trackingMethod = [answer];
                break;
            case 'busy_season':
                data.busySeason = answer;
                break;
            case 'main_challenge':
                data.mainChallenge = Array.isArray(data.mainChallenge) ? data.mainChallenge : [];
                if (!data.mainChallenge.length) data.mainChallenge = [answer];
                break;
            case 'business_goal':
                data.businessGoal = Array.isArray(data.businessGoal) ? data.businessGoal : [];
                if (!data.businessGoal.length) data.businessGoal = [answer];
                break;
            default:
                break;
        }
    }

    advanceToNextPhase() {
        const phases = [
            'greeting',
            'business_discovery',
            'years_experience',
            'business_size',
            'service_area',
            'customer_type',
            'current_tracking',
            'busy_season',
            'main_challenge',
            'business_goal',
            'completion'
        ];

        const currentIndex = phases.indexOf(this.currentPhase);
        if (currentIndex < phases.length - 1) {
            this.currentPhase = phases[currentIndex + 1];
        }

        // Handle completion phase
        if (this.currentPhase === 'completion') {
            // Complete onboarding for already authenticated user
            this.completeOnboarding();
        }

        this.updatePhase();
    }
    
    extractDataFromConversation() {
        // Smart extraction from natural conversation
        const conversation = this.userData.rawConversation;
        const lastMessages = conversation.slice(-4); // Last 2 exchanges
        
        // Look for patterns in recent messages
        lastMessages.forEach(msg => {
            // ONLY extract data from USER messages, not AI messages
            if (msg.role !== 'user') {
                return;
            }
            
            const content = msg.content.toLowerCase();
            
            // Name extraction (more flexible)
            if (!this.userData.extractedData.name && this.currentPhase === 'greeting') {
                const namePatterns = [
                    /(?:i'm|im|i am|name is|call me)\s+([a-z]+)/i,
                    /^([a-z]+)$/i, // Just a single word as first response
                    /^(?:hi|hey|hello),?\s*([a-z]+)/i
                ];
                
                for (const pattern of namePatterns) {
                    const match = msg.content.match(pattern);
                    if (match) {
                        this.userData.extractedData.name = match[1];
                        // console.log('🚨 DEBUG: Extracted name:', match[1], 'from message:', msg.content);
                        break;
                    }
                }
            }
            
            // Store business type when mentioned
            if (this.currentPhase === 'business_discovery' && msg.role === 'user') {
                // Business type will be stored by handleChoiceSelection
            }
        });
    }
    
    updatePhase() {
        // Strictly linear phase UI with one clear question per phase
        const currentProgress = document.getElementById('progress-text');
        const phases = [
            'greeting', 'business_discovery', 'years_experience', 'business_size',
            'service_area', 'customer_type', 'current_tracking', 'busy_season',
            'main_challenge', 'business_goal', 'completion'
        ];

        switch (this.currentPhase) {
            case 'greeting':
                currentProgress.textContent = 'Getting to know you...';
                this.showMessage('What should I call you?', 'cora');
                this.showTextInput('What should I call you?');
                break;
            case 'business_discovery':
                currentProgress.textContent = 'Nice to meet you!';
                this.showMessage('What type of construction work do you do?', 'cora');
                this.showBusinessTypeOptions();
                break;
            case 'years_experience':
                currentProgress.textContent = 'Learning about your experience...';
                this.showMessage('How many years have you been in business?', 'cora');
                this.showYearsInBusinessOptions();
                break;
            case 'business_size':
                currentProgress.textContent = 'Understanding your business...';
                this.showMessage('What is your business size?', 'cora');
                this.showBusinessSizeOptions();
                break;
            case 'service_area':
                currentProgress.textContent = 'Getting to know your market...';
                this.showMessage('Where do you typically work?', 'cora');
                this.showServiceAreaOptions();
                break;
            case 'customer_type':
                currentProgress.textContent = 'Learning about your customers...';
                this.showMessage('Who are your typical customers?', 'cora');
                this.showCustomerTypeOptions();
                break;
            case 'current_tracking':
                currentProgress.textContent = 'Understanding your systems...';
                this.showMessage('How do you currently track your business?', 'cora');
                this.showTrackingMethodOptions();
                break;
            case 'busy_season':
                currentProgress.textContent = 'Just a few more questions...';
                this.showMessage('When are you the busiest?', 'cora');
                this.showBusySeasonOptions();
                break;
            case 'main_challenge':
                currentProgress.textContent = 'Understanding your challenges...';
                this.showMessage('What is your biggest challenge right now?', 'cora');
                this.showPainPointOptions();
                break;
            case 'business_goal':
                currentProgress.textContent = 'Almost there...';
                this.showMessage('What is your primary business goal?', 'cora');
                this.showBusinessGoalOptions();
                break;
            case 'completion':
                currentProgress.textContent = 'All set!';
                this.showCompletionButton();
                break;
            default:
                break;
        }

        // Update progress bar and persist
        const currentIndex = phases.indexOf(this.currentPhase);
        const progress = ((currentIndex + 1) / phases.length) * 100;
        const fill = document.querySelector('.progress-fill');
        if (fill) fill.style.width = `${progress}%`;
        this.updateProgress();
    }
    
    getPhaseInstructions() {
        const instructions = {
            greeting: "Get their name naturally. Be warm and conversational, not formal.",
            business_discovery: "Find out what type of contractor they are. Allow multiple selections.",
            years_experience: "Learn how long they've been in business.",
            business_size: "Get their business size - solo, small crew, or larger company.",
            service_area: "Understand their geographic coverage.",
            customer_type: "Learn about their typical customers.",
            current_tracking: "Find out how they currently manage their business.",
            main_challenge: "Understand their biggest pain point with business management.",
            busy_season: "Learn when they're busiest - can be multiple seasons.",
            business_goal: "Understand their primary goal for growth.",
            completion: "Wrap up positively and transition to dashboard."
        };
        
        return instructions[this.currentPhase] || "";
    }
    
    scrollToBottom(force = false) {
        const area = this.messageArea;
        if (!area) return;
        if (!force && !this.autoScrollEnabled) return;
        
        // Scroll to bottom with a small delay to ensure content is rendered
        setTimeout(() => {
            area.scrollTop = area.scrollHeight;
        }, 10);
    }

    updateBottomSpace() {
        // With the new layout, we don't need dynamic padding
        // The flex layout handles the spacing automatically
        const area = this.messageArea;
        if (!area) return;
        
        // Just ensure scroll position is maintained
        if (this.autoScrollEnabled) {
            this.scrollToBottom();
        }
    }
    
    estimateRevenueRange() {
        // Estimate monthly revenue based on business size and experience
        const size = this.userData.extractedData.businessSize;
        const experience = this.userData.extractedData.yearsInBusiness;
        
        if (size === 'solo') {
            if (experience === 'new') return '$0-$10,000';
            if (experience === 'establishing') return '$5,000-$20,000';
            if (experience === 'experienced') return '$10,000-$40,000';
            if (experience === 'veteran') return '$20,000-$60,000';
            return '$10,000-$30,000';
        } else if (size === 'small_crew') {
            if (experience === 'new') return '$10,000-$50,000';
            if (experience === 'establishing') return '$20,000-$80,000';
            if (experience === 'experienced') return '$40,000-$150,000';
            if (experience === 'veteran') return '$60,000-$250,000';
            return '$30,000-$100,000';
        } else if (size === 'growing') {
            return '$80,000-$400,000';
        } else if (size === 'established') {
            return '$200,000-$1,000,000+';
        }
        
        return '$10,000-$100,000'; // Default fallback
    }
    
    async completeOnboarding() {
        // Save business profile data for already authenticated user
        try {
            // console.log('🔍 DEBUG: Starting onboarding completion...');
            // console.log('🔍 DEBUG: User data:', this.userData.extractedData);
            
            // Save to localStorage for dashboard access
            localStorage.setItem('coraUserData', JSON.stringify(this.userData.extractedData));
            
            // Prepare business profile data for API
            const businessProfileData = {
                businessName: `${this.userData.extractedData.name}'s ${(this.userData.extractedData.businessType || ['Construction'])[0]} Business`,
                businessType: (this.userData.extractedData.businessType || ['general']).join(', '),
                industry: 'Construction',
                monthlyRevenueRange: this.estimateRevenueRange(),
                onboardingData: {
                    name: this.userData.extractedData.name,
                    yearsInBusiness: this.userData.extractedData.yearsInBusiness,
                    businessSize: this.userData.extractedData.businessSize,
                    serviceArea: this.userData.extractedData.serviceArea,
                    customerType: this.userData.extractedData.customerType,
                    trackingMethod: this.userData.extractedData.trackingMethod,
                    mainChallenge: this.userData.extractedData.mainChallenge,
                    busySeason: this.userData.extractedData.busySeason,
                    businessGoal: this.userData.extractedData.businessGoal
                }
            };
            
            // Save the business profile data to the user's account
            console.log('Saving business profile:', businessProfileData);
            const profileResponse = await fetch('/api/onboarding/create-business-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',  // Include cookies with auth token
                body: JSON.stringify(businessProfileData)
            });
            
            if (!profileResponse.ok) {
                console.error('Failed to save business profile:', profileResponse.status, await profileResponse.text());
            } else {
                console.log('Business profile saved successfully!');
                const result = await profileResponse.json();
                console.log('Server response:', result);
            }
            
            // Show success message
            this.showMessage("🎉 All set! I've saved your business profile.", 'cora');
            this.showMessage("Let me redirect you to your personalized dashboard...", 'cora');
            
            // Add countdown timer
            let countdown = 3;
            const countdownInterval = setInterval(() => {
                if (countdown > 0) {
                    document.getElementById('progress-text').textContent = `Redirecting in ${countdown}...`;
                    countdown--;
                } else {
                    clearInterval(countdownInterval);
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                }
            }, 1000);
            
        } catch (error) {
            console.error('Failed to complete onboarding:', error);
            this.showMessage("Something went wrong. Let me try again...", 'cora');
            
            // Fallback: Still redirect to dashboard after delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 3000);
        }
    }
    
    async createBusinessProfile(accessToken) {
        try {
            // console.log('🔍 DEBUG: Creating business profile...');
            
            const businessProfileData = {
                businessName: `${this.userData.extractedData.name}'s ${(this.userData.extractedData.businessType || ['Construction'])[0]} Business`,
                businessType: (this.userData.extractedData.businessType || ['general']).join(', '),
                industry: 'Construction',
                monthlyRevenueRange: this.estimateRevenueRange(),
                userEmail: this.userData.extractedData.email,
                onboardingData: {
                    yearsInBusiness: this.userData.extractedData.yearsInBusiness,
                    businessSize: this.userData.extractedData.businessSize,
                    serviceArea: this.userData.extractedData.serviceArea,
                    customerType: this.userData.extractedData.customerType,
                    trackingMethod: this.userData.extractedData.trackingMethod,
                    mainChallenge: this.userData.extractedData.mainChallenge,
                    busySeason: this.userData.extractedData.busySeason,
                    businessGoal: this.userData.extractedData.businessGoal
                }
            };
            
            // console.log('🔍 DEBUG: Business profile data:', businessProfileData);
            
            // Use the onboarding-specific endpoint that doesn't require authentication
            const profileResponse = await fetch('/api/onboarding/create-business-profile-onboarding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(businessProfileData)
            });
            
            // console.log('🔍 DEBUG: Business profile response status:', profileResponse.status);
            
            if (profileResponse.ok) {
                const profileResult = await profileResponse.json();
                // console.log('🔍 DEBUG: Business profile created successfully:', profileResult);
            } else {
                const errorData = await profileResponse.json();
                // console.error('🔍 DEBUG: Business profile creation failed:', errorData);
                // Don't fail the entire flow if profile creation fails
            }
            
        } catch (error) {
            // console.error('Failed to create business profile:', error);
            // Continue anyway - profile can be created later
        }
    }
    
    async saveOnboardingCompletion() {
        try {
            // console.log('🔍 DEBUG: Saving onboarding completion...');
            
            const completionData = {
                userData: {
                    ...this.userData.extractedData,
                    fullConversation: this.userData.rawConversation
                },
                completedAt: new Date().toISOString()
            };
            
            // console.log('🔍 DEBUG: Completion data:', completionData);
            
            const completionResponse = await fetch('/api/onboarding/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(completionData)
            });
            
            // console.log('🔍 DEBUG: Completion response status:', completionResponse.status);
            
            if (completionResponse.ok) {
                const completionResult = await completionResponse.json();
                // console.log('🔍 DEBUG: Onboarding completion saved:', completionResult);
            } else {
                const errorData = await completionResponse.json();
                // console.error('🔍 DEBUG: Onboarding completion failed:', errorData);
                // Don't fail the entire flow if completion save fails
            }
            
        } catch (error) {
            // console.error('Failed to save onboarding completion:', error);
            // Continue anyway - completion can be saved later
        }
    }
    
    showCompletionMessage() {
        // Clear any old completion progress to prevent "All set!" on reload
        try {
            localStorage.removeItem('onboardingProgress');
        } catch (e) {}
        
        // Hide all inputs
        document.getElementById('textInputContainer').style.display = 'none';
        document.getElementById('choicesContainer').style.display = 'none';
        document.getElementById('multiSelectInfo').style.display = 'none';
        
        // Update progress text
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.textContent = 'Account created successfully!';
        }
        
        // Show success message in the message area
        this.showMessage(`Perfect! Your account is all set up, ${this.userData.extractedData.name || 'there'}!`, 'cora');
        this.showMessage('Taking you to your personalized dashboard...', 'cora');
        
        // Create completion display with auto-redirect
        const completionHtml = `
            <div class="completion-container" style="text-align: center; margin-top: 40px;">
                <div style="font-size: 48px; margin-bottom: 20px; animation: pulse 1.5s infinite;">🎉</div>
                <h2 style="color: var(--accent-orange); font-size: 28px; margin-bottom: 20px;">
                    Welcome to CORA!
                </h2>
                
                <div style="color: var(--text-secondary); font-size: 16px; margin-bottom: 20px;">
                    Redirecting to your dashboard in <span id="countdown">3</span> seconds...
                </div>
                
                <button id="continueBtn" class="continue-to-dashboard" style="
                    background: var(--accent-orange);
                    color: var(--bg-primary);
                    border: none;
                    padding: 14px 32px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 25px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                ">
                    Go to Dashboard Now →
                </button>
            </div>
        `;
        
        // Add completion to input area
        this.inputArea.innerHTML = completionHtml;
        
        // Add immediate click handler
        const continueBtn = document.getElementById('continueBtn');
        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                window.location.href = '/dashboard';
            });
        }
        
        // Auto-redirect with countdown
        let countdown = 3;
        const countdownEl = document.getElementById('countdown');
        const countdownInterval = setInterval(() => {
            countdown--;
            if (countdownEl) {
                countdownEl.textContent = countdown;
            }
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                window.location.href = '/dashboard';
            }
        }, 1000);
    }
    
    // Progress tracking methods
    updateProgress() {
        this.currentStepIndex = this.progressSteps.indexOf(this.currentPhase);
        this.saveProgress(this.currentPhase);
        this.updateProgressUI();
    }
    
    saveProgress(phase) {
        const progress = {
            phase: phase,
            stepIndex: this.progressSteps.indexOf(phase),
            timestamp: new Date().toISOString(),
            userData: this.userData.extractedData
        };
        
        localStorage.setItem('onboardingProgress', JSON.stringify(progress));
        // console.log('Progress saved:', progress);
    }
    
    loadProgress() {
        const savedProgress = localStorage.getItem('onboardingProgress');
        if (savedProgress) {
            try {
                const progress = JSON.parse(savedProgress);
                this.currentPhase = progress.phase;
                this.currentStepIndex = progress.stepIndex;
                
                // Restore user data if available
                if (progress.userData) {
                    this.userData.extractedData = { ...this.userData.extractedData, ...progress.userData };
                }
                
                // console.log('Progress loaded:', progress);
            } catch (error) {
                // console.error('Error loading progress:', error);
            }
        }
    }
    
    updateProgressUI() {
        // Create or update progress bar
        let progressBar = document.getElementById('onboardingProgressBar');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.id = 'onboardingProgressBar';
            progressBar.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: rgba(255,152,0,0.2);
                z-index: 10000;
            `;
            
            const progressFill = document.createElement('div');
            progressFill.id = 'onboardingProgressFill';
            progressFill.style.cssText = `
                height: 100%;
                background: linear-gradient(90deg, #FF9800, #F57C00);
                transition: width 0.5s ease;
                width: 0%;
            `;
            
            progressBar.appendChild(progressFill);
            document.body.appendChild(progressBar);
        }
        
        // Update progress percentage
        const progressPercentage = ((this.currentStepIndex + 1) / this.progressSteps.length) * 100;
        const progressFill = document.getElementById('onboardingProgressFill');
        if (progressFill) {
            progressFill.style.width = `${progressPercentage}%`;
        }
        
        // Update step indicator
        this.updateStepIndicator();
    }
    
    updateStepIndicator() {
        let stepIndicator = document.getElementById('onboardingStepIndicator');
        if (!stepIndicator) {
            stepIndicator = document.createElement('div');
            stepIndicator.id = 'onboardingStepIndicator';
            stepIndicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(26,26,26,0.9);
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                z-index: 10000;
                border: 1px solid rgba(255,152,0,0.3);
            `;
            document.body.appendChild(stepIndicator);
        }
        
        const currentStep = this.currentStepIndex + 1;
        const totalSteps = this.progressSteps.length;
        stepIndicator.textContent = `Step ${currentStep} of ${totalSteps}`;
    }
    
    resumeFromProgress() {
        const savedProgress = localStorage.getItem('onboardingProgress');
        if (savedProgress) {
            try {
                const progress = JSON.parse(savedProgress);
                if (progress.phase && progress.phase !== 'completion') {
                    // Resume from saved phase
                    this.currentPhase = progress.phase;
                    this.currentStepIndex = progress.stepIndex;
                    
                    // Restore user data
                    if (progress.userData) {
                        this.userData.extractedData = { ...this.userData.extractedData, ...progress.userData };
                    }
                    
                    // Show resume message
                    this.showMessage("Welcome back! Let's continue where we left off.", 'cora');
                    
                    // Continue from current phase
                    this.autoShowPhaseUI();
                    return true;
                }
            } catch (error) {
                // console.error('Error resuming progress:', error);
            }
        }
        return false;
    }
}

// Initialize when ready
document.addEventListener('DOMContentLoaded', () => {
    new AIOnboardingWizard();
});