import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
# For local development: postgresql://postgres:password@localhost:5432/fyyur
# For Docker dev container: set via environment variable (see docker-compose.yml)
SQLALCHEMY_DATABASE_URI = os.getenv(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://postgres:postgres@localhost:5432/fyyur'
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
