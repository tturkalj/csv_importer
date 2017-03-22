# csv_importer

Script for importing CSV files and Flask app

Project setup instructions:
    
    virtualenv --no-site-packages venv
    activate virtual environment
    pip install -r requirements.txt
    python setup.py develop
    python CsvImporter/utility/initialize_db.py
    python CsvImporter/utility/csv_importer.py
    python CsvImporter/app.py

For importing CSV data use: 
    
    python CsvImporter/utility/csv_importer.py

SQLite database is located at: 
    
    CsvImporter/models/csvimporter.db

Import errors are logged in: 
    
    CsvImporter/csv_import/errors

Application errors are logged in: 
    
    CsvImporter/log