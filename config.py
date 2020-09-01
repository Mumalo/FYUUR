import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True  # Set to false on production

# Connect to the database

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = os.environ["FYYUR_DB_URL"]
