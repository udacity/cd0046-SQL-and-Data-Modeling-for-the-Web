from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

db = SQLAlchemy()

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column( db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    past_shows = []
    upcoming_shows = []
    
    genres = db.relationship('Genre', 
                             back_populates='artist', 
                             uselist=True)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade='all,delete')
    
    def get_past_shows(self):
        data = []
        results = self.shows.filter(Show.start_time < datetime.now()).order_by(desc(Show.start_time)).all()
        for result in results:
            data.append({
                'venue_id': result.venue_id,
                'venue_name': result.venue.name,
                'venue_image_link': result.venue.image_link,
                'start_time': str(result.start_time),
            })
        return data
    
    def get_upcoming_shows(self):
        data = []
        results = self.shows.filter(Show.start_time > datetime.now()).order_by(Show.start_time).all()
        for result in results:
            data.append({
                'venue_id': result.venue_id,
                'venue_name': result.venue.name,
                'venue_image_link': result.venue.image_link,
                'start_time': str(result.start_time),
            })
        return data
    
    def to_dict(self):
        self.past_shows = self.get_past_shows()
        self.upcoming_shows = self.get_upcoming_shows()
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'genres': self.genres,
            'past_shows': self.past_shows,
            'upcoming_shows': self.upcoming_shows,
            'past_shows_count': len(self.past_shows),
            'upcoming_shows_count': len(self.upcoming_shows),
        }
        

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    artists = db.relationship('Artist', back_populates='genres', uselist=True)
    venues = db.relationship('Venue', back_populates='genres', uselist=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'artists': self.artists,
            'venues': self.venues,
        }


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    past_shows = []
    upcoming_shows = []
    
    genres = db.relationship('Genre', back_populates='venues', uselist=True)
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade='all,delete')
    
    def get_past_shows(self):
        data = []
        results = self.shows.filter(Show.start_time < datetime.now()).order_by(desc(Show.start_time)).all()
        for result in results:
            data.append({
                'artist_id': result.artist_id,
                'artist_name': result.artist.name,
                'artist_image_link': result.artist.image_link,
                'start_time': str(result.start_time),
            })
        return data
    
    def get_upcoming_shows(self):
        data = []
        results = self.shows.filter(Show.start_time > datetime.now()).order_by(Show.start_time).all()
        for result in results:
            data.append({
                'artist_id': result.artist_id,
                'artist_name': result.artist.name,
                'artist_image_link': result.artist.image_link,
                'start_time': str(result.start_time),
            })
        return data
    
    def to_dict(self):
        self.past_shows = self.get_past_shows()
        self.upcoming_shows = self.get_upcoming_shows()
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'genres': self.genres,
            'past_shows': self.past_shows,
            'upcoming_shows': self.upcoming_shows,
            'past_shows_count': len(self.past_shows),
            'upcoming_shows_count': len(self.upcoming_shows),
        }
        

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'))
    
    artist = db.relationship('Artist', back_populates='show')
    venue = db.relationship('Venue', back_populates='show')
    
    def to_dict(self):
        return {
            'id': self.id,
            'start_time': self.start_time,
            'artist_id': self.artist_id,
            'venue_id': self.venue_id,
        }
