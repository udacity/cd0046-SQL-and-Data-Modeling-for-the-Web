"""
SQLAlchemy models for Genre and junction tables.
"""
from datetime import datetime
from dal import db


class Genre(db.Model):
    """Genre model for music genres."""
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Genre {self.name}>'


class VenueGenre(db.Model):
    """Junction table for Venue-Genre many-to-many relationship."""
    __tablename__ = 'venue_genre'

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True)


class ArtistGenre(db.Model):
    """Junction table for Artist-Genre many-to-many relationship."""
    __tablename__ = 'artist_genre'

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True)
