/**
 * Construction Expense Categories
 * Comprehensive categorization system for construction contractors
 */

class ConstructionCategories {
    constructor() {
        this.categories = {
            // Materials
            materials: {
                hardware: {
                    name: 'Materials - Hardware',
                    keywords: ['hardware', 'nails', 'screws', 'bolts', 'nuts', 'washers', 'hinges', 'locks', 'handles', 'brackets', 'fasteners', 'anchors', 'drywall screws', 'deck screws', 'lag bolts'],
                    vendors: ['home depot', 'lowes', 'menards', 'ace hardware', 'true value'],
                    icon: '🔨'
                },
                lumber: {
                    name: 'Materials - Lumber',
                    keywords: ['lumber', 'wood', 'plywood', 'osb', '2x4', '2x6', '2x8', '2x10', '2x12', '4x4', '4x6', 'boards', 'studs', 'joists', 'beams', 'posts', 'decking', 'siding', 'trim', 'molding'],
                    vendors: ['lumber yard', 'home depot', 'lowes', 'menards', '84 lumber'],
                    icon: '🪵'
                },
                electrical: {
                    name: 'Materials - Electrical',
                    keywords: ['wire', 'cable', 'outlet', 'switch', 'breaker', 'electrical', 'conduit', 'junction box', 'light fixture', 'ceiling fan', 'smoke detector', 'gfci', 'receptacle', 'panel'],
                    vendors: ['electrical supply', 'home depot', 'lowes', 'menards', 'grainger'],
                    icon: '⚡'
                },
                plumbing: {
                    name: 'Materials - Plumbing',
                    keywords: ['pipe', 'fitting', 'valve', 'plumbing', 'pvc', 'copper', 'pex', 'faucet', 'sink', 'toilet', 'shower', 'drain', 'vent', 'water heater', 'pump'],
                    vendors: ['plumbing supply', 'home depot', 'lowes', 'menards', 'ferguson'],
                    icon: '🚰'
                },
                hvac: {
                    name: 'Materials - HVAC',
                    keywords: ['duct', 'vent', 'hvac', 'furnace', 'ac', 'air conditioner', 'thermostat', 'filter', 'blower', 'compressor', 'refrigerant'],
                    vendors: ['hvac supply', 'home depot', 'lowes', 'grainger'],
                    icon: '❄️'
                },
                roofing: {
                    name: 'Materials - Roofing',
                    keywords: ['shingle', 'roofing', 'underlayment', 'flashing', 'drip edge', 'ridge cap', 'ice shield', 'tar paper', 'felt', 'metal roof'],
                    vendors: ['roofing supply', 'home depot', 'lowes', 'menards'],
                    icon: '🏠'
                },
                concrete: {
                    name: 'Materials - Concrete',
                    keywords: ['concrete', 'cement', 'rebar', 'wire mesh', 'form', 'masonry', 'block', 'brick', 'mortar', 'grout', 'sand', 'gravel'],
                    vendors: ['concrete supply', 'home depot', 'lowes', 'quikrete'],
                    icon: '🧱'
                },
                paint: {
                    name: 'Materials - Paint',
                    keywords: ['paint', 'primer', 'stain', 'varnish', 'caulk', 'sealant', 'brush', 'roller', 'drop cloth', 'tape', 'spray paint'],
                    vendors: ['sherwin williams', 'benjamin moore', 'home depot', 'lowes', 'menards'],
                    icon: '🎨'
                },
                insulation: {
                    name: 'Materials - Insulation',
                    keywords: ['insulation', 'fiberglass', 'foam', 'batt', 'roll', 'spray foam', 'vapor barrier', 'house wrap', 'tyvek'],
                    vendors: ['home depot', 'lowes', 'menards', 'insulation supply'],
                    icon: '🧶'
                },
                flooring: {
                    name: 'Materials - Flooring',
                    keywords: ['flooring', 'tile', 'carpet', 'hardwood', 'laminate', 'vinyl', 'linoleum', 'grout', 'thinset', 'underlayment', 'baseboard'],
                    vendors: ['flooring supply', 'home depot', 'lowes', 'menards'],
                    icon: '🏗️'
                }
            },
            
            // Labor
            labor: {
                crew: {
                    name: 'Labor - Crew',
                    keywords: ['crew', 'labor', 'worker', 'helper', 'apprentice', 'journeyman', 'overtime', 'bonus', 'meal', 'lunch', 'breakfast', 'dinner'],
                    vendors: ['crew', 'labor', 'workers'],
                    icon: '👷'
                },
                subcontractor: {
                    name: 'Labor - Subcontractors',
                    keywords: ['subcontractor', 'sub', 'contractor', 'electrician', 'plumber', 'hvac', 'roofer', 'painter', 'drywall', 'flooring', 'mason'],
                    vendors: ['subcontractor', 'sub', 'contractor'],
                    icon: '👨‍🔧'
                },
                professional: {
                    name: 'Labor - Professional Services',
                    keywords: ['architect', 'engineer', 'inspector', 'surveyor', 'lawyer', 'accountant', 'consultant', 'designer'],
                    vendors: ['professional services'],
                    icon: '👔'
                }
            },
            
            // Equipment
            equipment: {
                rental: {
                    name: 'Equipment - Rental',
                    keywords: ['rental', 'rent', 'excavator', 'backhoe', 'skid steer', 'forklift', 'scaffold', 'ladder', 'generator', 'compressor', 'jackhammer', 'concrete mixer'],
                    vendors: ['equipment rental', 'sunbelt', 'united rentals', 'herc rentals', 'cat rental'],
                    icon: '🚜'
                },
                fuel: {
                    name: 'Equipment - Fuel',
                    keywords: ['gas', 'diesel', 'fuel', 'propane', 'oil', 'lubricant', 'grease'],
                    vendors: ['gas station', 'shell', 'exxon', 'mobil', 'chevron', 'bp'],
                    icon: '⛽'
                },
                maintenance: {
                    name: 'Equipment - Maintenance',
                    keywords: ['maintenance', 'repair', 'service', 'parts', 'filter', 'oil change', 'tire', 'battery', 'blade', 'bit', 'tool'],
                    vendors: ['equipment service', 'dealer', 'repair shop'],
                    icon: '🔧'
                }
            },
            
            // Transportation
            transportation: {
                vehicle: {
                    name: 'Transportation - Vehicle',
                    keywords: ['truck', 'van', 'trailer', 'vehicle', 'mileage', 'gas', 'diesel', 'toll', 'parking', 'registration', 'insurance'],
                    vendors: ['gas station', 'dmv', 'insurance'],
                    icon: '🚛'
                },
                delivery: {
                    name: 'Transportation - Delivery',
                    keywords: ['delivery', 'shipping', 'freight', 'hauling', 'dumpster', 'porta potty', 'storage'],
                    vendors: ['delivery service', 'freight', 'hauling'],
                    icon: '📦'
                }
            },
            
            // Permits & Fees
            permits: {
                building: {
                    name: 'Permits & Fees - Building',
                    keywords: ['permit', 'building permit', 'electrical permit', 'plumbing permit', 'hvac permit', 'roofing permit', 'inspection', 'fee'],
                    vendors: ['city hall', 'building department', 'permit office'],
                    icon: '📋'
                },
                utility: {
                    name: 'Permits & Fees - Utility',
                    keywords: ['utility', 'water', 'sewer', 'electric', 'gas', 'connection', 'hookup', 'meter', 'deposit'],
                    vendors: ['utility company', 'water company', 'electric company'],
                    icon: '🔌'
                }
            },
            
            // Office & Admin
            office: {
                supplies: {
                    name: 'Office - Supplies',
                    keywords: ['office', 'supplies', 'paper', 'ink', 'toner', 'pen', 'pencil', 'notebook', 'folder', 'tape', 'stapler'],
                    vendors: ['office depot', 'staples', 'walmart', 'target'],
                    icon: '📄'
                },
                software: {
                    name: 'Office - Software',
                    keywords: ['software', 'license', 'subscription', 'app', 'program', 'cad', 'design', 'accounting'],
                    vendors: ['software company', 'subscription service'],
                    icon: '💻'
                }
            },
            
            // Insurance & Legal
            insurance: {
                general: {
                    name: 'Insurance & Legal',
                    keywords: ['insurance', 'liability', 'workers comp', 'bond', 'legal', 'lawyer', 'attorney', 'court', 'filing'],
                    vendors: ['insurance company', 'law firm', 'attorney'],
                    icon: '🛡️'
                }
            },
            
            // Marketing & Sales
            marketing: {
                advertising: {
                    name: 'Marketing & Sales',
                    keywords: ['marketing', 'advertising', 'sign', 'business card', 'website', 'listing', 'referral', 'commission'],
                    vendors: ['marketing company', 'sign company', 'web designer'],
                    icon: '📢'
                }
            }
        };
        
        this.vendorMappings = this.buildVendorMappings();
    }
    
