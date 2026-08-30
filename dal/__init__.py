"""Data Access Layer - manages all database models and queries."""

from flask_sqlalchemy import SQLAlchemy

# Single shared database instance used across entire app
db = SQLAlchemy()

# Import models so they're registered with db
# Genre must be imported first since Venue and Artist depend on it
from dal.genre import Genre, VenueGenre, ArtistGenre
from dal.venue import Venue
from dal.artist import Artist
from dal.show import Show
from dal.album import Album
from dal.song import Song

__all__ = ['db', 'Genre', 'VenueGenre', 'ArtistGenre', 'Venue', 'Artist', 'Show', 'Album', 'Song']
