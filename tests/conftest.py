"""Pytest configuration and fixtures for Fyyur tests."""

import os
import pytest
from datetime import datetime
from pathlib import Path

# CRITICAL: Set test database BEFORE importing app to ensure it uses SQLite
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

from app import app as flask_app
from dal import db
from dto.venue import VenueDTO
from dto.artist import ArtistDTO
from dto.show import ShowDTO


@pytest.fixture(scope='function', autouse=True)
def _ensure_test_database():
    """Ensure we NEVER connect to production database during tests.
    
    This runs before every test to verify the database is SQLite.
    """
    current_uri = flask_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    # Safety check: NEVER allow PostgreSQL connections during tests
    if 'postgresql' in current_uri.lower() or 'postgres' in current_uri.lower():
        raise RuntimeError(
            f"CRITICAL: Test attempted to use production database! "
            f"Database URI: {current_uri}\n"
            f"Tests must ONLY use SQLite (sqlite:///:memory:). "
            f"Set SQLALCHEMY_DATABASE_URI environment variable before running tests."
        )
    
    # Ensure we're using SQLite
    if 'sqlite' not in current_uri.lower():
        raise RuntimeError(
            f"CRITICAL: Test database is not SQLite! "
            f"Current URI: {current_uri}\n"
            f"Tests must use SQLite only. Set SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'"
        )


@pytest.fixture(scope='function', autouse=True)
def _patch_models_for_tests():
    """Auto-patch Venue and Artist models to provide defaults for required fields.
    
    This allows tests to create Venue/Artist objects without specifying all required fields,
    while the database still enforces the NOT NULL constraints.
    """
    from dal.venue import Venue
    from dal.artist import Artist
    
    # Store original __init__ methods
    venue_original_init = Venue.__init__
    artist_original_init = Artist.__init__
    
    def venue_init_with_defaults(self, **kwargs):
        # Provide defaults for required fields
        kwargs.setdefault('address', 'Test Address')
        kwargs.setdefault('city', 'Test City')
        kwargs.setdefault('state', 'CA')
        kwargs.setdefault('name', 'Test Venue')
        venue_original_init(self, **kwargs)
    
    def artist_init_with_defaults(self, **kwargs):
        # Provide defaults for required fields
        kwargs.setdefault('city', 'Test City')
        kwargs.setdefault('state', 'CA')
        kwargs.setdefault('name', 'Test Artist')
        artist_original_init(self, **kwargs)
    
    # Apply patches
    Venue.__init__ = venue_init_with_defaults
    Artist.__init__ = artist_init_with_defaults
    
    yield
    
    # Restore original __init__ methods
    Venue.__init__ = venue_original_init
    Artist.__init__ = artist_original_init


@pytest.fixture
def app():
    """Provide the Flask app instance with test configuration."""
    # Ensure test mode is enabled
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with flask_app.app_context():
        # Dispose of any stale connections
        db.engine.dispose()
        
        # Create all tables for this test
        db.create_all()
        
        yield flask_app
        
        # Cleanup after test
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client():
    """Create a test client with an in-memory SQLite database."""
    # Ensure test mode is enabled
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with flask_app.app_context():
        # Dispose of any stale connections
        db.engine.dispose()
        
        # Create all tables for this test
        db.create_all()
        
        yield flask_app.test_client()
        
        # Cleanup after test
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


# ============================================================================
# Helper Functions for Creating DTOs
# ============================================================================

def create_venue_dto(name='Test Venue', city='SF', state='CA', address='123 St', phone='555-1234', genres=None):
    """Helper to create VenueDTO objects."""
    if genres is None:
        genres = []
    return VenueDTO(
        id=None,
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        image_link='http://image.com/test.jpg',
        facebook_link='http://facebook.com/test',
        website='http://test.com',
        genres=genres
    )


def create_artist_dto(name='Test Artist', city='SF', state='CA', phone='555-1234', genres=None):
    """Helper to create ArtistDTO objects."""
    if genres is None:
        genres = []
    return ArtistDTO(
        id=None,
        name=name,
        city=city,
        state=state,
        phone=phone,
        image_link='http://image.com/test.jpg',
        facebook_link='http://facebook.com/test',
        website='http://test.com',
        genres=genres,
        seeking_venue=False,
        seeking_description=''
    )


def create_show_dto(artist_id, venue_id, start_time):
    """Helper to create ShowDTO objects."""
    return ShowDTO(
        id=None,
        artist_id=artist_id,
        venue_id=venue_id,
        start_time=start_time.isoformat() if isinstance(start_time, datetime) else start_time
    )


# ============================================================================
# Helper Functions for Creating Model Instances
# ============================================================================

def create_venue_model(name='Test Venue', city='SF', state='CA', address='123 St', phone='', genres=None):
    """Helper to create Venue model instances with all required fields."""
    from dal.venue import Venue
    if genres is None:
        genres = []
    venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        image_link='',
        facebook_link='',
        website='',
        seeking_talent=False,
        seeking_description=''
    )
    if genres:
        venue.genres = genres
    return venue


def create_artist_model(name='Test Artist', city='SF', state='CA', phone='', genres=None):
    """Helper to create Artist model instances with all required fields."""
    from dal.artist import Artist
    if genres is None:
        genres = []
    artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        image_link='',
        facebook_link='',
        website='',
        seeking_venue=False,
        seeking_description=''
    )
    if genres:
        artist.genres = genres
    return artist
