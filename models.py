from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# *DONE: connected to a local postgresql database via config.py

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

    # *DONE: implemented any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # *DONE: implemented missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

# *DONE Implemented Show and Artist models, and completed all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} {self.artist_id} {self.venue_id}>'
