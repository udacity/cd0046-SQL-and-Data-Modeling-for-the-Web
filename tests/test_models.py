"""Tests for Fyyur models."""

import pytest
from app import app
from dal import db, Venue, Artist


class TestVenueModel:
    """Test cases for the Venue model."""
    
    def test_venue_creation(self, client):
        """Test creating a new venue."""
        with app.app_context():
            venue = Venue(
                name='Test Venue',
                city='Test City',
                state='TS',
                address='123 Test St',
                phone='555-1234'
            )
            db.session.add(venue)
            db.session.commit()
            
            assert venue.id is not None
            assert venue.name == 'Test Venue'
            assert venue.city == 'Test City'
    
    def test_venue_retrieval(self, client):
        """Test retrieving a venue from database."""
        with app.app_context():
            venue = Venue(
                name='Retrieve Test Venue',
                city='Test City',
                state='TS'
            )
            db.session.add(venue)
            db.session.commit()
            
            retrieved = Venue.query.filter_by(name='Retrieve Test Venue').first()
            assert retrieved is not None
            assert retrieved.name == 'Retrieve Test Venue'


class TestArtistModel:
    """Test cases for the Artist model."""
    
    def test_artist_creation(self, client):
        """Test creating a new artist."""
        with app.app_context():
            artist = Artist(
                name='Test Artist',
                city='Test City',
                state='TS'
            )
            db.session.add(artist)
            db.session.commit()
            
            assert artist.id is not None
            assert artist.name == 'Test Artist'
    
    def test_artist_retrieval(self, client):
        """Test retrieving an artist from database."""
        with app.app_context():
            artist = Artist(
                name='Retrieve Test Artist',
                city='Test City',
                state='TS'
            )
            db.session.add(artist)
            db.session.commit()
            
            retrieved = Artist.query.filter_by(name='Retrieve Test Artist').first()
            assert retrieved is not None
            assert retrieved.name == 'Retrieve Test Artist'
