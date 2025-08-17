// Emotional Wellness Component - CORA's Empathetic Support System
// Shows wellness check-ins, stress indicators, and emotional support

class EmotionalWellness {
    constructor() {
        this.profile = null;
        this.checkInVisible = false;
        this.lastCheckIn = null;
        this.supportHistory = [];
        this.init();
    }

    init() {
        // Create wellness indicator in dashboard
        this.createWellnessIndicator();
        
        // Create check-in modal
        this.createCheckInModal();
        
        // Start wellness monitoring
        this.startWellnessMonitoring();
        
        // Add styles
        this.injectStyles();
    }

    createWellnessIndicator() {
        // Add wellness indicator to existing dashboard
        const indicatorHtml = `
            <div id="wellness-indicator" class="wellness-indicator">
                <div class="wellness-icon">
                    <span class="mood-emoji">😊</span>
                    <div class="stress-ring">
                        <svg viewBox="0 0 36 36">
                            <path class="stress-bg"
                                d="M18 2.0845
                                a 15.9155 15.9155 0 0 1 0 31.831
                                a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <path class="stress-level"
                                stroke-dasharray="0, 100"
                                d="M18 2.0845
                                a 15.9155 15.9155 0 0 1 0 31.831
                                a 15.9155 15.9155 0 0 1 0 -31.831" />
                        </svg>
                    </div>
                </div>
                <div class="wellness-status">
                    <div class="status-text">Checking wellness...</div>
                    <div class="status-subtext">Click for support</div>
                </div>
            </div>
        `;
        
        // Try to add to intelligence widget area first
        const intelligenceWidget = document.querySelector('.intelligence-score-widget');
        if (intelligenceWidget) {
            intelligenceWidget.insertAdjacentHTML('afterend', indicatorHtml);
        } else {
            // Fallback to dashboard header
            const dashboardHeader = document.querySelector('.dashboard-header');
            if (dashboardHeader) {
                dashboardHeader.insertAdjacentHTML('beforeend', indicatorHtml);
            }
        }
        
        // Add click handler
        const indicator = document.getElementById('wellness-indicator');
        if (indicator) {
            indicator.addEventListener('click', () => this.showCheckIn());
        }
    }

