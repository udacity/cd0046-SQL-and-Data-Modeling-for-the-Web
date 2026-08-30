"""Tests for database configuration and Flask-Migrate setup."""

import os
from sqlalchemy import text
from app import app
from dal import db, Venue, Artist


class TestDatabaseConfiguration:
    """Test database configuration and connectivity."""
    
    def test_database_uri_configured(self):
        """Test that SQLALCHEMY_DATABASE_URI is configured."""
        with app.app_context():
            assert app.config['SQLALCHEMY_DATABASE_URI'] is not None
            # Should have protocol and database name
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            assert 'sqlite' in db_uri or 'postgresql' in db_uri
    
    def test_sqlalchemy_track_modifications_disabled(self):
        """Test that SQLALCHEMY_TRACK_MODIFICATIONS is disabled."""
        with app.app_context():
            assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    
    def test_database_connection_works(self, client):
        """Test that we can connect to the database."""
        with app.app_context():
            # This should not raise an exception
            result = db.session.execute(text('SELECT 1'))
            assert result is not None


class TestFlaskMigrateInitialization:
    """Test Flask-Migrate is properly initialized."""
    
    def test_migrations_folder_exists(self):
        """Test that migrations folder exists."""
        migrations_path = os.path.join(os.path.dirname(__file__), '..', 'migrations')
        assert os.path.exists(migrations_path), "migrations folder does not exist"
        assert os.path.isdir(migrations_path)
    
    def test_migrations_env_exists(self):
        """Test that migrations/env.py exists."""
        env_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'env.py')
        assert os.path.exists(env_path), "migrations/env.py does not exist"
    
    def test_alembic_ini_exists(self):
        """Test that alembic.ini configuration exists."""
        alembic_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'alembic.ini')
        assert os.path.exists(alembic_path), "migrations/alembic.ini does not exist"
    
    def test_migrations_versions_folder_exists(self):
        """Test that migrations/versions folder exists."""
        versions_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'versions')
        assert os.path.exists(versions_path), "migrations/versions folder does not exist"
        assert os.path.isdir(versions_path)


class TestVenueAndArtistTables:
    """Test that Venue and Artist tables are created."""
    
    def test_venue_table_exists(self, client):
        """Test that Venue table can be created."""
        with app.app_context():
            # Verify table structure
            assert Venue.__tablename__ == 'venue'
            # Verify key columns exist
            assert hasattr(Venue, 'id')
            assert hasattr(Venue, 'name')
            assert hasattr(Venue, 'city')
            assert hasattr(Venue, 'state')
            assert hasattr(Venue, 'address')
            assert hasattr(Venue, 'phone')
    
    def test_artist_table_exists(self, client):
        """Test that Artist table can be created."""
        with app.app_context():
            # Verify table structure
            assert Artist.__tablename__ == 'artist'
            # Verify key columns exist
            assert hasattr(Artist, 'id')
            assert hasattr(Artist, 'name')
            assert hasattr(Artist, 'city')
            assert hasattr(Artist, 'state')
            assert hasattr(Artist, 'phone')
    
    def test_venue_crud_operations(self, client):
        """Test CRUD operations on Venue model."""
        with app.app_context():
            # Create
            venue = Venue(
                name='Test Venue',
                city='Test City',
                state='TS',
                address='123 Test St',
                phone='555-0123'
            )
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
            
            # Read
            retrieved = Venue.query.get(venue_id)
            assert retrieved is not None
            assert retrieved.name == 'Test Venue'
            
            # Update
            retrieved.phone = '555-0456'
            db.session.commit()
            updated = Venue.query.get(venue_id)
            assert updated.phone == '555-0456'
            
            # Delete
            db.session.delete(updated)
            db.session.commit()
            deleted = Venue.query.get(venue_id)
            assert deleted is None
    
    def test_artist_crud_operations(self, client):
        """Test CRUD operations on Artist model."""
        with app.app_context():
            # Create
            artist = Artist(
                name='Test Artist',
                city='Test City',
                state='TS',
                phone='555-0789'
            )
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
            
            # Read
            retrieved = Artist.query.get(artist_id)
            assert retrieved is not None
            assert retrieved.name == 'Test Artist'
            
            # Update
            retrieved.phone = '555-0999'
            db.session.commit()
            updated = Artist.query.get(artist_id)
            assert updated.phone == '555-0999'
            
            # Delete
            db.session.delete(updated)
            db.session.commit()
            deleted = Artist.query.get(artist_id)
            assert deleted is None
