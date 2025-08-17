// CORA Personality Demo - External JavaScript
// Handles demo functionality without inline scripts

// Demo data to make CORA more engaging
window.demoData = {
    profitScore: 82,
    recentExpenses: [
        { amount: 1250, vendor: "ABC Supply", date: new Date() },
        { amount: 850, vendor: "Quality Materials", date: new Date() }
    ],
    profitTrend: 5.2
};

// Launch CORA function
function launchCORA() {
    // console.log("🚀 Launching CORA Personality Demo...");
    
    try {
        // Check if CORAPersonality class exists
        if (typeof window.CORAPersonality === 'undefined') {
            // console.error("❌ CORAPersonality class not found!");
            alert("CORA Personality system not loaded. Please refresh the page and try again.");
            return;
        }
        
        // console.log("✅ CORAPersonality class found, initializing...");
        
        // Initialize CORA Personality
        window.coraPersonality = new CORAPersonality();
        // console.log("✅ CORA Personality initialized successfully");
        
        // Show a welcome message after a short delay
        setTimeout(() => {
            if (window.coraPersonality) {
                // console.log("📱 Showing chat interface...");
                window.coraPersonality.showChat();
                
                // console.log("💬 Adding welcome message...");
                window.coraPersonality.addChatMessage("Hey there! 👋 I'm CORA, and I'm excited to show you my new AI-powered personality! I'm not just a chatbot anymore - I have real intelligence, I remember our conversations, and I genuinely care about your business success. What would you like to explore?", 'cora');
                
                // Add a follow-up message to demonstrate AI capabilities
                setTimeout(() => {
                    window.coraPersonality.addChatMessage("I'm now powered by real AI! Try asking me anything about your business, profits, or just chat with me naturally. I'll give you intelligent, contextual responses! 🚀", 'cora');
                }, 2000);
            } else {
                // console.error("❌ coraPersonality instance not found after initialization");
            }
        }, 1000);
        
    } catch (error) {
        // console.error("💥 Error initializing CORA Personality:", error);
        alert("Error initializing CORA Personality: " + error.message);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // console.log("🎯 CORA Personality Demo DOM loaded");
    
    // Add event listener to launch button
    const launchBtn = document.getElementById('launchCoraBtn');
    if (launchBtn) {
        // console.log("✅ Launch button found, adding event listener");
        launchBtn.addEventListener('click', function(e) {
            // console.log("🖱️ Launch button clicked!");
            e.preventDefault();
            launchCORA();
        });
    } else {
        // console.error("❌ Launch button not found!");
    }
    
    // console.log("🎉 CORA Personality Demo ready!");
}); 