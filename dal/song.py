"""SQLAlchemy model for Song."""

from dal import db
from datetime import datetime


class Song(db.Model):
    """Song model representing a single track on an album.
    
    Attributes:
        id (int): Primary key
        album_id (int): Foreign key to Album (required)
        title (str): Song title (required)
        duration (int): Duration in seconds
        track_number (int): Track position on the album
        genre (str): Genre of the song
        spotify_track_id (str): Spotify track identifier
        spotify_link (str): URL to song on Spotify
        created_at (datetime): Timestamp when song was created
    """
    __tablename__ = 'song'
    
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer)  # Duration in seconds
    track_number = db.Column(db.Integer)  # Track position on album
    genre = db.Column(db.String(120))
    spotify_track_id = db.Column(db.String)
    spotify_link = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Song {self.id} {self.title}>'
    
    def format_duration(self):
        """Format duration from seconds to MM:SS format."""
        if not self.duration:
            return '0:00'
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f'{minutes}:{seconds:02d}'
