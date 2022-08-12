from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Shows(db.Model):	
    __tablename__ = 'shows'	
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)	
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)	
    start_time = db.Column(db.DateTime, nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String)	
    website = db.Column(db.String)	
    seeking_description = db.Column(db.String)	
    seeking_talent = db.Column(db.String)	
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.today())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)	
    seeking_venue = db.Column(db.String)	
    seeking_description = db.Column(db.String)	
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.today())	
    venues = db.relationship('Venue', secondary='shows', backref=db.backref('artists', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
