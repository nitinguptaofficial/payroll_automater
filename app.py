from flask import Flask, render_template, request, jsonify, Response, send_file
import pandas as pd
import os
from datetime import datetime
import calendar
from io import BytesIO, StringIO

app = Flask(__name__)

DATA_FILE = 'employee_data.xlsx'

# Working days per month in 2025 (excluding weekends)
WORKING_DAYS_2025 = {
    'January': 23, 'February': 22, 'March': 23, 'April': 22,
    'May': 23, 'June': 22, 'July': 23, 'August': 23,
    'September': 22, 'October': 23, 'November': 22, 'December': 23
}

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

def get_empty_dataframe():
    """Create an empty DataFrame with the required structure."""
    columns = ['Name', 'Annual_Package'] + [f'{m}_Absent' for m in MONTHS] + ['Remarks']
    return pd.DataFrame(columns=columns)

def load_data():
    """Load employee data from Excel file."""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return get_empty_dataframe()
    return get_empty_dataframe()

def save_data(df):
    """Save employee data to Excel file."""
    df.to_excel(DATA_FILE, index=False)

def calculate_salary(annual_package, absent_days, working_days):
    """Calculate monthly salary using the formula: (package/271) * (working_days - absent_days)"""
    if pd.isna(absent_days):
        absent_days = 0
    daily_rate = annual_package / 271
    effective_days = max(0, working_days - absent_days)
    return round(daily_rate * effective_days, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html', months=MONTHS)

@app.route('/salary')
def salary():
    return render_template('salary.html', months=MONTHS)

@app.route('/api/employees', methods=['GET'])
def get_employees():
    df = load_data()
    data = df.to_dict('records')
    return jsonify(data)

@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.json
    df = load_data()
    
    new_row = {
        'Name': data['name'],
        'Annual_Package': float(data['annual_package'])
    }
    for month in MONTHS:
        new_row[f'{month}_Absent'] = 0
    new_row['Remarks'] = ''
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    return jsonify({'success': True, 'message': 'Employee added successfully'})

@app.route('/api/employees/<int:index>', methods=['DELETE'])
def delete_employee(index):
    df = load_data()
    if 0 <= index < len(df):
        df = df.drop(index).reset_index(drop=True)
        save_data(df)
        return jsonify({'success': True, 'message': 'Employee deleted successfully'})
    return jsonify({'success': False, 'message': 'Employee not found'}), 404

@app.route('/api/employees/<int:index>', methods=['PUT'])
def update_employee(index):
    data = request.json
    df = load_data()
    
    if 0 <= index < len(df):
        if 'name' in data:
            df.at[index, 'Name'] = data['name']
        if 'annual_package' in data:
            df.at[index, 'Annual_Package'] = float(data['annual_package'])
        for month in MONTHS:
            key = f'{month}_Absent'
            if key in data:
                df.at[index, key] = int(data[key])
        if 'Remarks' in data:
            df.at[index, 'Remarks'] = str(data['Remarks'])
        
        save_data(df)
        return jsonify({'success': True, 'message': 'Employee updated successfully'})
    return jsonify({'success': False, 'message': 'Employee not found'}), 404

@app.route('/api/salary-data', methods=['GET'])
def get_salary_data():
    df = load_data()
    salary_data = []
    monthly_totals = {month: 0 for month in MONTHS}
    
    for _, row in df.iterrows():
        emp_data = {
            'name': row['Name'],
            'annual_package': row['Annual_Package'],
            'monthly_salaries': {},
            'total_salary': 0
        }
        
        for month in MONTHS:
            absent_days = row.get(f'{month}_Absent', 0)
            if pd.isna(absent_days):
                absent_days = 0
            working_days = WORKING_DAYS_2025[month]
            salary = calculate_salary(row['Annual_Package'], absent_days, working_days)
            emp_data['monthly_salaries'][month] = salary
            emp_data['total_salary'] += salary
            monthly_totals[month] += salary
        
        emp_data['total_salary'] = round(emp_data['total_salary'], 2)
        salary_data.append(emp_data)
    
    grand_total = round(sum(monthly_totals.values()), 2)
    monthly_totals = {k: round(v, 2) for k, v in monthly_totals.items()}
    
    return jsonify({
        'employees': salary_data,
        'monthly_totals': monthly_totals,
        'grand_total': grand_total,
        'working_days': WORKING_DAYS_2025
    })

@app.route('/api/working-days', methods=['GET'])
def get_working_days():
    return jsonify(WORKING_DAYS_2025)

@app.route('/api/working-days', methods=['PUT'])
def update_working_days():
    global WORKING_DAYS_2025
    data = request.json
    for month, days in data.items():
        if month in WORKING_DAYS_2025:
            WORKING_DAYS_2025[month] = int(days)
    return jsonify({'success': True, 'working_days': WORKING_DAYS_2025})

@app.route('/api/export/attendance/<format>')
def export_attendance(format):
    """Export attendance data as CSV or Excel."""
    df = load_data()
    
    # Rename columns for better readability
    column_mapping = {'Name': 'Employee Name', 'Annual_Package': 'Annual Package (₹)'}
    for month in MONTHS:
        column_mapping[f'{month}_Absent'] = f'{month[:3]} Absent Days'
    
    export_df = df.rename(columns=column_mapping)
    
    if format == 'csv':
        output = StringIO()
        export_df.to_csv(output, index=False)
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=attendance_data.csv'}
        )
    elif format == 'excel':
        output = BytesIO()
        export_df.to_excel(output, index=False, sheet_name='Attendance')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='attendance_data.xlsx'
        )
    return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/export/salary/<format>')
def export_salary(format):
    """Export salary data as CSV or Excel."""
    df = load_data()
    
    # Build salary data
    salary_rows = []
    monthly_totals = {month: 0 for month in MONTHS}
    grand_total = 0
    
    for _, row in df.iterrows():
        emp_row = {
            'Employee Name': row['Name'],
            'Annual Package (₹)': row['Annual_Package']
        }
        emp_total = 0
        
        for month in MONTHS:
            absent_days = row.get(f'{month}_Absent', 0)
            if pd.isna(absent_days):
                absent_days = 0
            working_days = WORKING_DAYS_2025[month]
            salary = calculate_salary(row['Annual_Package'], absent_days, working_days)
            emp_row[f'{month[:3]} Salary (₹)'] = salary
            emp_total += salary
            monthly_totals[month] += salary
        
        emp_row['Total Salary (₹)'] = round(emp_total, 2)
        grand_total += emp_total
        salary_rows.append(emp_row)
    
    # Add totals row
    totals_row = {'Employee Name': 'MONTHLY TOTAL', 'Annual Package (₹)': ''}
    for month in MONTHS:
        totals_row[f'{month[:3]} Salary (₹)'] = round(monthly_totals[month], 2)
    totals_row['Total Salary (₹)'] = round(grand_total, 2)
    salary_rows.append(totals_row)
    
    export_df = pd.DataFrame(salary_rows)
    
    if format == 'csv':
        output = StringIO()
        export_df.to_csv(output, index=False)
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=salary_data.csv'}
        )
    elif format == 'excel':
        output = BytesIO()
        export_df.to_excel(output, index=False, sheet_name='Salary')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='salary_data.xlsx'
        )
    return jsonify({'error': 'Invalid format'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
