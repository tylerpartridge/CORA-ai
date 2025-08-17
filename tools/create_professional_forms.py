#!/usr/bin/env python3
"""
Create professional data collection forms for remote consulting
"""

def create_excel_data_collection_form():
    """Create a professional Excel form Glen can fill out"""
    
    # Create HTML that looks like Excel and can be saved as .xlsx
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Contractor Profit Analysis - Data Collection Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: white;
        }
        .header {
            background: #1f4788;
            color: white;
            padding: 20px;
            margin: -20px -20px 20px -20px;
        }
        .instructions {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th {
            background: #4472c4;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: normal;
        }
        td {
            border: 1px solid #d0d0d0;
            padding: 8px;
        }
        input[type="text"], input[type="number"], input[type="date"] {
            width: 100%;
            border: none;
            padding: 5px;
            font-size: 14px;
        }
        input[type="number"] {
            text-align: right;
        }
        .save-button {
            background: #70ad47;
            color: white;
            padding: 10px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .section-header {
            background: #e7e6e6;
            padding: 8px;
            font-weight: bold;
            margin-top: 20px;
        }
        @media print {
            .save-button { display: none; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Contractor Profit Analysis</h1>
        <p>Job Cost Data Collection Form</p>
    </div>

    <div class="instructions">
        <h3>Instructions:</h3>
        <ol>
            <li>Fill out one row for each completed job (last 5-10 jobs)</li>
            <li>Enter all amounts in dollars (no $ symbol needed)</li>
            <li>If you don't have exact numbers, your best estimate is fine</li>
            <li>Save this form and email back when complete</li>
        </ol>
    </div>

    <form id="jobDataForm">
        <div class="section-header">JOB INFORMATION</div>
        <table>
            <thead>
                <tr>
                    <th style="width:20%">Job Name/Address</th>
                    <th style="width:15%">Customer Name</th>
                    <th style="width:10%">Job Type</th>
                    <th style="width:10%">Start Date</th>
                    <th style="width:10%">End Date</th>
                    <th style="width:12%">Original Quote ($)</th>
                    <th style="width:12%">Final Invoice ($)</th>
                    <th style="width:11%">Change Orders ($)</th>
                </tr>
            </thead>
            <tbody id="jobRows">
                <!-- 10 rows for jobs -->
            </tbody>
        </table>

        <div class="section-header">COST BREAKDOWN (per job - use same order as above)</div>
        <table>
            <thead>
                <tr>
                    <th style="width:20%">Job Name (match above)</th>
                    <th style="width:11%">Materials ($)</th>
                    <th style="width:11%">Your Labor ($)</th>
                    <th style="width:11%">Your Hours</th>
                    <th style="width:11%">Subcontractors ($)</th>
                    <th style="width:11%">Permits/Fees ($)</th>
                    <th style="width:11%">Equipment ($)</th>
                    <th style="width:14%">Other/Misc ($)</th>
                </tr>
            </thead>
            <tbody id="costRows">
                <!-- 10 rows for costs -->
            </tbody>
        </table>

        <div class="section-header">ADDITIONAL INFORMATION</div>
        <table>
            <tr>
                <td style="width:40%">What types of jobs are most profitable for you?</td>
                <td><input type="text" name="profitable_jobs" /></td>
            </tr>
            <tr>
                <td>What types of jobs give you the most problems?</td>
                <td><input type="text" name="problem_jobs" /></td>
            </tr>
            <tr>
                <td>Do you typically add markup to materials? If yes, how much?</td>
                <td><input type="text" name="markup_practice" /></td>
            </tr>
            <tr>
                <td>What's your target profit margin per job?</td>
                <td><input type="text" name="target_margin" /></td>
            </tr>
            <tr>
                <td>How often do you have unbilled change orders?</td>
                <td><input type="text" name="unbilled_frequency" /></td>
            </tr>
            <tr>
                <td>What's your hourly rate for labor?</td>
                <td><input type="text" name="hourly_rate" /></td>
            </tr>
        </table>

        <div style="text-align: center; margin-top: 30px;">
            <button type="button" class="save-button" onclick="saveData()">Save Form Data</button>
            <p style="margin-top: 10px; color: #666;">After saving, email this file back to continue with analysis</p>
        </div>
    </form>

    <script>
        // Create empty rows
        function createRows() {
            const jobRows = document.getElementById('jobRows');
            const costRows = document.getElementById('costRows');
            
            for (let i = 1; i <= 10; i++) {
                // Job info row
                const jobRow = document.createElement('tr');
                jobRow.innerHTML = `
                    <td><input type="text" name="job_name_${i}" /></td>
                    <td><input type="text" name="customer_${i}" /></td>
                    <td><input type="text" name="job_type_${i}" /></td>
                    <td><input type="date" name="start_date_${i}" /></td>
                    <td><input type="date" name="end_date_${i}" /></td>
                    <td><input type="number" name="quote_${i}" step="0.01" /></td>
                    <td><input type="number" name="invoice_${i}" step="0.01" /></td>
                    <td><input type="number" name="changes_${i}" step="0.01" /></td>
                `;
                jobRows.appendChild(jobRow);
                
                // Cost row
                const costRow = document.createElement('tr');
                costRow.innerHTML = `
                    <td><input type="text" name="cost_job_name_${i}" /></td>
                    <td><input type="number" name="materials_${i}" step="0.01" /></td>
                    <td><input type="number" name="labor_own_${i}" step="0.01" /></td>
                    <td><input type="number" name="hours_${i}" step="0.01" /></td>
                    <td><input type="number" name="subs_${i}" step="0.01" /></td>
                    <td><input type="number" name="permits_${i}" step="0.01" /></td>
                    <td><input type="number" name="equipment_${i}" step="0.01" /></td>
                    <td><input type="number" name="other_${i}" step="0.01" /></td>
                `;
                costRows.appendChild(costRow);
            }
        }
        
        function saveData() {
            const formData = new FormData(document.getElementById('jobDataForm'));
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            // Create CSV content
            let csv = 'Job Profit Analysis Data\\n';
            csv += 'Field,Value\\n';
            
            for (let [key, value] of Object.entries(data)) {
                if (value) {
                    csv += `"${key}","${value}"\\n`;
                }
            }
            
            // Download as CSV
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'contractor_job_data.csv';
            a.click();
            
            alert('Data saved! Please email the downloaded file back for analysis.');
        }
        
        // Initialize
        createRows();
    </script>
</body>
</html>"""

    # Save as HTML that can be opened in Excel
    with open('Glen_Day_Data_Collection_Form.html', 'w') as f:
        f.write(html_content)
    
    print("Created: Glen_Day_Data_Collection_Form.html")
    print("This opens in any browser and can be saved/emailed back")

def create_google_form_script():
    """Create instructions for Google Forms version"""
    
    instructions = """
# Professional Data Collection Options

## Option 1: Google Forms (Recommended for Remote)
1. Create Google Form with these fields:
   - Job Name/Address (Short answer)
   - Customer Name (Short answer)
   - Job Type (Dropdown: Bathroom, Kitchen, Addition, Other)
   - Original Quote (Number)
   - Material Costs (Number)
   - Labor Costs (Number)
   - Subcontractor Costs (Number)
   - Other Costs (Number)
   - Unbilled Extras (Number)
   - Comments (Paragraph)

2. Share link with Glen
3. Responses automatically go to Google Sheets
4. You analyze in Sheets and create report

## Option 2: Professional PDF Form
Use Adobe Acrobat or similar to create fillable PDF

## Option 3: Simple Excel Template
Create basic Excel with formulas that Glen fills out

The key is making it EASY for Glen to provide data remotely.
"""
    
    with open('remote_data_collection_options.txt', 'w') as f:
        f.write(instructions)

if __name__ == "__main__":
    create_excel_data_collection_form()
    create_google_form_script()
    
    print("\nPROFESSIONAL REMOTE WORKFLOW:")
    print("1. Email Glen the HTML form (works in any browser)")
    print("2. He fills it out and saves/emails back")
    print("3. You import into Excel/Google Sheets")
    print("4. Run analysis and create professional PDF report")
    print("5. Video call to review findings")
    print("6. Email invoice for $500")