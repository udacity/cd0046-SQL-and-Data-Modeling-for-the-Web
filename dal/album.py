"""SQLAlchemy model for Album."""

from dal import db
from datetime import datetime


class Album(db.Model):
    """Album model representing a musical album by an artist.
    
    Attributes:
        id (int): Primary key
        artist_id (int): Foreign key to Artist
        title (str): Album title (required)
        release_date (date): Album release date
        description (str): Album description/notes
        image_link (str): URL to album cover art
        spotify_link (str): URL to album on Spotify
        created_at (datetime): Timestamp when album was created
    """
    __tablename__ = 'album'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    image_link = db.Column(db.String)
    spotify_link = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    artist = db.relationship('Artist', backref=db.backref('albums', cascade='all, delete-orphan'))
    songs = db.relationship('Song', backref='album', cascade='all, delete-orphan', lazy='joined')
    
    def __repr__(self):
        return f'<Album {self.id} {self.title}>'
