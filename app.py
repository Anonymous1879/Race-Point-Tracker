from flask import Flask, render_template, send_file, after_this_request, request
import pandas as pd
from datetime import datetime
import os
from tempfile import NamedTemporaryFile
import json

app = Flask(__name__)

@app.route('/')
def home():
    # Ensure that 'index.html' is in a 'templates' folder
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    # Get the data sent from the frontend
    table_data = request.get_json()
    
    # Create DataFrame from the table data
    columns = ['Participation Team', 'Lap 1 Time', 'Lap 2 Time', 'Lap 3 Time', 'Total Time', 'Point Deduction', 'Total Points']
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
            # Delay the file removal until after the response has been sent
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Error removing or closing downloaded file handle: {e}")
        return response
    
    # Return the file to be downloaded
    return send_file(filename, as_attachment=True, download_name=f'race_results_{timestamp}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
