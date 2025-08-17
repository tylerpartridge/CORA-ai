/**
 * Plaid Link Integration for CORA
 */

// Initialize Plaid Link
async function initializePlaidLink() {
    try {
        // Get link token from backend
        const response = await fetch('/api/integrations/plaid/link-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_user_id: 'test-user', // In production, use actual user ID
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get link token');
        }

        const data = await response.json();
        const linkToken = data.link_token;

        // Configure Plaid Link
        const handler = Plaid.create({
            token: linkToken,
            onSuccess: async (public_token, metadata) => {
                // console.log('Plaid Link success:', metadata);
                
                // Exchange public token for access token
                try {
                    const exchangeResponse = await fetch('/api/integrations/plaid/exchange-token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            public_token: public_token,
                            metadata: metadata
                        })
                    });

                    if (exchangeResponse.ok) {
                        // Success! Redirect to success page
                        window.location.href = '/onboarding/success';
                    } else {
                        // console.error('Token exchange failed');
                        alert('Failed to connect bank account. Please try again.');
                    }
                } catch (error) {
                    // console.error('Token exchange error:', error);
                    alert('Failed to connect bank account. Please try again.');
                }
            },
            onExit: (err, metadata) => {
                // console.log('Plaid Link exit:', err, metadata);
                if (err != null) {
                    // Handle error
                    // console.error('Plaid Link error:', err);
                }
            },
            onEvent: (eventName, metadata) => {
                // console.log('Plaid Link event:', eventName, metadata);
            }
        });

        return handler;
    } catch (error) {
        // console.error('Failed to initialize Plaid Link:', error);
        alert('Failed to initialize bank connection. Please try again.');
        return null;
    }
}

// Global variable to store Plaid handler
let plaidHandler = null;

// Initialize when page loads - but only after Plaid script loads
document.addEventListener('DOMContentLoaded', async () => {
    // console.log('Plaid Connect: DOM loaded, checking for Plaid...');
    
    // Wait a bit for Plaid to load
    let plaidCheckCount = 0;
    const checkPlaid = setInterval(() => {
        plaidCheckCount++;
        if (typeof Plaid !== 'undefined') {
            // console.log('Plaid Connect: Plaid loaded successfully!');
            clearInterval(checkPlaid);
            initializePlaidHandlers();
        } else if (plaidCheckCount > 10) {
            // console.error('Plaid Connect: Plaid failed to load after 5 seconds');
            clearInterval(checkPlaid);
        }
    }, 500);
    
    async function initializePlaidHandlers() {
        // console.log('Plaid Connect: Initializing handlers...');
        
        // Remove the existing click handlers from connect_bank.html
        // to avoid conflicts
        document.querySelectorAll('.bank-option').forEach(option => {
            const newOption = option.cloneNode(true);
            option.parentNode.replaceChild(newOption, option);
        });
        
        // Add new click handlers to bank options
        document.querySelectorAll('.bank-option').forEach(option => {
            option.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const bankName = option.dataset.bank;
                // console.log('Bank selected:', bankName);
                
                // Remove previous selection
                document.querySelectorAll('.bank-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                
                // Select current option
                option.classList.add('selected');
                
                // Update button state
                const connectBtn = document.getElementById('connectBtn');
                const connectBtnText = document.getElementById('connectBtnText');
                
                if (bankName === 'other') {
                    connectBtn.disabled = false;
                    connectBtnText.textContent = 'Continue with manual entry';
                    document.getElementById('manualBankEntry').classList.remove('hidden');
                } else {
                    connectBtn.disabled = false;
                    connectBtnText.textContent = `Connect ${option.querySelector('h4').textContent}`;
                    document.getElementById('manualBankEntry').classList.add('hidden');
                    
                    // Initialize and open Plaid Link immediately
                    if (!plaidHandler) {
                        plaidHandler = await initializePlaidLink();
                    }
                    
                    // Open Plaid Link
                    if (plaidHandler) {
                        // console.log('Opening Plaid Link...');
                        plaidHandler.open();
                    }
                }
            });
        });
        
        // Override connect button handler
        const connectBtn = document.getElementById('connectBtn');
        if (connectBtn) {
            // Remove existing listeners by cloning
            const newBtn = connectBtn.cloneNode(true);
            connectBtn.parentNode.replaceChild(newBtn, connectBtn);
            
            newBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                
                const selectedBank = document.querySelector('.bank-option.selected');
                if (selectedBank && selectedBank.dataset.bank !== 'other') {
                    // Initialize Plaid Link if not already done
                    if (!plaidHandler) {
                        plaidHandler = await initializePlaidLink();
                    }
                    
                    // Open Plaid Link
                    if (plaidHandler) {
                        // console.log('Opening Plaid Link from connect button...');
                        plaidHandler.open();
                    }
                }
            });
        }
    }
});