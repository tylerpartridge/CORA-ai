#!/usr/bin/env python3
"""
Create Excel template for Glen's job analysis
"""

import pandas as pd
from datetime import datetime

def create_job_analysis_template():
    """Create Excel template for contractor job analysis"""
    
    # Create sample data structure
    jobs_data = {
        'Job Name': ['Smith Bathroom', 'Wilson Kitchen', 'Johnson Addition', '', '', '', '', '', '', ''],
        'Customer': ['John Smith', 'Sarah Wilson', 'Bob Johnson', '', '', '', '', '', '', ''],
        'Job Type': ['Bathroom', 'Kitchen', 'Addition', '', '', '', '', '', '', ''],
        'Quote Amount': [12000, 8500, 45000, 0, 0, 0, 0, 0, 0, 0],
        'Materials': [3500, 4000, 18000, 0, 0, 0, 0, 0, 0, 0],
        'Labor (Subs)': [4000, 800, 12000, 0, 0, 0, 0, 0, 0, 0],
        'Labor (Own)': [2200, 1600, 8000, 0, 0, 0, 0, 0, 0, 0],
        'Permits/Fees': [450, 0, 1200, 0, 0, 0, 0, 0, 0, 0],
        'Equipment': [300, 0, 800, 0, 0, 0, 0, 0, 0, 0],
        'Other Costs': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Total Costs': ['=SUM(E2:J2)', '=SUM(E3:J3)', '=SUM(E4:J4)', '=SUM(E5:J5)', '=SUM(E6:J6)', 
                       '=SUM(E7:J7)', '=SUM(E8:J8)', '=SUM(E9:J9)', '=SUM(E10:J10)', '=SUM(E11:J11)'],
        'Profit': ['=D2-K2', '=D3-K3', '=D4-K4', '=D5-K5', '=D6-K6', 
                  '=D7-K7', '=D8-K8', '=D9-K9', '=D10-K10', '=D11-K11'],
        'Margin %': ['=IF(D2>0,L2/D2*100,0)', '=IF(D3>0,L3/D3*100,0)', '=IF(D4>0,L4/D4*100,0)', 
                    '=IF(D5>0,L5/D5*100,0)', '=IF(D6>0,L6/D6*100,0)', '=IF(D7>0,L7/D7*100,0)', 
                    '=IF(D8>0,L8/D8*100,0)', '=IF(D9>0,L9/D9*100,0)', '=IF(D10>0,L10/D10*100,0)', 
                    '=IF(D11>0,L11/D11*100,0)'],
        'Days to Complete': [14, 7, 45, 0, 0, 0, 0, 0, 0, 0],
        'Change Orders': [0, 0, 2500, 0, 0, 0, 0, 0, 0, 0],
        'Unbilled Extras': [500, 0, 1000, 0, 0, 0, 0, 0, 0, 0]
    }
    
    # Create DataFrame
    df = pd.DataFrame(jobs_data)
    
    # Create summary data
    summary_data = {
        'Metric': [
            'Total Jobs Analyzed',
            'Total Revenue', 
            'Total Costs',
            'Total Profit',
            'Average Margin %',
            'Best Margin Job',
            'Worst Margin Job',
            'Total Unbilled Extras',
            'Potential with 25% Material Markup',
            'Annual Impact (10 jobs/year)'
        ],
        'Value': [
            '=COUNTA(A2:A11)',
            '=SUM(D2:D11)',
            '=SUM(K2:K11)',
            '=SUM(L2:L11)',
            '=AVERAGE(M2:M11)',
            '=MAX(M2:M11)',
            '=MIN(M2:M11)',
            '=SUM(P2:P11)',
            '=SUM(E2:E11)*0.25',
            '=I9*10'
        ],
        'Notes': [
            'Number of jobs in analysis',
            'Sum of all quotes',
            'Sum of all expenses',
            'Revenue minus costs',
            'Average profit margin',
            'Best performing job type',
            'Needs immediate attention',
            'Money left on table',
            'Additional profit from markup',
            'Projected annual improvement'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    
    # Create recommendations
    recommendations = {
        'Priority': [1, 2, 3, 4, 5],
        'Action': [
            'Add 25% markup to all materials',
            'Track and bill ALL change orders',
            'Raise bathroom remodel quotes by 20%',
            'Focus marketing on kitchen updates',
            'Implement job tracking system'
        ],
        'Impact': [
            '$2,000+ per job',
            '$500-1,500 per job',
            '$2,400 per bathroom',
            'Higher margin work',
            'Prevent profit leaks'
        ],
        'When': [
            'Immediately',
            'Next job',
            'Next quote',
            'This month',
            'This week'
        ]
    }
    
    recommendations_df = pd.DataFrame(recommendations)
    
    # Save to Excel with multiple sheets
    with pd.ExcelWriter('Glen_Day_Profit_Analysis.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Job Analysis', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        # Get the workbook and worksheets
        workbook = writer.book
        job_sheet = writer.sheets['Job Analysis']
        summary_sheet = writer.sheets['Summary']
        rec_sheet = writer.sheets['Recommendations']
        
        # Format currency columns
        from openpyxl.styles import numbers
        currency_format = '"$"#,##0.00'
        percent_format = '0.0"%"'
        
        # Format Job Analysis sheet
        for row in range(2, 12):
            for col in 'DEFGHIJKL':
                job_sheet[f'{col}{row}'].number_format = currency_format
            job_sheet[f'M{row}'].number_format = percent_format
            job_sheet[f'O{row}'].number_format = currency_format
            job_sheet[f'P{row}'].number_format = currency_format
        
        # Auto-fit columns
        for column in job_sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            job_sheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Created: Glen_Day_Profit_Analysis.xlsx")
    print("\nHow to use:")
    print("1. Open the Excel file")
    print("2. Enter Glen's job data in the Job Analysis tab")
    print("3. Formulas will auto-calculate profits and margins")
    print("4. Review Summary tab for key insights")
    print("5. Show Recommendations tab for action plan")

if __name__ == "__main__":
    create_job_analysis_template()
    
    print("\n" + "="*50)
    print("CONSULTING CHECKLIST")
    print("="*50)
    print("[ ] Print data collection form")
    print("[ ] Bring this Excel template on laptop")
    print("[ ] Have calculator ready")
    print("[ ] Bring NDA (if needed)")
    print("[ ] Charge laptop")
    print("[ ] Prepare for common objections")
    print("\nREMEMBER: You're finding money he's already losing!")