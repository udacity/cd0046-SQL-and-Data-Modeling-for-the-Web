"""
Venue model - part of the Data Access Layer.
Represents venue entities in the database.
"""

from datetime import datetime
from dal import db


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Many-to-many relationship with Genre through venue_genre junction table
    genres = db.relationship(
        'Genre',
        secondary='venue_genre'
    )