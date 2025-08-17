/**
 * Voice Expense Entry Activation Script
 * Run this in the browser console on the dashboard page to test/activate voice entry
 */

// Check if voice button exists
const checkVoiceButton = () => {
    const container = document.querySelector('.voice-button-container');
    const voiceBtn = document.querySelector('.voice-btn');
    
    console.log('Voice Button Container:', container ? 'Found' : 'NOT FOUND');
    console.log('Voice Button:', voiceBtn ? 'Found' : 'NOT FOUND');
    
    if (container && !voiceBtn) {
        console.log('Container exists but button not initialized. Initializing now...');
        
        // Force initialization
        if (typeof initVoiceButton === 'function') {
            initVoiceButton();
            console.log('Voice button initialized!');
        } else {
            console.error('initVoiceButton function not found!');
        }
    }
    
    // Check if VoiceButton class exists
    if (typeof VoiceButton !== 'undefined') {
        console.log('VoiceButton class is available');
    } else {
        console.error('VoiceButton class NOT FOUND');
    }
    
    // Check if voice expense entry script is loaded
    if (typeof VoiceExpenseEntry !== 'undefined') {
        console.log('VoiceExpenseEntry class is available');
    } else {
        console.log('VoiceExpenseEntry class not loaded (using inline implementation)');
    }
    
    // Test the API endpoint
    testVoiceAPI();
};

// Test the voice API endpoint
const testVoiceAPI = async () => {
    console.log('\nTesting Voice API Endpoint...');
    
    try {
        const response = await fetch('/api/expenses/voice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transcript: 'test expense fifty dollars at home depot',
                source: 'activation_test'
            })
        });
        
        const result = await response.json();
        console.log('API Response:', result);
        
        if (response.ok && result.success) {
            console.log('✅ Voice API is WORKING!');
        } else {
            console.error('❌ Voice API returned error:', result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('❌ Failed to test voice API:', error);
    }
};

// Add visual indicator
const addVisualIndicator = () => {
    const container = document.querySelector('.voice-button-container');
    if (container && !document.querySelector('.voice-btn')) {
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            background: #ff6b6b;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            margin-right: 12px;
        `;
        indicator.textContent = 'Voice Button Missing - Click to Initialize';
        indicator.style.cursor = 'pointer';
        indicator.onclick = () => {
            initVoiceButton();
            indicator.remove();
        };
        container.appendChild(indicator);
    }
};

// Run checks
console.log('=== Voice Expense Entry Activation Check ===');
checkVoiceButton();
addVisualIndicator();

// Export for manual testing
window.testVoiceExpense = {
    checkButton: checkVoiceButton,
    testAPI: testVoiceAPI,
    forceInit: () => {
        const container = document.querySelector('.voice-button-container');
        if (container && typeof VoiceButton !== 'undefined') {
            new VoiceButton(container, {
                onSuccess: (expense) => {
                    console.log('Voice expense created:', expense);
                    alert(`Success! Added $${(expense.amount_cents/100).toFixed(2)} expense`);
                },
                onError: (error) => {
                    console.error('Voice error:', error);
                    alert('Error: ' + error);
                }
            });
            console.log('Voice button force initialized!');
        }
    }
};

console.log('\nTo manually test, run:');
console.log('- testVoiceExpense.checkButton()');
console.log('- testVoiceExpense.testAPI()');
console.log('- testVoiceExpense.forceInit()');