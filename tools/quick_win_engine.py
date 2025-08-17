#!/usr/bin/env python3
"""
Quick Win Engine - Intelligent Deduction Discovery
Finds tax savings opportunities in user expenses to create "aha!" moments
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class DeductionPattern:
    """Represents a deduction pattern"""
    category: str
    deduction_rate: float  # 0.0 to 1.0 (percentage deductible)
    keywords: List[str]
    tip: str
    irs_category: str
    annual_limit: Optional[float] = None

@dataclass
class QuickWin:
    """Represents a found deduction opportunity"""
    expense_amount: float
    deduction_amount: float
    tax_savings: float
    annual_savings: float
    tip: str
    category: str
    confidence: str  # 'high', 'medium', 'low'
    celebration_level: str  # 'small', 'medium', 'large'


class QuickWinEngine:
    """Intelligent engine for finding tax deductions in expenses"""
    
    def __init__(self, user_tax_rate: float = 0.25):
        self.user_tax_rate = user_tax_rate
        self.deduction_patterns = self._load_deduction_patterns()
        self.vendor_mappings = self._load_vendor_mappings()
        
    def _load_deduction_patterns(self) -> Dict[str, DeductionPattern]:
        """Load comprehensive deduction patterns"""
        return {
            # Meals & Entertainment
            'business_meal': DeductionPattern(
                category='Meals & Entertainment',
                deduction_rate=0.5,
                keywords=['lunch', 'dinner', 'breakfast', 'meal', 'restaurant', 'cafe', 'diner'],
                tip='Business meals are 50% deductible when discussing business',
                irs_category='meals_entertainment'
            ),
            'client_entertainment': DeductionPattern(
                category='Client Entertainment',
                deduction_rate=1.0,
                keywords=['client', 'customer', 'prospect', 'meeting', 'entertainment'],
                tip='Client entertainment expenses are 100% deductible!',
                irs_category='client_entertainment'
            ),
            'coffee_meeting': DeductionPattern(
                category='Business Meetings',
                deduction_rate=0.5,
                keywords=['coffee', 'starbucks', 'dunkin', 'cafe', 'espresso', 'latte'],
                tip='Coffee meetings are 50% deductible when discussing business',
                irs_category='meals_entertainment'
            ),
            
            # Transportation
            'business_travel': DeductionPattern(
                category='Transportation',
                deduction_rate=1.0,
                keywords=['uber', 'lyft', 'taxi', 'ride', 'airport', 'flight', 'hotel'],
                tip='Business travel is 100% deductible - keep those receipts!',
                irs_category='travel'
            ),
            'vehicle_expenses': DeductionPattern(
                category='Auto Expenses',
                deduction_rate=1.0,
                keywords=['gas', 'fuel', 'parking', 'toll', 'car', 'maintenance', 'oil change'],
                tip='Track mileage for maximum deductions - $0.655/mile in 2023',
                irs_category='vehicle'
            ),
            
            # Office & Equipment
            'office_supplies': DeductionPattern(
                category='Office Supplies',
                deduction_rate=1.0,
                keywords=['supplies', 'staples', 'office depot', 'paper', 'pens', 'printer', 'ink'],
                tip='Office supplies are 100% deductible business expenses',
                irs_category='supplies'
            ),
            'technology': DeductionPattern(
                category='Technology & Equipment',
                deduction_rate=1.0,
                keywords=['computer', 'laptop', 'software', 'app', 'subscription', 'adobe', 'microsoft'],
                tip='Technology expenses are fully deductible for business use',
                irs_category='equipment'
            ),
            'home_office': DeductionPattern(
                category='Home Office',
                deduction_rate=0.3,  # Assumes 30% business use
                keywords=['internet', 'phone', 'utilities', 'rent', 'mortgage'],
                tip='Deduct the business portion of your home office expenses',
                irs_category='home_office'
            ),
            
            # Professional Development
            'education': DeductionPattern(
                category='Professional Development',
                deduction_rate=1.0,
                keywords=['course', 'training', 'conference', 'workshop', 'book', 'seminar', 'webinar'],
                tip='Professional development that maintains or improves job skills is 100% deductible',
                irs_category='education'
            ),
            'memberships': DeductionPattern(
                category='Professional Memberships',
                deduction_rate=1.0,
                keywords=['membership', 'association', 'chamber', 'guild', 'union', 'professional'],
                tip='Professional organization memberships are fully deductible',
                irs_category='dues'
            ),
            
            # Marketing & Advertising
            'advertising': DeductionPattern(
                category='Marketing & Advertising',
                deduction_rate=1.0,
                keywords=['ads', 'advertising', 'marketing', 'promotion', 'facebook', 'google', 'instagram'],
                tip='Marketing expenses are 100% deductible - invest in growing your business!',
                irs_category='advertising'
            ),
            'business_cards': DeductionPattern(
                category='Marketing Materials',
                deduction_rate=1.0,
                keywords=['business cards', 'flyers', 'brochures', 'printing', 'design'],
                tip='Marketing materials are fully deductible business expenses',
                irs_category='advertising'
            ),
            
            # Professional Services
            'professional_fees': DeductionPattern(
                category='Professional Services',
                deduction_rate=1.0,
                keywords=['lawyer', 'attorney', 'accountant', 'cpa', 'consultant', 'freelancer'],
                tip='Professional service fees for your business are 100% deductible',
                irs_category='professional_services'
            ),
            'insurance': DeductionPattern(
                category='Business Insurance',
                deduction_rate=1.0,
                keywords=['insurance', 'liability', 'errors', 'omissions', 'business insurance'],
                tip='Business insurance premiums are fully deductible',
                irs_category='insurance'
            )
        }
    
    def _load_vendor_mappings(self) -> Dict[str, str]:
        """Map common vendors to categories"""
        return {
            # Food & Dining
            'starbucks': 'coffee_meeting',
            'dunkin': 'coffee_meeting',
            'mcdonalds': 'business_meal',
            'subway': 'business_meal',
            'chipotle': 'business_meal',
            
            # Transportation
            'uber': 'business_travel',
            'lyft': 'business_travel',
            'united': 'business_travel',
            'american airlines': 'business_travel',
            'hertz': 'business_travel',
            'enterprise': 'business_travel',
            
            # Office Supplies
            'staples': 'office_supplies',
            'office depot': 'office_supplies',
            'amazon': 'office_supplies',  # Could be multiple categories
            'best buy': 'technology',
            
            # Software
            'adobe': 'technology',
            'microsoft': 'technology',
            'zoom': 'technology',
            'dropbox': 'technology',
            'google': 'technology',
            
            # Services
            'godaddy': 'technology',
            'squarespace': 'technology',
            'mailchimp': 'advertising',
            'canva': 'advertising',
            'fiverr': 'professional_fees',
            'upwork': 'professional_fees'
        }
    
    def find_quick_win(self, expense_description: str, amount: float, 
                      vendor: Optional[str] = None) -> Optional[QuickWin]:
        """Find deduction opportunity in an expense"""
        # Normalize text
        text = expense_description.lower()
        if vendor:
            text += f" {vendor.lower()}"
        
        # First, try vendor mapping
        pattern_key = None
        if vendor:
            vendor_lower = vendor.lower()
            for vendor_pattern, category_key in self.vendor_mappings.items():
                if vendor_pattern in vendor_lower:
                    pattern_key = category_key
                    break
        
        # If no vendor match, search keywords
        if not pattern_key:
            for key, pattern in self.deduction_patterns.items():
                if any(keyword in text for keyword in pattern.keywords):
                    pattern_key = key
                    break
        
        # If still no match, check for business indicators
        if not pattern_key:
            business_indicators = ['business', 'work', 'client', 'meeting', 'conference']
            if any(indicator in text for indicator in business_indicators):
                # Default to partially deductible business expense
                pattern_key = 'business_meal'  # Conservative default
        
        if pattern_key:
            pattern = self.deduction_patterns[pattern_key]
            return self._calculate_quick_win(amount, pattern)
        
        # No clear deduction found
        return None
    
    def _calculate_quick_win(self, amount: float, pattern: DeductionPattern) -> QuickWin:
        """Calculate the tax savings from a deduction"""
        deduction_amount = amount * pattern.deduction_rate
        tax_savings = deduction_amount * self.user_tax_rate
        
        # Assume this is a recurring expense (weekly)
        annual_savings = tax_savings * 52
        
        # Determine celebration level
        if tax_savings >= 50:
            celebration_level = 'large'
            confidence = 'high'
        elif tax_savings >= 10:
            celebration_level = 'medium'
            confidence = 'high' if pattern.deduction_rate == 1.0 else 'medium'
        else:
            celebration_level = 'small'
            confidence = 'medium'
        
        return QuickWin(
            expense_amount=amount,
            deduction_amount=deduction_amount,
            tax_savings=tax_savings,
            annual_savings=annual_savings,
            tip=pattern.tip,
            category=pattern.category,
            confidence=confidence,
            celebration_level=celebration_level
        )
    
    def analyze_expense_batch(self, expenses: List[Dict]) -> Dict:
        """Analyze a batch of expenses for deduction opportunities"""
        total_deductions = 0
        total_tax_savings = 0
        missed_opportunities = []
        found_deductions = []
        
        for expense in expenses:
            quick_win = self.find_quick_win(
                expense.get('description', ''),
                expense.get('amount', 0),
                expense.get('vendor')
            )
            
            if quick_win:
                found_deductions.append({
                    'expense': expense,
                    'quick_win': quick_win
                })
                total_deductions += quick_win.deduction_amount
                total_tax_savings += quick_win.tax_savings
            else:
                # Check if this might be deductible with more info
                if expense.get('amount', 0) > 20:  # Significant expense
                    missed_opportunities.append(expense)
        
        return {
            'total_deductions': total_deductions,
            'total_tax_savings': total_tax_savings,
            'annual_tax_savings': total_tax_savings * 52,
            'found_deductions': found_deductions,
            'missed_opportunities': missed_opportunities,
            'deduction_rate': (total_deductions / sum(e.get('amount', 0) for e in expenses)) if expenses else 0
        }
    
    def get_personalized_tips(self, user_business_type: str) -> List[str]:
        """Get personalized deduction tips based on business type"""
        tips_by_type = {
            'consultant': [
                "Track all client meeting expenses - they're 100% deductible!",
                "Your home office can save you thousands in deductions",
                "Professional development courses are fully deductible"
            ],
            'freelancer': [
                "Software subscriptions for work are 100% deductible",
                "Track mileage to client sites - $0.655 per mile adds up!",
                "That new laptop? Fully deductible business equipment"
            ],
            'ecommerce': [
                "Advertising expenses are 100% deductible",
                "Shipping supplies and postage are business expenses",
                "Website hosting and domains are fully deductible"
            ],
            'coach': [
                "Client entertainment expenses are 100% deductible",
                "Professional certifications are tax-deductible",
                "Video equipment for sessions is deductible"
            ],
            'creator': [
                "Camera equipment can be deducted or depreciated",
                "Content creation tools and software are deductible",
                "Studio space rent is a business expense"
            ]
        }
        
        return tips_by_type.get(user_business_type, [
            "Track every business expense - they add up!",
            "Keep receipts for all deductible expenses",
            "Consult a tax professional for maximum savings"
        ])
    
    def estimate_annual_savings(self, monthly_expenses: float, 
                               business_type: str = 'general') -> Dict:
        """Estimate potential annual tax savings"""
        # Average deduction rates by business type
        deduction_rates = {
            'consultant': 0.65,  # High travel and client expenses
            'freelancer': 0.55,  # Software and equipment heavy
            'ecommerce': 0.70,   # High material and shipping costs
            'coach': 0.60,       # Mix of services and materials
            'creator': 0.65,     # Equipment and production costs
            'general': 0.50      # Conservative estimate
        }
        
        rate = deduction_rates.get(business_type, 0.50)
        annual_expenses = monthly_expenses * 12
        annual_deductions = annual_expenses * rate
        annual_tax_savings = annual_deductions * self.user_tax_rate
        
        return {
            'estimated_annual_expenses': annual_expenses,
            'estimated_annual_deductions': annual_deductions,
            'estimated_annual_tax_savings': annual_tax_savings,
            'monthly_tax_savings': annual_tax_savings / 12,
            'effective_discount': rate * self.user_tax_rate  # % saved on expenses
        }