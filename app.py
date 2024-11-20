from flask import Flask, render_template, send_file, after_this_request, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import os
from tempfile import NamedTemporaryFile
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Please upload an Excel file (.xlsx)'}), 400
    
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Replace NaN values with None (which will be converted to null in JSON)
        df = df.replace({np.nan: None})
        
        # Convert DataFrame to list of lists for frontend
        data = df.values.tolist()
        
        # Convert any remaining numpy types to Python native types
        data = [[None if pd.isna(cell) else 
                int(cell) if isinstance(cell, np.integer) else
                float(cell) if isinstance(cell, np.floating) else
                str(cell) for cell in row] for row in data]
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download():
    # Get the data sent from the frontend
    table_data = request.get_json()
    
    # Create DataFrame from the table data
    columns = [
        'Participation Team', 
        'Lap 1 Time', 
        'Lap 2 Time', 
        'Lap 3 Time', 
        'Total Time', 
        'Point Deduction', 
        'Total Points', 
        'Central Line', 
        'Opponent Track', 
        'No Mobility', 
        'Ramp Maneuver', 
        'Collision'
    ]
    df = pd.DataFrame(table_data, columns=columns)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Use NamedTemporaryFile to save the file temporarily
    with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        filename = tmp_file.name
        # Save to Excel
        df.to_excel(filename, index=False)
    
    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Error removing or closing downloaded file handle: {e}")
        return response
    
    return send_file(filename, as_attachment=True, download_name=f'race_results_{timestamp}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)