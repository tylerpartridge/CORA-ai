#!/usr/bin/env python3
"""
Manual Profit Analysis Tool for CORA Consulting
Use this to analyze contractor data before CORA is fully automated
"""

def analyze_job_profitability():
    """Interactive job profit analyzer"""
    print("CONTRACTOR PROFIT ANALYSIS TOOL")
    print("="*40)
    
    jobs = []
    
    while True:
        print("\nEnter job details (or 'done' to finish):")
        job_name = input("Job name: ")
        if job_name.lower() == 'done':
            break
            
        quoted = float(input("Quoted amount: $"))
        
        print("\nEnter expenses (enter 0 to finish):")
        expenses = []
        total_expenses = 0
        
        while True:
            amount = float(input("  Expense amount (0 to finish): $"))
            if amount == 0:
                break
            category = input("  Category (Materials/Labor/Permits/Equipment): ")
            expenses.append({"amount": amount, "category": category})
            total_expenses += amount
        
        profit = quoted - total_expenses
        margin = (profit / quoted * 100) if quoted > 0 else 0
        
        jobs.append({
            "name": job_name,
            "quoted": quoted,
            "expenses": total_expenses,
            "profit": profit,
            "margin": margin
        })
        
        print(f"\nJob Summary:")
        print(f"  Revenue: ${quoted:,.2f}")
        print(f"  Expenses: ${total_expenses:,.2f}")
        print(f"  Profit: ${profit:,.2f} ({margin:.1f}%)")
        
        if margin < 20:
            print("  WARNING: Low profit margin!")
    
    # Final report
    if jobs:
        print("\n" + "="*50)
        print("PROFIT ANALYSIS REPORT")
        print("="*50)
        
        total_revenue = sum(j["quoted"] for j in jobs)
        total_expenses = sum(j["expenses"] for j in jobs)
        total_profit = total_revenue - total_expenses
        avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        print(f"\nTotal Jobs Analyzed: {len(jobs)}")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Total Expenses: ${total_expenses:,.2f}")
        print(f"Total Profit: ${total_profit:,.2f}")
        print(f"Average Margin: {avg_margin:.1f}%")
        
        print("\nJob-by-Job Summary:")
        for job in sorted(jobs, key=lambda x: x["margin"]):
            status = "LOSS" if job["margin"] < 0 else "LOW" if job["margin"] < 20 else "GOOD"
            print(f"  {job['name']}: {job['margin']:.1f}% ({status})")
        
        print("\nRECOMMENDATIONS:")
        low_margin_jobs = [j for j in jobs if j["margin"] < 20]
        if low_margin_jobs:
            print(f"- {len(low_margin_jobs)} jobs below 20% margin - review pricing")
        print("- Track all change orders and bill them")
        print("- Consider 20-30% markup on materials")
        print("- Focus on job types with highest margins")

if __name__ == "__main__":
    analyze_job_profitability()