    createCheckInModal() {
        const modalHtml = `
            <div id="wellness-check-in" class="wellness-check-in hidden">
                <div class="check-in-overlay"></div>
                <div class="check-in-content">
                    <button class="check-in-close">×</button>
                    
                    <div class="check-in-header">
                        <h3 class="greeting">Hey there! 👋</h3>
                        <p class="observation">Let's check in on how you're doing.</p>
                    </div>
                    
                    <div class="emotional-state">
                        <div class="state-indicator">
                            <span class="state-emoji">😊</span>
                            <span class="state-label">Balanced</span>
                        </div>
                        <div class="stress-meter">
                            <label>Stress Level</label>
                            <div class="meter-bar">
                                <div class="meter-fill"></div>
                            </div>
                            <div class="meter-labels">
                                <span>Low</span>
                                <span>High</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="wellness-insights">
                        <h4>What I've noticed:</h4>
                        <div class="insight-cards"></div>
                    </div>
                    
                    <div class="support-recommendations">
                        <h4>How can I help?</h4>
                        <div class="support-actions"></div>
                    </div>
                    
                    <div class="quick-actions">
                        <button class="action-button" data-action="breathing">
                            <span>🧘</span> Breathing Exercise
                        </button>
                        <button class="action-button" data-action="break">
                            <span>☕</span> Take a Break
                        </button>
                        <button class="action-button" data-action="chat">
                            <span>💬</span> Just Talk
                        </button>
                    </div>
                    
                    <div class="check-in-footer">
                        <p class="care-message">Remember: Your well-being matters as much as your business.</p>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Add event handlers
        const modal = document.getElementById('wellness-check-in');
        const closeBtn = modal.querySelector('.check-in-close');
        const overlay = modal.querySelector('.check-in-overlay');
        
        closeBtn.addEventListener('click', () => this.hideCheckIn());
        overlay.addEventListener('click', () => this.hideCheckIn());
        
        // Quick action handlers
        modal.querySelectorAll('.action-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    async startWellnessMonitoring() {
        // Initial check
        await this.checkEmotionalWellness();
        
        // Periodic checks (every 30 minutes during work hours)
        setInterval(() => {
            const hour = new Date().getHours();
            if (hour >= 8 && hour <= 20) {
                this.checkEmotionalWellness();
            }
        }, 30 * 60 * 1000);
        
        // Check on specific triggers
        this.monitorStressTriggers();
    }

    async checkEmotionalWellness() {
        try {
            const response = await fetch('/api/wellness/check', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateWellnessProfile(data);
                
                // Show proactive check-in if stress is high
                if (data.profile.stress_level > 7 && !this.checkInVisible) {
                    setTimeout(() => this.showProactiveCheckIn(data), 5000);
                }
            }
        } catch (error) {
            // console.error('Wellness check error:', error);
        }
    }

    updateWellnessProfile(data) {
        this.profile = data.profile;
        
        // Update indicator
        const indicator = document.getElementById('wellness-indicator');
        if (!indicator) return;
        
        // Update mood emoji
        const moodEmoji = indicator.querySelector('.mood-emoji');
        moodEmoji.textContent = this.getStateEmoji(data.profile.current_state);
        
        // Update stress ring
        const stressPath = indicator.querySelector('.stress-level');
        const stressPercent = (data.profile.stress_level / 10) * 100;
        stressPath.style.strokeDasharray = `${stressPercent}, 100`;
        
        // Update color based on stress
        if (data.profile.stress_level > 7) {
            stressPath.style.stroke = '#ff4444';
            indicator.classList.add('high-stress');
        } else if (data.profile.stress_level > 5) {
            stressPath.style.stroke = '#ffaa00';
            indicator.classList.remove('high-stress');
        } else {
            stressPath.style.stroke = '#00ff88';
            indicator.classList.remove('high-stress');
        }
        
        // Update status text
        const statusText = indicator.querySelector('.status-text');
        const statusSubtext = indicator.querySelector('.status-subtext');
        
        statusText.textContent = this.getStateLabel(data.profile.current_state);
        
        if (data.profile.stress_level > 6) {
            statusSubtext.textContent = 'Support available';
            indicator.classList.add('pulse');
        } else {
            statusSubtext.textContent = 'Doing well';
            indicator.classList.remove('pulse');
        }
    }

    getStateEmoji(state) {
        const emojis = {
            'thriving': '🌟',
            'balanced': '😊',
            'stressed': '😰',
            'overwhelmed': '😵',
            'burnt_out': '😫',
            'recovering': '💪',
            'energized': '⚡'
        };
        return emojis[state] || '😊';
    }

    getStateLabel(state) {
        const labels = {
            'thriving': 'Thriving',
            'balanced': 'Balanced',
            'stressed': 'Stressed',
            'overwhelmed': 'Overwhelmed',
            'burnt_out': 'Burnt Out',
            'recovering': 'Recovering',
            'energized': 'Energized'
        };
        return labels[state] || 'Checking...';
    }

    showCheckIn() {
        const modal = document.getElementById('wellness-check-in');
        modal.classList.remove('hidden');
        this.checkInVisible = true;
        
        // Update content based on current profile
        if (this.profile) {
            this.updateCheckInContent(this.profile);
        }
        
        // Track interaction
        this.trackWellnessInteraction('check_in_opened');
    }

    hideCheckIn() {
        const modal = document.getElementById('wellness-check-in');
        modal.classList.add('hidden');
        this.checkInVisible = false;
    }

    updateCheckInContent(profile) {
        const modal = document.getElementById('wellness-check-in');
        
        // Update greeting based on time and state
        const greeting = modal.querySelector('.greeting');
        const observation = modal.querySelector('.observation');
        
        const hour = new Date().getHours();
        if (profile.stress_level > 7) {
            greeting.textContent = "Hey, let's take a moment 🤗";
            observation.textContent = "I've noticed things have been intense lately.";
        } else if (profile.current_state === 'thriving') {
            greeting.textContent = "You're doing amazing! 🌟";
            observation.textContent = "Your positive energy is inspiring.";
        } else {
            greeting.textContent = hour < 12 ? "Good morning! ☀️" : "How's it going? 👋";
            observation.textContent = "Let's check in on your well-being.";
        }
        
        // Update emotional state display
        const stateEmoji = modal.querySelector('.state-emoji');
        const stateLabel = modal.querySelector('.state-label');
        stateEmoji.textContent = this.getStateEmoji(profile.current_state);
        stateLabel.textContent = this.getStateLabel(profile.current_state);
        
        // Update stress meter
        const meterFill = modal.querySelector('.meter-fill');
        meterFill.style.width = `${(profile.stress_level / 10) * 100}%`;
        
        if (profile.stress_level > 7) {
            meterFill.style.backgroundColor = '#ff4444';
        } else if (profile.stress_level > 5) {
            meterFill.style.backgroundColor = '#ffaa00';
        } else {
            meterFill.style.backgroundColor = '#00ff88';
        }
        
        // Update insights
        this.updateWellnessInsights(profile);
        
        // Update support recommendations
        this.updateSupportRecommendations(profile);
    }

    updateWellnessInsights(profile) {
        const insightCards = document.querySelector('.insight-cards');
        insightCards.innerHTML = '';
        
        // Show recent signals as insights
        if (profile.recent_signals && profile.recent_signals.length > 0) {
            profile.recent_signals.slice(0, 3).forEach(signal => {
                const card = document.createElement('div');
                card.className = `insight-card ${signal.is_positive ? 'positive' : 'negative'}`;
                
                card.innerHTML = `
                    <div class="insight-icon">${this.getSignalIcon(signal.indicator)}</div>
                    <div class="insight-text">${signal.context.message || 'Pattern detected'}</div>
                `;
                
                insightCards.appendChild(card);
            });
        } else {
            insightCards.innerHTML = '<p class="no-insights">Monitoring your patterns...</p>';
        }
    }

    getSignalIcon(indicator) {
        const icons = {
            'late_night_work': '🌙',
            'weekend_work': '📅',
            'rapid_expense_entry': '⚡',
            'positive_momentum': '📈',
            'regular_breaks': '☕',
            'cash_flow_stress': '💰'
        };
        return icons[indicator] || '📊';
    }

    updateSupportRecommendations(profile) {
        const supportActions = document.querySelector('.support-actions');
        supportActions.innerHTML = '';
        
        if (profile.support_recommendations && profile.support_recommendations.length > 0) {
            profile.support_recommendations.slice(0, 2).forEach(rec => {
                const action = document.createElement('div');
                action.className = 'support-action';
                
                action.innerHTML = `
                    <h5>${rec.title}</h5>
                    <p>${rec.message}</p>
                    ${rec.actions ? `
                        <ul>
                            ${rec.actions.map(a => `<li>${a}</li>`).join('')}
                        </ul>
                    ` : ''}
                `;
                
                supportActions.appendChild(action);
            });
        }
    }

    showProactiveCheckIn(data) {
        // Create a gentle notification instead of forcing modal
        const notification = document.createElement('div');
        notification.className = 'wellness-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">💙</span>
                <div class="notification-text">
                    <strong>Just checking in...</strong>
                    <p>${data.check_in.observation}</p>
                </div>
                <button class="notification-action">I'm here</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('visible'), 100);
        
        // Add handlers
        notification.querySelector('.notification-action').addEventListener('click', () => {
            notification.remove();
            this.showCheckIn();
        });
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.classList.remove('visible');
                setTimeout(() => notification.remove(), 300);
            }
        }, 10000);
    }

    handleQuickAction(action) {
        switch (action) {
            case 'breathing':
                this.startBreathingExercise();
                break;
            case 'break':
                this.startBreakTimer();
                break;
            case 'chat':
                this.openSupportChat();
                break;
        }
        
        // Track action
        this.trackWellnessInteraction(`quick_action_${action}`);
    }

    startBreathingExercise() {
        // Create breathing guide overlay
        const guide = document.createElement('div');
        guide.className = 'breathing-guide';
        guide.innerHTML = `
            <div class="breathing-content">
                <div class="breathing-circle">
                    <div class="breathing-text">Breathe In</div>
                </div>
                <div class="breathing-instructions">
                    <p>Follow the circle - breathe in as it grows, out as it shrinks</p>
                    <button class="breathing-done">Done</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(guide);
        
        // Animate breathing
        const circle = guide.querySelector('.breathing-circle');
        const text = guide.querySelector('.breathing-text');
        let phase = 'in';
        
        const breathingInterval = setInterval(() => {
            if (phase === 'in') {
                circle.classList.add('expand');
                text.textContent = 'Breathe In';
                setTimeout(() => {
                    text.textContent = 'Hold';
                    setTimeout(() => {
                        phase = 'out';
                    }, 2000);
                }, 4000);
            } else {
                circle.classList.remove('expand');
                text.textContent = 'Breathe Out';
                setTimeout(() => {
                    text.textContent = 'Rest';
                    setTimeout(() => {
                        phase = 'in';
                    }, 2000);
                }, 4000);
            }
        }, 8000);
        
        // Start first cycle immediately
        circle.classList.add('expand');
        
        // Done button
        guide.querySelector('.breathing-done').addEventListener('click', () => {
            clearInterval(breathingInterval);
            guide.remove();
            this.showBreathingComplete();
        });
    }

