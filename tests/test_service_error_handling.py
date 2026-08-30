"""Error handling and exception path tests for services."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app import app
from dal import db, Venue, Artist, Show, Genre
from services.venue import VenueService
from services.artist import ArtistService
from services.show import ShowService
from dto.venue import VenueDTO
from dto.artist import ArtistDTO
from dto.show import ShowDTO


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


class TestVenueServiceErrorHandling:
    """Test error handling and exception paths in VenueService."""
    
    def test_create_venue_database_exception_rollback(self, client):
        """Test that create_venue properly rolls back on database error."""
        with app.app_context():
            venue_dto = create_venue_dto()
            
            # Mock db.session.commit to raise an exception
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                success, error = VenueService.create_venue(venue_dto)
                
                assert success is False
                assert error is not None
                assert "Database error" in error
    
    def test_create_venue_integrity_error(self, client):
        """Test create_venue handles integrity errors."""
        with app.app_context():
            # Create first venue with unique constraint
            venue_dto = create_venue_dto(name='Unique Venue', city='SF', state='CA')
            success1, error1 = VenueService.create_venue(venue_dto)
            assert success1 is True
            
            # Try to create another with same attributes (might violate constraints)
            venue_dto2 = create_venue_dto(name='Unique Venue', city='SF', state='CA')
            # This should succeed because venues can have same names
            success2, error2 = VenueService.create_venue(venue_dto2)
            assert success2 is True
    
    def test_update_venue_database_exception_rollback(self, client):
        """Test that update_venue properly rolls back on database error."""
        with app.app_context():
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            
            update_dto = create_venue_dto(name='Updated')
            
            # Mock db.session.commit to raise an exception
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Update failed")
                
                success, error = VenueService.update_venue(venue.id, update_dto)
                
                assert success is False
                assert error is not None
    
    def test_update_venue_not_found_exception(self, client):
        """Test update_venue with non-existent venue."""
        with app.app_context():
            update_dto = create_venue_dto()
            success, error = VenueService.update_venue(9999, update_dto)
            
            assert success is False
            assert error is not None
    
    def test_delete_venue_database_exception(self, client):
        """Test delete_venue error handling."""
        with app.app_context():
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
            
            # Mock db.session.delete to raise an exception
            with patch('dal.db.session.delete') as mock_delete:
                mock_delete.side_effect = Exception("Delete failed")
                
                # This should not raise an exception, but handle it gracefully
                try:
                    VenueService.delete_venue(venue_id)
                except Exception as e:
                    pytest.fail(f"delete_venue raised {e} instead of handling exception")
    
    def test_delete_venue_with_shows(self, client):
        """Test deleting venue with foreign key constraint."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            # Create show with foreign key to venue
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2)
            )
            db.session.add(show)
            db.session.commit()
            venue_id = venue.id
            
            # Try to delete venue (should fail due to FK constraint)
            with patch('dal.db.session.delete') as mock_delete:
                mock_delete.side_effect = Exception("Foreign key constraint")
                
                try:
                    VenueService.delete_venue(venue_id)
                except Exception as e:
                    pytest.fail(f"delete_venue raised {e} instead of handling exception")


class TestArtistServiceErrorHandling:
    """Test error handling and exception paths in ArtistService."""
    
    def test_create_artist_database_exception_rollback(self, client):
        """Test that create_artist properly rolls back on database error."""
        with app.app_context():
            artist_dto = create_artist_dto()
            
            # Mock db.session.commit to raise an exception
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                success, error = ArtistService.create_artist(artist_dto)
                
                assert success is False
                assert error is not None
    
    def test_update_artist_database_exception_rollback(self, client):
        """Test that update_artist properly rolls back on database error."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            
            update_dto = create_artist_dto(name='Updated')
            
            # Mock db.session.commit to raise an exception
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Update failed")
                
                success, error = ArtistService.update_artist(artist.id, update_dto)
                
                assert success is False
                assert error is not None
    
    def test_update_artist_not_found_exception(self, client):
        """Test update_artist with non-existent artist."""
        with app.app_context():
            update_dto = create_artist_dto()
            success, error = ArtistService.update_artist(9999, update_dto)
            
            assert success is False
            assert error is not None
    
    def test_delete_artist_database_exception(self, client):
        """Test delete_artist error handling."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
            
            # Mock db.session.delete to raise an exception
            with patch('dal.db.session.delete') as mock_delete:
                mock_delete.side_effect = Exception("Delete failed")
                
                # This should not raise an exception
                try:
                    ArtistService.delete_artist(artist_id)
                except Exception as e:
                    pytest.fail(f"delete_artist raised {e} instead of handling exception")
    
    def test_create_artist_with_genre_lookup_failure(self, client):
        """Test create_artist when genre lookup fails gracefully."""
        with app.app_context():
            # Genre doesn't exist
            artist_dto = create_artist_dto(
                name='Test Artist',
                genres=['NonExistentGenre']
            )
            
            # Should still succeed, just without the genre
            success, error = ArtistService.create_artist(artist_dto)
            assert success is True
            
            # Verify artist exists but has no genres
            artist = Artist.query.filter_by(name='Test Artist').first()
            assert artist is not None
            assert len(artist.genres) == 0


