from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)

    shows = db.relationship('Show', backref='artist', lazy='joined', cascade='all, delete')
    
    @property
    def past_shows(self):
        results = []
        for show in self.shows:
            if show.start_time < datetime.now():
                results.append(show)

        data = []
        for result in results:
            venue = db.session.query(Venue).filter(Venue.id == result.venue_id).one_or_none()
            data.append({
                'venue_id': result.venue_id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': result.start_time.isoformat(),
            })

        return data
    
    @property
    def upcoming_shows(self):
        results = []
        for show in self.shows:
            if show.start_time > datetime.now():
                results.append(show)
        
        data = []
        for result in results:
            venue = db.session.query(Venue).filter(Venue.id == result.venue_id).one_or_none()
            data.append({
                'venue_id': result.venue_id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': result.start_time.isoformat(),
            })

        return data
    
    def to_dict(self):
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
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)

    shows = db.relationship('Show', backref='venue', lazy='joined', cascade='all, delete')
    
    @property
    def past_shows(self):
        results = []
        for show in self.shows:
            if show.start_time < datetime.now():
                results.append(show)
        
        data = []
        for result in results:
            artist = db.session.query(Artist).filter(Artist.id == result.artist_id).one_or_none()
            data.append({
                'artist_id': result.artist_id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': result.start_time.strftime('%m/%d/%Y, %H:%M'),
            })

        return data
    
    @property
    def upcoming_shows(self):
        results = []
        for show in self.shows:
            if show.start_time > datetime.now():
                results.append(show)
        
        data = []
        for result in results:
            artist = db.session.query(Artist).filter(Artist.id == result.artist_id).one_or_none()
            data.append({
                'artist_id': result.artist_id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': result.start_time.strftime('%m/%d/%Y, %H:%M'),
            })
            
        return data
    
    def to_dict(self):
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
    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time.strftime("%m/%d/%Y, %H:%M")}>'
    