    /**
     * Build vendor to category mappings
     */
    buildVendorMappings() {
        const mappings = {};
        
        // Iterate through all categories and their vendors
        Object.values(this.categories).forEach(categoryGroup => {
            Object.values(categoryGroup).forEach(category => {
                category.vendors.forEach(vendor => {
                    mappings[vendor.toLowerCase()] = category.name;
                });
            });
        });
        
        return mappings;
    }
    
    /**
     * Categorize expense based on transcript
     */
    categorizeExpense(transcript, vendor = null) {
        const text = transcript.toLowerCase();
        let bestMatch = null;
        let bestScore = 0;
        
        // First, try vendor-based categorization
        if (vendor && this.vendorMappings[vendor.toLowerCase()]) {
            return this.vendorMappings[vendor.toLowerCase()];
        }
        
        // Then, try keyword-based categorization
        Object.values(this.categories).forEach(categoryGroup => {
            Object.values(categoryGroup).forEach(category => {
                const score = this.calculateKeywordScore(text, category.keywords);
                if (score > bestScore) {
                    bestScore = score;
                    bestMatch = category.name;
                }
            });
        });
        
        return bestMatch || 'Materials - Other';
    }
    
    /**
     * Calculate keyword match score
     */
    calculateKeywordScore(text, keywords) {
        let score = 0;
        keywords.forEach(keyword => {
            if (text.includes(keyword.toLowerCase())) {
                score += 1;
            }
        });
        return score;
    }
    