    showBreathingComplete() {
        const message = document.createElement('div');
        message.className = 'wellness-message success';
        message.innerHTML = `
            <span>🌟</span>
            <p>Great job! Taking mindful breaks improves decision-making.</p>
        `;
        
        document.body.appendChild(message);
        setTimeout(() => message.classList.add('visible'), 100);
        setTimeout(() => {
            message.classList.remove('visible');
            setTimeout(() => message.remove(), 300);
        }, 3000);
    }

    startBreakTimer() {
        // Create break timer
        const timer = document.createElement('div');
        timer.className = 'break-timer';
        timer.innerHTML = `
            <div class="timer-content">
                <h3>Break Time! ☕</h3>
                <div class="timer-display">15:00</div>
                <p>Step away from work - you've earned it!</p>
                <button class="timer-end">End Break Early</button>
            </div>
        `;
        
        document.body.appendChild(timer);
        
        let seconds = 15 * 60; // 15 minutes
        const display = timer.querySelector('.timer-display');
        
        const interval = setInterval(() => {
            seconds--;
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            display.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
            
            if (seconds <= 0) {
                clearInterval(interval);
                timer.remove();
                this.showBreakComplete();
            }
        }, 1000);
        
        timer.querySelector('.timer-end').addEventListener('click', () => {
            clearInterval(interval);
            timer.remove();
        });
    }

