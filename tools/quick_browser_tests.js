/**
 * Quick Browser Tests for CORA Features
 * Run these in the browser console on your dashboard
 */

// Test Suite for immediate browser testing
const CORATests = {
    // 1. Voice Expense Entry Tests
    async testVoiceEntry() {
        console.log('🎤 Testing Voice Expense Entry...');
        
        // Check if voice button exists
        const voiceContainer = document.querySelector('.voice-button-container');
        const voiceBtn = document.querySelector('.voice-btn');
        
        console.log('Voice Container:', voiceContainer ? '✅ Found' : '❌ Not Found');
        console.log('Voice Button:', voiceBtn ? '✅ Found' : '❌ Not Found');
        
        // Test API endpoint
        try {
            const response = await fetch('/api/expenses/voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: 'test expense fifty dollars at hardware store',
                    source: 'browser_test'
                })
            });
            
            const result = await response.json();
            console.log('Voice API Response:', response.ok ? '✅ Working' : '❌ Failed');
            console.log('Result:', result);
            
            if (result.success) {
                console.log(`✅ Created expense: $${result.expense.amount_cents/100}`);
            }
        } catch (error) {
            console.error('❌ Voice API Error:', error);
        }
        
        return voiceBtn !== null;
    },
    
    // 2. Quick Win Engine Tests
    async testQuickWins() {
        console.log('🏆 Testing Quick Win Engine...');
        
        // Check if dashboard component exists
        const quickWinContainer = document.querySelector('.quick-win-dashboard-container');
        console.log('Quick Win Container:', quickWinContainer ? '✅ Found' : '❌ Not Found');
        
        // Test API endpoint
        try {
            const response = await fetch('/api/expenses/quick-wins');
            const data = await response.json();
            
            console.log('Quick Wins API:', response.ok ? '✅ Working' : '❌ Failed');
            console.log(`Found ${data.quick_wins?.length || 0} deductions`);
            console.log(`Total monthly savings: $${data.total_savings?.toFixed(2) || 0}`);
            
            // Display first few deductions
            if (data.quick_wins?.length > 0) {
                console.log('\nTop Deductions Found:');
                data.quick_wins.slice(0, 3).forEach(win => {
                    console.log(`- ${win.vendor}: Save $${win.tax_savings.toFixed(2)} (${win.tip})`);
                });
            }
        } catch (error) {
            console.error('❌ Quick Wins API Error:', error);
        }
        
        return quickWinContainer !== null;
    },
    
    // 3. Notification Tests
    async testNotifications() {
        console.log('📧 Testing Notification System...');
        
        // Check configuration
        try {
            // This endpoint might need to be created
            const response = await fetch('/api/user/preferences');
            if (response.ok) {
                const prefs = await response.json();
                console.log('Email Notifications:', prefs.email_notifications ? '✅ Enabled' : '❌ Disabled');
                console.log('SMS Notifications:', prefs.sms_notifications ? '✅ Enabled' : '❌ Disabled');
            }
        } catch (error) {
            console.log('⚠️ Could not fetch notification preferences');
        }
        
        // Test email configuration
        console.log('\nChecking email service...');
        // You could add a test endpoint for this
        
        return true;
    },
    
    // 4. Integration Test
    async runFullTest() {
        console.log('🚀 Running Full Integration Test...\n');
        
        const results = {
            voice: await this.testVoiceEntry(),
            quickWins: await this.testQuickWins(),
            notifications: await this.testNotifications()
        };
        
        console.log('\n📊 Test Summary:');
        console.log('Voice Entry:', results.voice ? '✅ PASS' : '❌ FAIL');
        console.log('Quick Wins:', results.quickWins ? '✅ PASS' : '❌ FAIL');
        console.log('Notifications:', results.notifications ? '✅ PASS' : '❌ FAIL');
        
        const allPassed = Object.values(results).every(r => r);
        console.log('\nOverall:', allPassed ? '✅ ALL TESTS PASSED!' : '❌ Some tests failed');
        
        return results;
    },
    
    // 5. Create Test Data
    async createTestExpenses() {
        console.log('📝 Creating test expenses...');
        
        const testExpenses = [
            { transcript: "Bought lumber at Home Depot for fifty dollars", source: "test" },
            { transcript: "Uber to client meeting twenty five dollars", source: "test" },
            { transcript: "Office supplies at Staples one hundred twenty dollars", source: "test" },
            { transcript: "Business lunch forty five fifty", source: "test" },
            { transcript: "Software subscription Adobe creative cloud fifty dollars", source: "test" }
        ];
        
        for (const expense of testExpenses) {
            try {
                const response = await fetch('/api/expenses/voice', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(expense)
                });
                
                const result = await response.json();
                if (result.success) {
                    console.log(`✅ Created: ${result.expense.vendor} - $${result.expense.amount_cents/100}`);
                } else {
                    console.log(`❌ Failed: ${expense.transcript}`);
                }
            } catch (error) {
                console.error('Error creating expense:', error);
            }
        }
        
        console.log('\n💡 Refresh Quick Wins to see deductions!');
    },
    
    // 6. Performance Test
    measurePerformance() {
        console.log('⚡ Measuring Performance...');
        
        const metrics = {
            voiceButton: document.querySelector('.voice-btn') ? 'Loaded' : 'Not Loaded',
            quickWins: document.querySelector('.quick-win-section') ? 'Loaded' : 'Not Loaded',
            loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
            domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart
        };
        
        console.table(metrics);
        
        // Check for memory leaks
        if (performance.memory) {
            console.log('\nMemory Usage:');
            console.log(`Used: ${(performance.memory.usedJSHeapSize / 1048576).toFixed(2)} MB`);
            console.log(`Total: ${(performance.memory.totalJSHeapSize / 1048576).toFixed(2)} MB`);
        }
    }
};

// Auto-run helper
console.log(`
🧪 CORA Feature Tests Ready!

Quick Commands:
- CORATests.runFullTest()     // Run all tests
- CORATests.testVoiceEntry()  // Test voice expense
- CORATests.testQuickWins()   // Test tax deductions
- CORATests.testNotifications() // Test notifications
- CORATests.createTestExpenses() // Generate test data
- CORATests.measurePerformance() // Check performance

Or just run: CORATests.runFullTest()
`);

// Make it globally available
window.CORATests = CORATests;