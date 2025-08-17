#!/usr/bin/env python3
"""
Simple profit analysis for Glen - no dependencies needed
"""

def analyze_glen_jobs():
    """Interactive job analysis"""
    print("GLEN DAY CONSTRUCTION - PROFIT ANALYSIS")
    print("="*50)
    
    jobs = []
    
    # Example data (what Glen might give you)
    print("\nExample: Analyzing Glen's recent jobs...")
    print("\nJob 1: Smith Bathroom Remodel")
    print("Quote: $12,000")
    print("Receipts Glen shows you:")
    print("- Home Depot receipt: $3,500 (tiles, fixtures)")
    print("- Paid ABC Plumbing: $4,000 (check #1234)")  
    print("- City permit: $450")
    print("- Rented tile saw: $300")
    print("- Glen's hours: 55 hrs (doesn't track rate)")
    
    # Calculate
    glen_hourly = 40  # What he thinks he makes
    labor_cost = 55 * glen_hourly
    total_costs = 3500 + 4000 + 450 + 300 + labor_cost
    profit = 12000 - total_costs
    margin = (profit / 12000) * 100
    
    print(f"\nCalculation:")
    print(f"Total Costs: ${total_costs:,.2f}")
    print(f"Profit: ${profit:,.2f}")
    print(f"Margin: {margin:.1f}%")
    print("STATUS: ⚠️  LOW MARGIN!")
    
    # Find the money
    print("\nFINDING THE MONEY:")
    print("1. No markup on materials")
    print("   - Paid $3,500, charged $3,500")
    print("   - Should charge $4,375 (25% markup)")
    print("   - FOUND: $875")
    
    print("\n2. Unbilled extras")
    print('   Glen: "Oh yeah, she wanted a different tile pattern"')
    print('   You: "Did you bill for the 6 extra hours?"')
    print('   Glen: "No, I just did it"')
    print("   - 6 hours × $65/hr = $390")
    print("   - FOUND: $390")
    
    print("\n3. True hourly rate")
    print("   - Glen thinks: $40/hour")
    print("   - Should be: $65/hour (industry standard)")
    print("   - 55 hours × $25 difference = $1,375")
    print("   - FOUND: $1,375")
    
    total_found = 875 + 390 + 1375
    new_profit = profit + total_found
    new_margin = (new_profit / 12000) * 100
    
    print(f"\nTOTAL MONEY FOUND: ${total_found:,.2f}")
    print(f"New Profit Would Be: ${new_profit:,.2f} ({new_margin:.1f}% margin)")
    
    # Recommendations
    print("\n" + "="*50)
    print("RECOMMENDATIONS FOR GLEN")
    print("="*50)
    print("IMMEDIATE ACTIONS:")
    print("1. Add 25% markup to ALL materials starting tomorrow")
    print("2. Create simple change order form")  
    print("3. Raise hourly rate to $65")
    print("4. Quote bathrooms at $15,000 minimum")
    
    print("\nEXPECTED RESULTS:")
    print(f"- Per bathroom: ${total_found:,.2f} more profit")
    print(f"- Per year (10 bathrooms): ${total_found * 10:,.2f}")
    print("- No extra work required!")
    
    print("\n" + "="*50)
    print("GLEN'S REACTION")
    print("="*50)
    print('Glen: "Holy crap, I\'m leaving that much on the table?"')
    print('You: "Yes, and this is just from one job. Want to see the others?"')
    print('Glen: "Absolutely. What do I owe you?"')
    print('You: "$500 for this analysis, and I can help you track this monthly"')

def create_simple_tracking_sheet():
    """Create a simple CSV Glen can use"""
    csv_content = """Job Name,Customer,Quote,Materials,Labor Sub,Labor Own,Permits,Equipment,Other,Total Costs,Profit,Margin %,Notes
Smith Bathroom,John Smith,12000,3500,4000,2200,450,300,0,=SUM(D2:I2),=B2-J2,=K2/B2*100,Low margin - no markup
Wilson Kitchen,Sarah Wilson,8500,4000,800,1600,0,0,0,=SUM(D3:I3),=B3-J3,=K3/B3*100,Good margin
Johnson Addition,Bob Johnson,45000,18000,12000,8000,1200,800,0,=SUM(D4:I4),=B4-J4,=K4/B4*100,Check unbilled extras
"""
    
    with open('glen_tracking_sheet.csv', 'w') as f:
        f.write(csv_content)
    
    print("\nCreated: glen_tracking_sheet.csv")
    print("Glen can open this in Excel and start tracking immediately")

if __name__ == "__main__":
    analyze_glen_jobs()
    print("\n")
    create_simple_tracking_sheet()
    
    print("\n" + "="*50)
    print("WHAT HAPPENS AT GLEN'S PLACE")
    print("="*50)
    print("1. Glen shows you his job folders/receipts")
    print("2. You fill out the data collection form together")
    print("3. You enter it into Excel/calculator")
    print("4. You show him the profit leaks")
    print("5. You give him specific actions")
    print("6. He pays you $500")
    print("7. You set up monthly check-in")
    
    print("\nYOUR TOOLS:")
    print("- Printed data collection form")
    print("- Laptop with Excel or calculator")
    print("- This analysis script")
    print("- Invoice for $500")