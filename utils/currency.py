#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/currency.py
🎯 PURPOSE: Unified currency formatting and validation utilities
🔗 IMPORTS: typing, decimal
📤 EXPORTS: format_currency, validate_currency, CurrencyService
"""

from typing import Union, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
import re

class CurrencyService:
    """Unified currency formatting and validation service"""
    
    # Currency symbols mapping
    CURRENCY_SYMBOLS = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "CHF": "Fr.",
        "CNY": "¥",
        "INR": "₹",
        "MXN": "$",
        "BRL": "R$",
        "KRW": "₩",
        "SGD": "S$",
        "HKD": "HK$",
        "NZD": "NZ$"
    }
    
    # Currency formatting rules
    CURRENCY_RULES = {
        "USD": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "EUR": {"decimals": 2, "symbol_position": "before", "thousands_separator": ".", "decimal_separator": ","},
        "GBP": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "JPY": {"decimals": 0, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "CAD": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "AUD": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "CHF": {"decimals": 2, "symbol_position": "before", "thousands_separator": "'", "decimal_separator": "."},
        "CNY": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "INR": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "MXN": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "BRL": {"decimals": 2, "symbol_position": "before", "thousands_separator": ".", "decimal_separator": ","},
        "KRW": {"decimals": 0, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "SGD": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "HKD": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."},
        "NZD": {"decimals": 2, "symbol_position": "before", "thousands_separator": ",", "decimal_separator": "."}
    }
    
    @classmethod
    def format_currency(cls, amount_cents: int, currency: str = "USD", include_symbol: bool = True) -> str:
        """
        Format amount in cents to human-readable currency string
        
        Args:
            amount_cents: Amount in cents (e.g., 1550 for $15.50)
            currency: Currency code (default: USD)
            include_symbol: Whether to include currency symbol
        
        Returns:
            Formatted string (e.g., "$15.50" or "15.50")
        """
        if amount_cents is None:
            return "0"
        
        # Convert cents to decimal for precise arithmetic
        amount = Decimal(amount_cents) / Decimal(100)
        
        # Get currency rules
        rules = cls.CURRENCY_RULES.get(currency, cls.CURRENCY_RULES["USD"])
        symbol = cls.CURRENCY_SYMBOLS.get(currency, currency + " ")
        
        # Format the number
        if rules["decimals"] == 0:
            # No decimal places (like JPY, KRW)
            formatted_amount = f"{int(amount):,}"
        else:
            # With decimal places
            formatted_amount = f"{amount:.{rules['decimals']}f}"
            
            # Add thousands separators
            if rules["thousands_separator"]:
                parts = formatted_amount.split(".")
                parts[0] = f"{int(parts[0]):,}".replace(",", rules["thousands_separator"])
                formatted_amount = rules["decimal_separator"].join(parts)
        
        # Add symbol if requested
        if include_symbol:
            if rules["symbol_position"] == "before":
                return f"{symbol}{formatted_amount}"
            else:
                return f"{formatted_amount}{symbol}"
        else:
            return formatted_amount
    
    @classmethod
    def parse_currency(cls, amount_str: str, currency: str = "USD") -> int:
        """
        Parse currency string back to cents
        
        Args:
            amount_str: Currency string (e.g., "$15.50" or "15.50")
            currency: Currency code (default: USD)
        
        Returns:
            Amount in cents (e.g., 1550)
        """
        if not amount_str:
            return 0
        
        # Remove currency symbol and clean the string
        symbol = cls.CURRENCY_SYMBOLS.get(currency, "")
        cleaned = amount_str.replace(symbol, "").strip()
        
        # Remove thousands separators
        rules = cls.CURRENCY_RULES.get(currency, cls.CURRENCY_RULES["USD"])
        if rules["thousands_separator"]:
            cleaned = cleaned.replace(rules["thousands_separator"], "")
        
        # Convert decimal separator to standard
        if rules["decimal_separator"] != ".":
            cleaned = cleaned.replace(rules["decimal_separator"], ".")
        
        try:
            amount = Decimal(cleaned)
            return int(amount * 100)
        except (ValueError, TypeError):
            return 0
    
    @classmethod
    def validate_currency_code(cls, currency: str) -> bool:
        """
        Validate currency code format
        
        Args:
            currency: Currency code to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not currency or not isinstance(currency, str):
            return False
        
        # Check if it's a 3-letter uppercase code
        if not re.match(r'^[A-Z]{3}$', currency):
            return False
        
        return True
    
    @classmethod
    def get_supported_currencies(cls) -> Dict[str, str]:
        """
        Get list of supported currencies with their symbols
        
        Returns:
            Dictionary of currency codes to symbols
        """
        return cls.CURRENCY_SYMBOLS.copy()
    
    @classmethod
    def convert_currency(cls, amount_cents: int, from_currency: str, to_currency: str, 
                        exchange_rate: float) -> int:
        """
        Convert amount between currencies using exchange rate
        
        Args:
            amount_cents: Amount in cents in source currency
            from_currency: Source currency code
            to_currency: Target currency code
            exchange_rate: Exchange rate (target/source)
        
        Returns:
            Amount in cents in target currency
        """
        if not cls.validate_currency_code(from_currency) or not cls.validate_currency_code(to_currency):
            raise ValueError("Invalid currency code")
        
        if exchange_rate <= 0:
            raise ValueError("Exchange rate must be positive")
        
        # Convert to decimal for precise calculation
        amount = Decimal(amount_cents) / Decimal(100)
        converted = amount * Decimal(str(exchange_rate))
        
        # Round to 2 decimal places and convert back to cents
        return int(converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * 100)

# Convenience functions for backward compatibility
def format_currency(amount_cents: int, currency: str = "USD") -> str:
    """Format amount in cents to human-readable currency string"""
    return CurrencyService.format_currency(amount_cents, currency)

def parse_currency(amount_str: str, currency: str = "USD") -> int:
    """Parse currency string back to cents"""
    return CurrencyService.parse_currency(amount_str, currency)

def validate_currency_code(currency: str) -> bool:
    """Validate currency code format"""
    return CurrencyService.validate_currency_code(currency) 