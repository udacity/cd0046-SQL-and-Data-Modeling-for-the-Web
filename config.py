import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = "postgresql://lwgrfwkq:I58OfvJFN7iXM1m4E1Qcv74U2TgwgcV5@silly.db.elephantsql.com/lwgrfwkq"
