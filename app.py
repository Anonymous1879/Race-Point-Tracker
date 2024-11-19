from flask import Flask, send_file
import pandas as pd
from datetime import datetime
import os
from tempfile import NamedTemporaryFile

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/download')
def download():
    # Create sample data if needed
    data = {
        'Participation Team': ['Team A'],
        'Lap 1 Time': ['01:30'],
        'Lap 2 Time': ['01:45'],
        'Lap 3 Time': ['01:35'],
        'Total Time': ['04:50'],
        'Point Deduction': [50],
        'Total Points': [950]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Use NamedTemporaryFile to save the file temporarily
    with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        filename = tmp_file.name
        # Save to Excel
        df.to_excel(filename, index=False)
    
    # Return the file to be downloaded
    return send_file(filename, as_attachment=True, download_name=f'race_results_{timestamp}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
