/**
 * CORA Voice Command Help System
 * Provides interactive guidance for voice expense entry
 */

class VoiceHelp {
    constructor() {
        this.examples = [
            {
                text: "Home Depot receipt fifty seven dollars",
                category: "materials",
                description: "Simple receipt with amount"
            },
            {
                text: "Lumber yard Johnson bathroom job hundred twenty",
                category: "materials",
                description: "Receipt with job name"
            },
            {
                text: "Gas station fill up thirty five bucks",
                category: "equipment",
                description: "Fuel expense"
            },
            {
                text: "Subcontractor Mike electrical work kitchen remodel two thousand",
                category: "subcontractor",
                description: "Subcontractor payment"
            },
            {
                text: "Equipment rental excavator daily rate three hundred fifty",
                category: "equipment",
                description: "Equipment rental"
            },
            {
                text: "Labor overtime weekend work bathroom job four hundred",
                category: "labor",
                description: "Labor expense with job"
            }
        ];
        
        this.tips = [
            "Speak clearly and at a normal pace",
            "Include the vendor name first",
            "Mention the amount clearly",
            "Add the job name if applicable",
            "Use natural language - don't worry about perfect grammar"
        ];
        
        this.init();
    }
    
    init() {
        this.createHelpButton();
        this.addHelpStyles();
    }
    
    createHelpButton() {
        // Create help button next to voice button
        const voiceContainer = document.querySelector('.voice-button-container');
        if (voiceContainer) {
            const helpButton = document.createElement('button');
            helpButton.className = 'voice-help-btn';
            helpButton.innerHTML = '❓';
            helpButton.title = 'Voice Command Help';
            helpButton.onclick = () => this.showHelp();
            
            voiceContainer.appendChild(helpButton);
        }
    }
    
    showHelp() {
        const modal = this.createHelpModal();
        document.body.appendChild(modal);
        
        // Add animation
        setTimeout(() => {
            modal.classList.add('open');
        }, 10);
    }
    
    createHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'voice-help-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="voiceHelp.close()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>🎤 Voice Command Help</h3>
                    <button class="close-btn" onclick="voiceHelp.close()">×</button>
                </div>
                <div class="modal-body">
                    <div class="help-section">
                        <h4>💡 Quick Tips</h4>
                        <ul class="tips-list">
                            ${this.tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="help-section">
                        <h4>📝 Example Commands</h4>
                        <div class="examples-grid">
                            ${this.examples.map(example => `
                                <div class="example-card" onclick="voiceHelp.tryExample('${example.text}')">
                                    <div class="example-text">"${example.text}"</div>
                                    <div class="example-category">${example.category}</div>
                                    <div class="example-description">${example.description}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="help-section">
                        <h4>🎯 Practice Mode</h4>
                        <div class="practice-section">
                            <p>Try saying one of the examples above, or practice with your own command:</p>
                            <div class="practice-input">
                                <input type="text" id="practice-input" placeholder="Type or speak your command here...">
                                <button onclick="voiceHelp.practiceCommand()">Try It</button>
                            </div>
                            <div class="practice-feedback" id="practice-feedback"></div>
                        </div>
                    </div>
                    
                    <div class="help-section">
                        <h4>🔧 Troubleshooting</h4>
                        <div class="troubleshooting">
                            <div class="trouble-item">
                                <strong>Not recognizing amounts?</strong>
                                <p>Try saying numbers clearly: "fifty dollars" instead of "50 bucks"</p>
                            </div>
                            <div class="trouble-item">
                                <strong>Wrong vendor detected?</strong>
                                <p>Say the vendor name first: "Home Depot receipt..."</p>
                            </div>
                            <div class="trouble-item">
                                <strong>Job not found?</strong>
                                <p>Make sure the job name matches exactly: "Johnson bathroom job"</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="voiceHelp.close()">Close</button>
                    <button class="btn-primary" onclick="voiceHelp.startPractice()">Start Practice</button>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    addHelpStyles() {
        const styleId = 'voice-help-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-help-btn {
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 16px;
                margin-left: 8px;
                transition: all 0.2s ease;
            }
            
            .voice-help-btn:hover {
                background: #e5e7eb;
                transform: scale(1.1);
            }
            
            .voice-help-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
            }
            
            .voice-help-modal.open {
                display: flex;
            }
            
            .voice-help-modal .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            
            .voice-help-modal .modal-content {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow-y: auto;
                animation: modalSlideIn 0.3s ease;
            }
            
            @keyframes modalSlideIn {
                from {
                    transform: translateY(-20px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .voice-help-modal .modal-header {
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .voice-help-modal .modal-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #111827;
            }
            
            .voice-help-modal .close-btn {
                background: none;
                border: none;
                font-size: 24px;
                color: #6b7280;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            
            .voice-help-modal .close-btn:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .voice-help-modal .modal-body {
                padding: 24px;
            }
            
            .help-section {
                margin-bottom: 32px;
            }
            
            .help-section h4 {
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 600;
                color: #111827;
            }
            
            .tips-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .tips-list li {
                padding: 8px 0;
                border-bottom: 1px solid #f3f4f6;
                color: #374151;
            }
            
            .tips-list li:last-child {
                border-bottom: none;
            }
            
            .examples-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 16px;
            }
            
            .example-card {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .example-card:hover {
                background: #f3f4f6;
                border-color: #9B6EC8;
                transform: translateY(-2px);
            }
            
            .example-text {
                font-weight: 600;
                color: #111827;
                margin-bottom: 8px;
                font-style: italic;
            }
            
            .example-category {
                display: inline-block;
                background: #9B6EC8;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 8px;
            }
            
            .example-description {
                font-size: 14px;
                color: #6b7280;
            }
            
            .practice-section {
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 16px;
            }
            
            .practice-input {
                display: flex;
                gap: 8px;
                margin: 16px 0;
            }
            
            .practice-input input {
                flex: 1;
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .practice-input button {
                padding: 10px 16px;
                background: #9B6EC8;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
            }
            
            .practice-feedback {
                margin-top: 16px;
                padding: 12px;
                border-radius: 6px;
                display: none;
            }
            
            .practice-feedback.success {
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                color: #166534;
                display: block;
            }
            
            .practice-feedback.error {
                background: #fef2f2;
                border: 1px solid #fecaca;
                color: #dc2626;
                display: block;
            }
            
            .troubleshooting {
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            
            .trouble-item {
                background: #fef3c7;
                border: 1px solid #fde68a;
                border-radius: 6px;
                padding: 12px;
            }
            
            .trouble-item strong {
                color: #92400e;
                display: block;
                margin-bottom: 4px;
            }
            
            .trouble-item p {
                color: #92400e;
                margin: 0;
                font-size: 14px;
            }
            
            .voice-help-modal .modal-footer {
                padding: 20px 24px;
                border-top: 1px solid #e5e7eb;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }
            
            .btn-primary,
            .btn-secondary {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
            }
            
            .btn-primary {
                background: #9B6EC8;
                color: white;
            }
            
            .btn-primary:hover {
                background: #7C3AED;
            }
            
            .btn-secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            
            .btn-secondary:hover {
                background: #e5e7eb;
            }
            
            @media (max-width: 768px) {
                .voice-help-modal .modal-content {
                    width: 95%;
                    margin: 20px;
                }
                
                .examples-grid {
                    grid-template-columns: 1fr;
                }
                
                .practice-input {
                    flex-direction: column;
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    tryExample(exampleText) {
        // Simulate voice input with the example
        const practiceInput = document.getElementById('practice-input');
        if (practiceInput) {
            practiceInput.value = exampleText;
            this.practiceCommand();
        }
    }
    
    practiceCommand() {
        const practiceInput = document.getElementById('practice-input');
        const feedback = document.getElementById('practice-feedback');
        
        if (!practiceInput || !feedback) return;
        
        const command = practiceInput.value.trim();
        if (!command) {
            feedback.className = 'practice-feedback error';
            feedback.textContent = 'Please enter a command to practice';
            return;
        }
        
        // Simulate parsing the command
        const result = this.parsePracticeCommand(command);
        
        if (result.success) {
            feedback.className = 'practice-feedback success';
            feedback.innerHTML = `
                <strong>Great job!</strong><br>
                Detected: ${result.vendor} - $${result.amount}<br>
                ${result.job ? `Job: ${result.job}` : ''}<br>
                Category: ${result.category}
            `;
        } else {
            feedback.className = 'practice-feedback error';
            feedback.innerHTML = `
                <strong>Try again!</strong><br>
                ${result.error}<br>
                <small>Tip: Make sure to include vendor and amount clearly</small>
            `;
        }
    }
    
    parsePracticeCommand(command) {
        // Simple command parsing for practice mode
        const lowerCommand = command.toLowerCase();
        
        // Extract amount (look for numbers)
        const amountMatch = lowerCommand.match(/(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?|dollars?|bucks?)?/i);
        const amount = amountMatch ? parseFloat(amountMatch[1]) : null;
        
        // Extract vendor (common vendors)
        const vendors = ['home depot', 'lumber yard', 'gas station', 'subcontractor', 'equipment rental'];
        const vendor = vendors.find(v => lowerCommand.includes(v)) || 'Unknown Vendor';
        
        // Extract job (look for "job" keyword)
        const jobMatch = lowerCommand.match(/(\w+)\s+job/i);
        const job = jobMatch ? jobMatch[1] : null;
        
        // Determine category
        let category = 'other';
        if (lowerCommand.includes('gas') || lowerCommand.includes('fuel')) category = 'equipment';
        else if (lowerCommand.includes('subcontractor')) category = 'subcontractor';
        else if (lowerCommand.includes('labor') || lowerCommand.includes('overtime')) category = 'labor';
        else if (lowerCommand.includes('equipment') || lowerCommand.includes('rental')) category = 'equipment';
        else if (lowerCommand.includes('lumber') || lowerCommand.includes('depot')) category = 'materials';
        
        if (!amount) {
            return {
                success: false,
                error: 'Could not detect amount. Try saying "fifty dollars" or "100 bucks"'
            };
        }
        
        return {
            success: true,
            vendor: vendor,
            amount: amount.toFixed(2),
            job: job,
            category: category
        };
    }
    
    startPractice() {
        // Start voice recognition for practice
        if (window.voiceButton) {
            this.close();
            setTimeout(() => {
                window.voiceButton.startRecording();
            }, 300);
        }
    }
    
    close() {
        const modal = document.querySelector('.voice-help-modal');
        if (modal) {
            modal.classList.remove('open');
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    }
}

// Global instance
window.voiceHelp = new VoiceHelp();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceHelp;
} 