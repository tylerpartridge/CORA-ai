// Integration code to add job parsing to existing voice system
// This shows how to modify voice_onboarding.js

// Add this to the existing parseExpense method in voice_onboarding.js:

// Import job patterns at top of file
// import { parseExpenseEnhanced } from '/features/voice_expense/claude/job_parser.js';

// Replace the existing parseExpense method with:
parseExpense(transcript) {
    // Use enhanced parser
    const result = parseExpenseEnhanced(transcript);
    
    if (!result.amount) {
        this.showError('Could not detect amount. Please try again.');
        return null;
    }
    
    // Format for existing system
    return {
        amount: result.amount,
        vendor: result.vendor,
        category: result.category,
        job_name: result.jobName,  // NEW FIELD
        description: result.description,
        deductionInfo: {
            rate: result.category.includes('Materials') ? 1.0 : 0.5,
            tip: result.jobName 
                ? `Job expense for ${result.jobName} - fully deductible`
                : 'Business expense - may be deductible',
            category: result.category
        },
        timestamp: new Date(),
        context: this.context,
        confidence: result.confidence  // NEW FIELD
    };
}