    showBreakComplete() {
        const message = document.createElement('div');
        message.className = 'wellness-message success';
        message.innerHTML = `
            <span>🎉</span>
            <p>Welcome back! You're more productive after a good break.</p>
        `;
        
        document.body.appendChild(message);
        setTimeout(() => message.classList.add('visible'), 100);
        setTimeout(() => {
            message.classList.remove('visible');
            setTimeout(() => message.remove(), 300);
        }, 3000);
    }

    openSupportChat() {
        // Open CORA chat with wellness context
        if (window.CORAChat) {
            window.CORAChat.open({
                context: 'wellness_support',
                initialMessage: "I'm here to listen. What's on your mind?",
                tone: 'empathetic'
            });
        }
        
        this.hideCheckIn();
    }

    monitorStressTriggers() {
        // Monitor for rapid actions that might indicate stress
        let actionCount = 0;
        let actionTimer = null;
        
        document.addEventListener('click', () => {
            actionCount++;
            
            if (actionCount > 20) {
                // Many rapid clicks might indicate frustration
                this.detectPossibleFrustration();
                actionCount = 0;
            }
            
            // Reset counter after 10 seconds of inactivity
            clearTimeout(actionTimer);
            actionTimer = setTimeout(() => {
                actionCount = 0;
            }, 10000);
        });
        
        // Monitor for late night activity
        setInterval(() => {
            const hour = new Date().getHours();
            if ((hour >= 22 || hour < 4) && !this.lateNightWarningShown) {
                this.showLateNightCare();
                this.lateNightWarningShown = true;
            } else if (hour >= 6 && hour < 22) {
                this.lateNightWarningShown = false;
            }
        }, 30 * 60 * 1000); // Check every 30 minutes
    }

