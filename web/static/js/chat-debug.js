// Chat Debug Script
// console.log('🔍 Chat Debug Script Loaded');

// Check if chat elements exist
function checkChatElements() {
    // console.log('🔍 Checking chat elements...');
    
    const chatBubble = document.querySelector('.cora-chat-bubble');
    const chatWindow = document.querySelector('.cora-chat-window');
    const welcomeMessage = document.querySelector('.cora-welcome-message');
    
    // console.log('Chat bubble:', chatBubble ? '✅ Found' : '❌ Missing');
    // console.log('Chat window:', chatWindow ? '✅ Found' : '❌ Missing');
    // console.log('Welcome message:', welcomeMessage ? '✅ Found' : '❌ Missing');
    
    // Check if chat instance exists
    // console.log('CoraChat instance:', window.coraChat ? '✅ Found' : '❌ Missing');
    // console.log('EnhancedChat instance:', window.enhancedChat ? '✅ Found' : '❌ Missing');
    
    // Check CSS
    const chatStyles = getComputedStyle(chatBubble || document.body);
    // console.log('Chat bubble display:', chatBubble ? chatStyles.display : 'N/A');
    // console.log('Chat bubble visibility:', chatBubble ? chatStyles.visibility : 'N/A');
    
    return {
        chatBubble: !!chatBubble,
        chatWindow: !!chatWindow,
        welcomeMessage: !!welcomeMessage,
        coraChat: !!window.coraChat,
        enhancedChat: !!window.enhancedChat
    };
}

// Force show chat if hidden
function forceShowChat() {
    // console.log('🔧 Forcing chat to show...');
    
    const chatBubble = document.querySelector('.cora-chat-bubble');
    if (chatBubble) {
        chatBubble.style.display = 'block';
        chatBubble.style.visibility = 'visible';
        chatBubble.style.opacity = '1';
        // console.log('✅ Chat bubble forced visible');
    } else {
        // console.log('❌ No chat bubble found to show');
    }
}

// Create chat if missing
function createChatIfMissing() {
    // console.log('🔧 Creating chat if missing...');
    
    if (!document.querySelector('.cora-chat-bubble')) {
        // console.log('Creating new chat instance...');
        
        // Create simple chat bubble
        const chatBubble = document.createElement('div');
        chatBubble.className = 'cora-chat-bubble';
        chatBubble.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3 .97 4.29L1 23l6.71-1.97C9 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.41 0-2.73-.36-3.88-.99l-.28-.15-2.91.85.85-2.91-.15-.28C4.36 14.73 4 13.41 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/>
                <circle cx="8.5" cy="12" r="1.5"/>
                <circle cx="12" cy="12" r="1.5"/>
                <circle cx="15.5" cy="12" r="1.5"/>
            </svg>
        `;
        chatBubble.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #FF9800;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: pointer;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        
        chatBubble.addEventListener('click', () => {
            alert('Chat clicked! CORA is here to help.');
        });
        
        document.body.appendChild(chatBubble);
        // console.log('✅ Created emergency chat bubble');
    }
}

// Run checks after page loads
document.addEventListener('DOMContentLoaded', () => {
    // console.log('🔍 DOM loaded, checking chat...');
    setTimeout(() => {
        const status = checkChatElements();
        
        if (!status.chatBubble) {
            // console.log('🚨 No chat bubble found, creating emergency one...');
            createChatIfMissing();
        }
        
        // Make debug functions available globally
        window.debugChat = {
            check: checkChatElements,
            forceShow: forceShowChat,
            create: createChatIfMissing
        };
        
        // console.log('🔧 Debug functions available: window.debugChat.check(), window.debugChat.forceShow(), window.debugChat.create()');
    }, 2000);
});

// Also check after a longer delay
setTimeout(() => {
    // console.log('🔍 Delayed check...');
    checkChatElements();
}, 5000); 