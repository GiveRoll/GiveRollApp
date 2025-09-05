# GiveRoll

# technical-assesment4

# Create vitual environment
python -m venv venv_name

# Activate virtual environmemnt
# Mac OS
source venv_name/bin/activate
# Windows
venv_name\Scripts\activate.bat

# Root directory
cd backend

# Install required packages
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Runserver
python manage.py runserver

# API documentation
https://giveroll.onrender.com/redoc/