    detectPossibleFrustration() {
        // Don't show if already showing other wellness content
        if (this.checkInVisible) return;
        
        const message = document.createElement('div');
        message.className = 'wellness-tip';
        message.innerHTML = `
            <span>💡</span>
            <p>Tip: If something's not working, I'm here to help!</p>
        `;
        
        document.body.appendChild(message);
        setTimeout(() => message.classList.add('visible'), 100);
        setTimeout(() => {
            message.classList.remove('visible');
            setTimeout(() => message.remove(), 300);
        }, 5000);
    }

    showLateNightCare() {
        const notification = document.createElement('div');
        notification.className = 'wellness-notification late-night';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">🌙</span>
                <div class="notification-text">
                    <strong>Still working?</strong>
                    <p>Rest is part of success. Your business needs you healthy.</p>
                </div>
                <button class="notification-action">I'll wrap up soon</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('visible'), 100);
        
        notification.querySelector('.notification-action').addEventListener('click', () => {
            notification.classList.remove('visible');
            setTimeout(() => notification.remove(), 300);
            
            // Send acknowledgment
            this.trackWellnessInteraction('late_night_acknowledged');
        });
    }

    async trackWellnessInteraction(action) {
        try {
            await fetch('/api/wellness/interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    action: action,
                    timestamp: new Date().toISOString(),
                    context: {
                        stress_level: this.profile?.stress_level,
                        current_state: this.profile?.current_state
                    }
                })
            });
        } catch (error) {
            // console.error('Failed to track wellness interaction:', error);
        }
    }

    injectStyles() {
        const styles = `
            <style>
                /* Wellness Indicator */
                .wellness-indicator {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px 16px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                }

                .wellness-indicator:hover {
                    background: rgba(255, 255, 255, 0.1);
                    transform: translateY(-1px);
                }

                .wellness-indicator.high-stress {
                    animation: subtlePulse 2s infinite;
                }

                @keyframes subtlePulse {
                    0%, 100% { box-shadow: 0 0 0 0 rgba(255, 68, 68, 0); }
                    50% { box-shadow: 0 0 20px 5px rgba(255, 68, 68, 0.2); }
                }

                .wellness-icon {
                    position: relative;
                    width: 36px;
                    height: 36px;
                }

                .mood-emoji {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 20px;
                    z-index: 2;
                }

                .stress-ring {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    transform: rotate(-90deg);
                }

                .stress-ring svg {
                    width: 100%;
                    height: 100%;
                }

                .stress-bg,
                .stress-level {
                    fill: none;
                    stroke-width: 3;
                }

                .stress-bg {
                    stroke: rgba(255, 255, 255, 0.1);
                }

                .stress-level {
                    stroke: #00ff88;
                    stroke-linecap: round;
                    transition: stroke-dasharray 0.5s ease, stroke 0.5s ease;
                }

                .wellness-status {
                    flex: 1;
                }

                .status-text {
                    font-weight: 600;
                    color: #fff;
                    font-size: 14px;
                }

                .status-subtext {
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.6);
                    margin-top: 2px;
                }

                /* Check-in Modal */
                .wellness-check-in {
                    position: fixed;
                    inset: 0;
                    z-index: 2000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }

                .wellness-check-in.hidden {
                    display: none;
                }

                .check-in-overlay {
                    position: absolute;
                    inset: 0;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(5px);
                }

                .check-in-content {
                    position: relative;
                    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 32px;
                    max-width: 500px;
                    width: 100%;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                }

                .check-in-close {
                    position: absolute;
                    top: 16px;
                    right: 16px;
                    background: rgba(255, 255, 255, 0.1);
                    border: none;
                    color: #fff;
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    cursor: pointer;
                    font-size: 20px;
                    transition: all 0.2s ease;
                }

                .check-in-close:hover {
                    background: rgba(255, 255, 255, 0.2);
                }

                .check-in-header {
                    text-align: center;
                    margin-bottom: 24px;
                }

                .greeting {
                    font-size: 24px;
                    color: #fff;
                    margin: 0 0 8px 0;
                }

                .observation {
                    color: rgba(255, 255, 255, 0.8);
                    margin: 0;
                }

                /* Emotional State Display */
                .emotional-state {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                    padding: 20px;
                    margin-bottom: 24px;
                }

                .state-indicator {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                    margin-bottom: 16px;
                }

                .state-emoji {
                    font-size: 32px;
                }

                .state-label {
                    font-size: 20px;
                    font-weight: 600;
                    color: #fff;
                }

                .stress-meter {
                    margin-top: 16px;
                }

                .stress-meter label {
                    display: block;
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.6);
                    margin-bottom: 8px;
                }

                .meter-bar {
                    height: 8px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    overflow: hidden;
                }

                .meter-fill {
                    height: 100%;
                    background: #00ff88;
                    transition: width 0.5s ease, background-color 0.5s ease;
                }

                .meter-labels {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 4px;
                    font-size: 11px;
                    color: rgba(255, 255, 255, 0.5);
                }

                /* Wellness Insights */
                .wellness-insights {
                    margin-bottom: 24px;
                }

                .wellness-insights h4 {
                    color: #fff;
                    font-size: 16px;
                    margin: 0 0 12px 0;
                }

                .insight-cards {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }

                .insight-card {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.9);
                }

                .insight-card.positive {
                    background: rgba(0, 255, 136, 0.1);
                    border: 1px solid rgba(0, 255, 136, 0.2);
                }

                .insight-card.negative {
                    background: rgba(255, 68, 68, 0.1);
                    border: 1px solid rgba(255, 68, 68, 0.2);
                }

                .insight-icon {
                    font-size: 20px;
                }

                /* Support Recommendations */
                .support-recommendations {
                    margin-bottom: 24px;
                }

                .support-recommendations h4 {
                    color: #fff;
                    font-size: 16px;
                    margin: 0 0 12px 0;
                }

                .support-action {
                    background: rgba(255, 152, 0, 0.1);
                    border: 1px solid rgba(255, 152, 0, 0.2);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                }

                .support-action h5 {
                    color: #ff9800;
                    margin: 0 0 8px 0;
                    font-size: 14px;
                }

                .support-action p {
                    color: rgba(255, 255, 255, 0.9);
                    margin: 0 0 8px 0;
                    font-size: 13px;
                }

                .support-action ul {
                    margin: 0;
                    padding-left: 20px;
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 13px;
                }

                /* Quick Actions */
                .quick-actions {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 24px;
                }

                .action-button {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 4px;
                    padding: 12px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-size: 12px;
                }

                .action-button:hover {
                    background: rgba(255, 255, 255, 0.1);
                    transform: translateY(-1px);
                }

                .action-button span {
                    font-size: 24px;
                }

                /* Care Message */
                .care-message {
                    text-align: center;
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 14px;
                    font-style: italic;
                    margin: 0;
                }

                /* Notifications */
                .wellness-notification {
                    position: fixed;
                    bottom: 100px;
                    right: 20px;
                    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                    transform: translateX(400px);
                    transition: transform 0.3s ease;
                    z-index: 1500;
                    max-width: 320px;
                }

                .wellness-notification.visible {
                    transform: translateX(0);
                }

                .wellness-notification.late-night {
                    border-color: rgba(138, 43, 226, 0.3);
                    box-shadow: 0 8px 32px rgba(138, 43, 226, 0.2);
                }

                .notification-content {
                    display: flex;
                    gap: 12px;
                    align-items: flex-start;
                }

                .notification-icon {
                    font-size: 24px;
                }

                .notification-text {
                    flex: 1;
                }

                .notification-text strong {
                    display: block;
                    color: #fff;
                    margin-bottom: 4px;
                }

                .notification-text p {
                    margin: 0;
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                }

                .notification-action {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    color: #fff;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 12px;
                    transition: all 0.2s ease;
                    white-space: nowrap;
                }

                .notification-action:hover {
                    background: rgba(255, 255, 255, 0.2);
                }

                /* Wellness Messages */
                .wellness-message,
                .wellness-tip {
                    position: fixed;
                    top: 80px;
                    left: 50%;
                    transform: translateX(-50%) translateY(-100px);
                    background: rgba(30, 30, 30, 0.95);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 12px 20px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: transform 0.3s ease;
                    z-index: 1600;
                }

                .wellness-message.visible,
                .wellness-tip.visible {
                    transform: translateX(-50%) translateY(0);
                }

                .wellness-message.success {
                    border-color: rgba(0, 255, 136, 0.3);
                    background: rgba(0, 255, 136, 0.1);
                }

                .wellness-message span,
                .wellness-tip span {
                    font-size: 20px;
                }

                .wellness-message p,
                .wellness-tip p {
                    margin: 0;
                    color: #fff;
                    font-size: 14px;
                }

                /* Breathing Exercise */
                .breathing-guide {
                    position: fixed;
                    inset: 0;
                    background: rgba(0, 0, 0, 0.95);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 3000;
                }

                .breathing-content {
                    text-align: center;
                }

                .breathing-circle {
                    width: 200px;
                    height: 200px;
                    background: radial-gradient(circle, rgba(0, 255, 136, 0.1) 0%, rgba(0, 255, 136, 0) 70%);
                    border: 2px solid rgba(0, 255, 136, 0.3);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 32px;
                    transition: transform 4s ease-in-out;
                }

                .breathing-circle.expand {
                    transform: scale(1.5);
                }

                .breathing-text {
                    color: #fff;
                    font-size: 20px;
                    font-weight: 600;
                }

                .breathing-instructions {
                    color: rgba(255, 255, 255, 0.8);
                }

                .breathing-done {
                    margin-top: 24px;
                    padding: 8px 24px;
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    color: #fff;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }

                .breathing-done:hover {
                    background: rgba(255, 255, 255, 0.2);
                }

                /* Break Timer */
                .break-timer {
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 16px;
                    padding: 32px;
                    text-align: center;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                    z-index: 2500;
                }

                .timer-content h3 {
                    color: #fff;
                    margin: 0 0 16px 0;
                }

                .timer-display {
                    font-size: 48px;
                    font-weight: 600;
                    color: #00ff88;
                    margin: 16px 0;
                    font-family: 'SF Mono', 'Monaco', monospace;
                }

                .timer-content p {
                    color: rgba(255, 255, 255, 0.8);
                    margin: 0 0 24px 0;
                }

                .timer-end {
                    padding: 8px 24px;
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    color: #fff;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }

                .timer-end:hover {
                    background: rgba(255, 255, 255, 0.2);
                }

                /* Responsive */
                @media (max-width: 600px) {
                    .check-in-content {
                        padding: 24px;
                    }

                    .quick-actions {
                        flex-direction: column;
                    }

                    .wellness-notification {
                        right: 10px;
                        left: 10px;
                        max-width: none;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.EmotionalWellness = new EmotionalWellness();
    });
} else {
    window.EmotionalWellness = new EmotionalWellness();
}