    /**
     * Get all categories for dropdown/selection
     */
    getAllCategories() {
        const allCategories = [];
        
        Object.values(this.categories).forEach(categoryGroup => {
            Object.values(categoryGroup).forEach(category => {
                allCategories.push({
                    name: category.name,
                    icon: category.icon,
                    keywords: category.keywords.slice(0, 3) // First 3 keywords for display
                });
            });
        });
        
        // Sort alphabetically
        return allCategories.sort((a, b) => a.name.localeCompare(b.name));
    }
    
    /**
     * Get categories by group
     */
    getCategoriesByGroup() {
        return this.categories;
    }
    
    /**
     * Get common vendors for a category
     */
    getVendorsForCategory(categoryName) {
        for (const categoryGroup of Object.values(this.categories)) {
            for (const category of Object.values(categoryGroup)) {
                if (category.name === categoryName) {
                    return category.vendors;
                }
            }
        }
        return [];
    }
    
    /**
     * Get category icon
     */
    getCategoryIcon(categoryName) {
        for (const categoryGroup of Object.values(this.categories)) {
            for (const category of Object.values(categoryGroup)) {
                if (category.name === categoryName) {
                    return category.icon;
                }
            }
        }
        return '📁'; // Default icon
    }
    
    /**
     * Suggest categories based on partial input
     */
    suggestCategories(input) {
        const suggestions = [];
        const inputLower = input.toLowerCase();
        
        Object.values(this.categories).forEach(categoryGroup => {
            Object.values(categoryGroup).forEach(category => {
                // Check if input matches category name
                if (category.name.toLowerCase().includes(inputLower)) {
                    suggestions.push({
                        name: category.name,
                        icon: category.icon,
                        matchType: 'name'
                    });
                }
                // Check if input matches keywords
                else if (category.keywords.some(keyword => keyword.toLowerCase().includes(inputLower))) {
                    suggestions.push({
                        name: category.name,
                        icon: category.icon,
                        matchType: 'keyword'
                    });
                }
            });
        });
        
        // Sort by match type (name matches first) then alphabetically
        return suggestions.sort((a, b) => {
            if (a.matchType !== b.matchType) {
                return a.matchType === 'name' ? -1 : 1;
            }
            return a.name.localeCompare(b.name);
        }).slice(0, 5); // Return top 5 suggestions
    }
    
    /**
     * Get construction-specific expense tips
     */
    getExpenseTips() {
        return {
            materials: [
                'Always specify the job when buying materials',
                'Keep receipts for warranty claims',
                'Consider bulk discounts for large projects',
                'Track material waste for future estimates'
            ],
            labor: [
                'Document hours worked for each job',
                'Include meal allowances in labor costs',
                'Track overtime separately',
                'Keep subcontractor agreements on file'
            ],
            equipment: [
                'Compare rental vs. purchase costs',
                'Track equipment hours for maintenance',
                'Include fuel costs with equipment',
                'Consider equipment sharing with other contractors'
            ],
            permits: [
                'Apply for permits well in advance',
                'Keep permit costs separate by job',
                'Track inspection fees separately',
                'Include permit costs in job estimates'
            ]
        };
    }
    
    /**
     * Generate expense report categories
     */
    getReportCategories() {
        return {
            'Materials': [
                'Materials - Hardware',
                'Materials - Lumber',
                'Materials - Electrical',
                'Materials - Plumbing',
                'Materials - HVAC',
                'Materials - Roofing',
                'Materials - Concrete',
                'Materials - Paint',
                'Materials - Insulation',
                'Materials - Flooring'
            ],
            'Labor': [
                'Labor - Crew',
                'Labor - Subcontractors',
                'Labor - Professional Services'
            ],
            'Equipment': [
                'Equipment - Rental',
                'Equipment - Fuel',
                'Equipment - Maintenance'
            ],
            'Transportation': [
                'Transportation - Vehicle',
                'Transportation - Delivery'
            ],
            'Permits & Fees': [
                'Permits & Fees - Building',
                'Permits & Fees - Utility'
            ],
            'Office & Admin': [
                'Office - Supplies',
                'Office - Software'
            ],
            'Other': [
                'Insurance & Legal',
                'Marketing & Sales'
            ]
        };
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConstructionCategories;
} 