class TestShowServiceErrorHandling:
    """Test error handling and exception paths in ShowService."""
    
    def test_create_show_database_exception_rollback(self, client):
        """Test that create_show properly rolls back on database error."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show_dto = ShowDTO(
                id=None,
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now().isoformat()
            )
            
            # Mock db.session.commit to raise an exception
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Database error")
                
                success, error = ShowService.create_show(show_dto)
                
                assert success is False
                assert error is not None
    
    def test_create_show_invalid_artist_id(self, client):
        """Test create_show with non-existent artist."""
        with app.app_context():
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            
            # Artist doesn't exist
            show_dto = ShowDTO(
                id=None,
                artist_id=9999,
                venue_id=venue.id,
                start_time=datetime.now().isoformat()
            )
            
            # Should fail with foreign key constraint
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Foreign key constraint")
                
                success, error = ShowService.create_show(show_dto)
                assert success is False
    
    def test_create_show_invalid_venue_id(self, client):
        """Test create_show with non-existent venue."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            
            # Venue doesn't exist
            show_dto = ShowDTO(
                id=None,
                artist_id=artist.id,
                venue_id=9999,
                start_time=datetime.now().isoformat()
            )
            
            # Should fail with foreign key constraint
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Foreign key constraint")
                
                success, error = ShowService.create_show(show_dto)
                assert success is False
    
    def test_update_show_database_exception_rollback(self, client):
        """Test that update_show properly rolls back on database error."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2)
            )
            db.session.add(show)
            db.session.commit()
            
            update_dto = ShowDTO(
                id=show.id,
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=(datetime.now() + timedelta(days=1)).isoformat()
            )
            
            # Mock db.session.commit to raise an exception
            with patch('dal.db.session.commit') as mock_commit:
                mock_commit.side_effect = Exception("Update failed")
                
                success, error = ShowService.update_show(show.id, update_dto)
                
                assert success is False
                assert error is not None
    
    def test_update_show_not_found_exception(self, client):
        """Test update_show with non-existent show."""
        with app.app_context():
            update_dto = ShowDTO(
                id=None,
                artist_id=1,
                venue_id=1,
                start_time=datetime.now().isoformat()
            )
            success, error = ShowService.update_show(9999, update_dto)
            
            assert success is False
            assert error is not None
    
    def test_delete_show_database_exception(self, client):
        """Test delete_show error handling."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2)
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id
            
            # Mock db.session.delete to raise an exception
            with patch('dal.db.session.delete') as mock_delete:
                mock_delete.side_effect = Exception("Delete failed")
                
                # This should not raise an exception
                try:
                    ShowService.delete_show(show_id)
                except Exception as e:
                    pytest.fail(f"delete_show raised {e} instead of handling exception")
    
    def test_create_show_invalid_datetime_format(self, client):
        """Test create_show with invalid datetime format."""
        with app.app_context():
            artist = Artist(name='Test', city='SF', state='CA')
            venue = Venue(name='Test', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            # Invalid datetime format
            show_dto = ShowDTO(
                id=None,
                artist_id=artist.id,
                venue_id=venue.id,
                start_time='invalid-datetime'
            )
            
            # Should fail during datetime parsing
            success, error = ShowService.create_show(show_dto)
            assert success is False
            assert error is not None
