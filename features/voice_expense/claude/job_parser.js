// Job name extraction for construction voice expenses
// Enhances existing parseExpense() method

const JOB_PATTERNS = [
    // "for the Johnson bathroom job"
    /for (?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:job|project)/i,
    
    // "on the Smith kitchen"
    /on (?:the )?([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:job|project|bathroom|kitchen|house|roof|deck)/i,
    
    // "Johnson bathroom" or "Smith kitchen" 
    /([a-zA-Z]+)\s+(bathroom|kitchen|house|roof|deck|basement|garage|addition|remodel)/i,
    
    // "downtown office job"
    /([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:job|project)(?:\s|$)/i
];

// Construction-specific vendor mappings
const CONSTRUCTION_VENDORS = {
    'home depot': { category: 'Materials - Hardware', common: true },
    'lowes': { category: 'Materials - Hardware', common: true },
    'menards': { category: 'Materials - Hardware', common: true },
    'ace hardware': { category: 'Materials - Hardware', common: true },
    'lumber yard': { category: 'Materials - Lumber', common: true },
    'electrical supply': { category: 'Materials - Electrical', common: true },
    'plumbing supply': { category: 'Materials - Plumbing', common: true },
    'gas station': { category: 'Equipment - Fuel', common: true },
    'equipment rental': { category: 'Equipment - Rental', common: true }
};

// Enhanced parseExpense method
function parseExpenseEnhanced(transcript) {
    const text = transcript.toLowerCase();
    
    // Extract job name
    let jobName = null;
    for (const pattern of JOB_PATTERNS) {
        const match = text.match(pattern);
        if (match) {
            jobName = match[1].trim();
            // Capitalize first letters
            jobName = jobName.split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            break;
        }
    }
    
    // Extract amount (improved)
    const amountPatterns = [
        /\$(\d+(?:\.\d{2})?)/,  // $123.45
        /(\d+(?:\.\d{2})?)\s*dollars?/i,  // 123 dollars
        /(\d+)\s*(?:bucks?|dollars?)/i,  // 45 bucks
        /(?:^|\s)(\d+(?:\.\d{2})?)(?:\s|$)/  // standalone number
    ];
    
    let amount = null;
    for (const pattern of amountPatterns) {
        const match = text.match(pattern);
        if (match) {
            amount = parseFloat(match[1]);
            break;
        }
    }
    
    // Handle word numbers
    const wordNumbers = {
        'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
        'hundred': 100, 'thousand': 1000
    };
    
    if (!amount) {
        for (const [word, value] of Object.entries(wordNumbers)) {
            if (text.includes(word)) {
                amount = value;
                break;
            }
        }
    }
    
    // Extract vendor with construction awareness
    let vendor = 'Unknown';
    let category = 'Materials - Other';
    
    // Check known construction vendors
    for (const [vendorName, info] of Object.entries(CONSTRUCTION_VENDORS)) {
        if (text.includes(vendorName)) {
            vendor = vendorName.split(' ')
                .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                .join(' ');
            category = info.category;
            break;
        }
    }
    
    // If no known vendor, try patterns
    if (vendor === 'Unknown') {
        const vendorPatterns = [
            /(?:at|from)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)(?:\s+for|\s+on|\s|$)/i,
            /([a-zA-Z]+(?:\s+[a-zA-Z]+)*?)\s+(?:receipt|purchase)/i
        ];
        
        for (const pattern of vendorPatterns) {
            const match = text.match(pattern);
            if (match) {
                vendor = match[1].trim();
                vendor = vendor.split(' ')
                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(' ');
                break;
            }
        }
    }
    
    // Auto-categorize based on keywords
    const categoryKeywords = {
        'Materials - Lumber': ['lumber', 'wood', 'plywood', '2x4', '2x6', 'boards'],
        'Materials - Electrical': ['wire', 'outlet', 'breaker', 'electrical'],
        'Materials - Plumbing': ['pipe', 'fitting', 'valve', 'plumbing'],
        'Equipment - Fuel': ['gas', 'diesel', 'fuel'],
        'Labor - Crew': ['lunch', 'food', 'meal', 'crew'],
        'Labor - Subcontractors': ['subcontractor', 'sub', 'contractor']
    };
    
    for (const [cat, keywords] of Object.entries(categoryKeywords)) {
        if (keywords.some(keyword => text.includes(keyword))) {
            category = cat;
            break;
        }
    }
    
    return {
        amount,
        vendor,
        category,
        jobName,
        description: transcript,
        confidence: {
            amount: amount ? 0.9 : 0,
            vendor: vendor !== 'Unknown' ? 0.95 : 0.3,
            job: jobName ? 0.9 : 0,
            category: 0.85
        }
    };
}

// Export for integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { parseExpenseEnhanced, JOB_PATTERNS, CONSTRUCTION_VENDORS };
}