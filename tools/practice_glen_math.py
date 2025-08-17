#!/usr/bin/env python3
"""
PRACTICE THE ACTUAL MATH YOU'LL DO AT GLEN'S TABLE
"""

print("PRACTICE RUN - What happens at Glen's kitchen table")
print("="*60)

# Glen shows you a crumpled quote
print("\nGlen pulls out folder: 'Smith Bathroom'")
print("Shows you his quote: $12,000")

# You ask about costs
print("\nYou: 'What did you spend on this job?'")
print("Glen starts pulling out receipts...\n")

# Add them up AS GLEN SHOWS YOU
costs = []

print("Home Depot receipt: $3,487.53")
costs.append(3487.53)

print("Lowes receipt: $412.18") 
costs.append(412.18)

print("ABC Plumbing invoice: $4,000")
costs.append(4000)

print("City permit: $450")
costs.append(450)

print("Rented tile saw: $300")
costs.append(300)

print("\nYou: 'How many hours did you work?'")
print("Glen: 'Uh... probably 50-60 hours'")
print("You: 'Let's say 55. What do you charge per hour?'")
print("Glen: 'I figure I make about $40 an hour'")
labor = 55 * 40
costs.append(labor)
print(f"Labor: 55 × $40 = ${labor}")

# THE ACTUAL MATH
total = sum(costs)
profit = 12000 - total
margin = (profit / 12000) * 100

print("\n" + "-"*40)
print(f"TOTAL COSTS: ${total:,.2f}")
print(f"PROFIT: ${profit:,.2f}")
print(f"MARGIN: {margin:.1f}%")
print("-"*40)

print("\nYou: 'Glen, you only made 13% on this job'")
print("Glen: 'That can't be right...'")
print("You: 'Let's check - did Mrs. Smith ask for anything extra?'")
print("Glen: 'Well, she wanted a different tile layout...'")
print("You: 'How many extra hours?'")
print("Glen: 'Maybe 6-7 hours'")
print("You: 'Did you bill for that?'")
print("Glen: 'No, I just did it'")

print("\n" + "="*60)
print("FINDING THE MONEY")
print("="*60)

# Material markup
material_costs = 3487.53 + 412.18  # Home Depot + Lowes
markup_missing = material_costs * 0.25
print(f"\n1. No markup on ${material_costs:.2f} of materials")
print(f"   Should add 25% = ${markup_missing:.2f}")

# Unbilled hours
unbilled_hours = 6
unbilled_value = unbilled_hours * 65  # What he SHOULD charge
print(f"\n2. Unbilled change order: {unbilled_hours} hours")
print(f"   Should charge $65/hr = ${unbilled_value}")

# Underpriced labor  
labor_gap = 55 * (65 - 40)
print(f"\n3. Charging $40/hr but should be $65/hr")
print(f"   55 hours × $25 gap = ${labor_gap}")

total_found = markup_missing + unbilled_value + labor_gap
new_profit = profit + total_found
new_margin = (new_profit / 12000) * 100

print("\n" + "="*60)
print(f"MONEY LEFT ON TABLE: ${total_found:,.2f}")
print(f"SHOULD HAVE MADE: ${new_profit:,.2f} ({new_margin:.1f}% margin)")
print("="*60)

print("\nGlen: 'Holy shit...'")
print("You: 'And this is just ONE job. Multiply by 10 jobs a year...'")
print(f"Glen: 'That's ${total_found * 10:,.2f} I'm losing every year!'")
print("You: 'Exactly. Want me to show you how to fix it?'")

print("\n" + "-"*60)
print("THE FIX (Write this on paper for Glen):")
print("-"*60)
print("1. TOMORROW: Add 25% to all material costs")
print("2. TOMORROW: Create simple change order form") 
print("3. NEXT QUOTE: Use $65/hour for labor")
print("4. NEXT QUOTE: Bathrooms start at $15,000")

print("\n" + "-"*60)
print("You: 'For $500, I'll analyze all your recent jobs and")
print("     create a simple system to track this going forward'")
print("Glen: *writes check*")
print("-"*60)