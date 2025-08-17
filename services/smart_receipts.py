#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/smart_receipts.py
🎯 PURPOSE: AI-powered receipt processing for contractors
🔗 IMPORTS: OCR, AI analysis, expense categorization
📤 EXPORTS: Intelligent receipt parsing and insights
"""

import base64
import io
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import pytesseract
from dataclasses import dataclass
import json

from sqlalchemy.orm import Session
from models import Expense

@dataclass
class ReceiptData:
    """Structured receipt information"""
    vendor_name: str
    total_amount: float
    date: datetime
    items: List[Dict[str, Any]]
    category: str
    tax_deductible: bool
    confidence_score: float
    insights: List[str]
    warnings: List[str]

class SmartReceiptProcessor:
    """AI-powered receipt processing for construction expenses"""
    
    def __init__(self, user_id: int, db: Session):
        self.user_id = user_id
        self.db = db
        self.contractor_categories = {
            'materials': ['lumber', 'concrete', 'drywall', 'paint', 'nails', 'screws', 'pipe', 'wire'],
            'tools': ['drill', 'saw', 'hammer', 'level', 'measure', 'tool', 'equipment'],
            'vehicle': ['gas', 'fuel', 'diesel', 'oil', 'tire', 'maintenance'],
            'safety': ['helmet', 'gloves', 'boots', 'harness', 'vest', 'goggles'],
            'office': ['paper', 'ink', 'computer', 'software', 'phone'],
            'subcontractor': ['labor', 'service', 'installation', 'repair']
        }
        
    async def process_receipt(self, image_data: str) -> ReceiptData:
        """Process receipt image and extract structured data"""
        
        # Extract text from image
        text = await self._extract_text(image_data)
        
        # Parse receipt data
        receipt_data = self._parse_receipt_text(text)
        
        # Enhance with AI insights
        receipt_data = self._add_intelligence(receipt_data)
        
        # Check for tax optimization
        receipt_data = self._analyze_tax_implications(receipt_data)
        
        # Detect anomalies or savings opportunities
        receipt_data = self._detect_opportunities(receipt_data)
        
        return receipt_data
    
    async def _extract_text(self, image_data: str) -> str:
        """Extract text from receipt image using OCR"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def _preprocess_image(self, image: Image) -> Image:
        """Enhance image for better OCR accuracy"""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        # Would implement contrast enhancement here
        
        return image
    
    def _parse_receipt_text(self, text: str) -> ReceiptData:
        """Parse receipt text into structured data"""
        lines = text.strip().split('\n')
        
        # Extract vendor name (usually at top)
        vendor_name = self._extract_vendor(lines)
        
        # Extract date
        date = self._extract_date(text)
        
        # Extract total amount
        total_amount = self._extract_total(text)
        
        # Extract line items
        items = self._extract_items(lines)
        
        # Auto-categorize based on items
        category = self._categorize_receipt(vendor_name, items)
        
        return ReceiptData(
            vendor_name=vendor_name,
            total_amount=total_amount,
            date=date,
            items=items,
            category=category,
            tax_deductible=True,  # Most contractor expenses are
            confidence_score=0.85,
            insights=[],
            warnings=[]
        )
    
    def _extract_vendor(self, lines: List[str]) -> str:
        """Extract vendor name from receipt"""
        # Common vendor patterns for contractors
        vendor_patterns = [
            r'home\s*depot',
            r'lowe\'?s',
            r'menards',
            r'ace\s*hardware',
            r'harbor\s*freight',
            r'grainger',
            r'fastenal'
        ]
        
        for line in lines[:5]:  # Check first 5 lines
            line_lower = line.lower()
            for pattern in vendor_patterns:
                if re.search(pattern, line_lower):
                    return line.strip()
        
        # Return first non-empty line as vendor
        for line in lines:
            if line.strip() and len(line.strip()) > 3:
                return line.strip()
        
        return "Unknown Vendor"
    
    def _extract_date(self, text: str) -> datetime:
        """Extract date from receipt text"""
        # Common date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+\w+\s+\d{4})',
            r'(\w+\s+\d{1,2},?\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    # Try various date formats
                    date_str = match.group(1)
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
                except:
                    pass
        
        # Default to today if can't parse
        return datetime.now()
    
    def _extract_total(self, text: str) -> float:
        """Extract total amount from receipt"""
        # Look for total patterns
        total_patterns = [
            r'total[:\s]+\$?([\d,]+\.?\d*)',
            r'amount[:\s]+\$?([\d,]+\.?\d*)',
            r'balance[:\s]+\$?([\d,]+\.?\d*)',
            r'\$?([\d,]+\.?\d*)\s*(?:total|ttl)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    return float(amount_str)
                except:
                    pass
        
        # Find largest dollar amount as fallback
        amounts = re.findall(r'\$?([\d,]+\.?\d{2})', text)
        if amounts:
            amounts_float = [float(a.replace(',', '')) for a in amounts]
            return max(amounts_float)
        
        return 0.0
    
    def _extract_items(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract line items from receipt"""
        items = []
        
        # Pattern for items with prices
        item_pattern = r'^(.+?)\s+\$?([\d,]+\.?\d{2})$'
        
        for line in lines:
            match = re.match(item_pattern, line.strip())
            if match:
                item_name = match.group(1).strip()
                price = float(match.group(2).replace(',', ''))
                
                # Skip if it looks like a total
                if not any(word in item_name.lower() for word in ['total', 'subtotal', 'tax', 'balance']):
                    items.append({
                        'name': item_name,
                        'price': price,
                        'category': self._categorize_item(item_name)
                    })
        
        return items
    
    def _categorize_item(self, item_name: str) -> str:
        """Categorize individual item"""
        item_lower = item_name.lower()
        
        for category, keywords in self.contractor_categories.items():
            for keyword in keywords:
                if keyword in item_lower:
                    return category
        
        return 'materials'  # Default for contractors
    
    def _categorize_receipt(self, vendor: str, items: List[Dict]) -> str:
        """Categorize entire receipt based on vendor and items"""
        vendor_lower = vendor.lower()
        
        # Vendor-based categorization
        if any(v in vendor_lower for v in ['home depot', 'lowes', 'menards']):
            return 'materials'
        elif any(v in vendor_lower for v in ['shell', 'exxon', 'chevron', 'gas']):
            return 'vehicle'
        elif any(v in vendor_lower for v in ['harbor freight', 'grainger']):
            return 'tools'
        
        # Item-based categorization
        if items:
            categories = [item.get('category', 'materials') for item in items]
            # Return most common category
            return max(set(categories), key=categories.count)
        
        return 'materials'
    
    def _add_intelligence(self, receipt_data: ReceiptData) -> ReceiptData:
        """Add AI-powered insights to receipt data"""
        insights = []
        
        # Price comparison insight
        if receipt_data.vendor_name and receipt_data.total_amount > 100:
            avg_price = self._get_vendor_average(receipt_data.vendor_name)
            if avg_price and receipt_data.total_amount > avg_price * 1.15:
                insights.append(
                    f"This purchase is {((receipt_data.total_amount/avg_price - 1) * 100):.0f}% "
                    f"higher than your average at {receipt_data.vendor_name}"
                )
        
        # Category spending insight
        category_total = self._get_month_category_total(receipt_data.category)
        if category_total > 1000:
            insights.append(
                f"You've spent ${category_total:,.0f} on {receipt_data.category} this month"
            )
        
        # Tax season reminder
        if receipt_data.date.month in [3, 4]:
            insights.append(
                "Tax season reminder: This expense is likely deductible as a business expense"
            )
        
        receipt_data.insights = insights
        return receipt_data
    
    def _analyze_tax_implications(self, receipt_data: ReceiptData) -> ReceiptData:
        """Analyze tax deductibility and optimization"""
        
        # All contractor categories are generally deductible
        deductible_categories = ['materials', 'tools', 'vehicle', 'safety', 'office', 'subcontractor']
        receipt_data.tax_deductible = receipt_data.category in deductible_categories
        
        # Add tax insights
        if receipt_data.tax_deductible:
            if receipt_data.category == 'vehicle':
                receipt_data.insights.append(
                    "Vehicle expense: Remember to track mileage for maximum deduction"
                )
            elif receipt_data.category == 'tools' and receipt_data.total_amount > 2500:
                receipt_data.insights.append(
                    "Large tool purchase: May qualify for Section 179 deduction"
                )
        
        return receipt_data
    
    def _detect_opportunities(self, receipt_data: ReceiptData) -> ReceiptData:
        """Detect savings opportunities and anomalies"""
        warnings = []
        
        # Duplicate purchase warning
        recent_similar = self._check_duplicate_purchase(
            receipt_data.vendor_name, 
            receipt_data.total_amount,
            receipt_data.date
        )
        if recent_similar:
            warnings.append(
                f"Similar purchase detected {recent_similar['days_ago']} days ago for "
                f"${recent_similar['amount']:.2f}"
            )
        
        # Price spike detection
        if receipt_data.items:
            for item in receipt_data.items:
                if self._is_price_spike(item['name'], item['price']):
                    warnings.append(
                        f"{item['name']} price seems high - consider checking alternatives"
                    )
        
        # Bulk purchase opportunity
        if receipt_data.category == 'materials' and receipt_data.total_amount < 500:
            receipt_data.insights.append(
                "Tip: Bulk purchases over $500 often get contractor discounts"
            )
        
        receipt_data.warnings = warnings
        return receipt_data
    
    def _get_vendor_average(self, vendor_name: str) -> Optional[float]:
        """Get user's average spending at vendor"""
        # Would query actual expense history
        # Simulated for now
        vendor_averages = {
            'home depot': 156.42,
            'lowes': 189.30,
            'harbor freight': 89.95
        }
        return vendor_averages.get(vendor_name.lower(), None)
    
    def _get_month_category_total(self, category: str) -> float:
        """Get total spending in category for current month"""
        # Would query actual expenses
        # Simulated for now
        return 1250.00 if category == 'materials' else 450.00
    
    def _check_duplicate_purchase(self, vendor: str, amount: float, date: datetime) -> Optional[Dict]:
        """Check for similar recent purchases"""
        # Would query expense history for duplicates
        # Simulated for now
        if vendor.lower() == 'home depot' and abs(amount - 156.42) < 20:
            return {'days_ago': 3, 'amount': 156.42}
        return None
    
    def _is_price_spike(self, item_name: str, price: float) -> bool:
        """Detect if item price is unusually high"""
        # Would compare against historical prices
        # Simple heuristic for now
        common_items = {
            '2x4': 8.50,
            'plywood': 45.00,
            'paint': 35.00
        }
        
        for item, typical_price in common_items.items():
            if item in item_name.lower():
                return price > typical_price * 1.5
        
        return False
    
    async def create_expense_from_receipt(self, receipt_data: ReceiptData) -> Expense:
        """Create expense record from receipt data"""
        expense = Expense(
            user_id=self.user_id,
            amount=receipt_data.total_amount,
            description=f"{receipt_data.vendor_name} - {receipt_data.category}",
            category=receipt_data.category,
            vendor_name=receipt_data.vendor_name,
            expense_date=receipt_data.date,
            is_tax_deductible=receipt_data.tax_deductible,
            receipt_data=json.dumps({
                'items': receipt_data.items,
                'insights': receipt_data.insights,
                'warnings': receipt_data.warnings,
                'confidence': receipt_data.confidence_score
            }),
            created_at=datetime.now()
        )
        
        self.db.add(expense)
        self.db.commit()
        
        return expense