# Setup
- Assuming you already have python and MySQL and MySQL workbench

# Virtual Environment (Windows)
- In the root directory, create a virtual environment as follows:
### py -3 -m venv venv
### venv\Scripts\activate

# Virtual Environment (Mac)
- In the root directory, create a virtual environment as follows:
### python3 -m venv venv
### venv/bin/activate

# Install all required libraries and dependencies from requirements.txt provided:
### pip install -r requirements.txt

# Database Configuration:
- Open the db_config.py file and change the password to your SQL passwod

# Creation of DB:
- Go to the root directory and run the following:
### flask shell
### from app import db
### db.create_all()
### exit()

# Running the backend:
- In the directory containing the Virtual environment run the following:
### set FLASK_APP=app
### set FLASK_ENV=development
### flask run
- You are good to go!

# Structure:
- The model folder contains the data models each containing database model and schema.
- The main python file is the app.py with is the main backend file that contains all the routes.
- The virtual environment is in the venv folder.
- requiremtns.txt file contains all the required libraries and dependencies with the versions used.
- db_config.py is the configuration file for the database.
- Procfile is the configuration file for Heroku for deployment