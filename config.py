import os

# DB_USER = os.environ.get('DB_USER', 'postgres')
# DB_HOST = os.environ.get('DB_HOST', 'localhost:5432')
# DB_NAME = os.environ.get('DB_NAME', 'fyyur')

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# SQLALCHEMY_DATABASE_URI = 'postgresql://{}@{}/{}'.format(DB_USER, DB_HOST, DB_NAME)
SQLALCHEMY_DATABASE_URI = 'postgresql:///fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
