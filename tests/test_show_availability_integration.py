"""
Integration tests for availability checking in show creation and update workflows.

Tests verify that "Blackout Always Wins" logic prevents shows from being created
or updated when artist is unavailable, with proper error messages.
"""
import pytest
from datetime import datetime, timedelta
from dal import db
from dal.artist import Artist
from dal.venue import Venue
from dal.show import Show
from dal.availability import ArtistAvailability, ArtistAvailabilityException
from dto.show import ShowDTO
from services.show import ShowService


@pytest.fixture
def app():
    """Create app and initialize test database."""
    from app import app as flask_app
    
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


class TestShowAvailabilityIntegration:
    """Integration tests for show creation/update with availability checking."""
    
    def test_create_show_when_artist_available(self, app):
        """Test that show can be created when artist is available."""
        with app.app_context():
            # Setup: Create artist, venue, and availability slot
            artist = Artist(name="Available Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create Monday 09:00-17:00 availability
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("17:00", "%H:%M").time(),
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()
            
            # Create show on Monday 14:00-16:00 (within available hours)
            show_date = datetime(2026, 9, 7, 14, 0)  # Monday, Sept 7, 2026
            show_dto = ShowDTO(
                id=None,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=show_date.isoformat(),
                end_time=(show_date + timedelta(hours=2)).isoformat()
            )
            
            success, error = ShowService.create_show(show_dto)
            
            assert success is True
            assert error is None
            
            # Verify show was created
            show = Show.query.filter_by(artist_id=artist.id).first()
            assert show is not None
            assert show.start_time == show_date
    
    def test_cannot_create_show_during_blackout(self, app):
        """Test that show cannot be created during blackout period."""
        with app.app_context():
            # Setup: Create artist, venue, and blackout slot
            artist = Artist(name="Busy Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create Monday 09:00-17:00 available, but 12:00-13:00 blackout
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("17:00", "%H:%M").time(),
                is_available=True
            )
            blackout = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("12:00", "%H:%M").time(),
                end_time=datetime.strptime("13:00", "%H:%M").time(),
                is_available=False  # Blackout
            )
            db.session.add(availability)
            db.session.add(blackout)
            db.session.commit()
            
            # Try to create show during blackout: 12:30-13:30 (overlaps blackout)
            show_date = datetime(2026, 9, 7, 12, 30)  # Monday during blackout
            show_dto = ShowDTO(
                id=None,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=show_date.isoformat(),
                end_time=(show_date + timedelta(hours=1)).isoformat()
            )
            
            success, error = ShowService.create_show(show_dto)
            
            assert success is False
            assert error is not None
            assert "Blackout" in error or "unavailable" in error.lower()
            
            # Verify show was NOT created
            shows = Show.query.filter_by(artist_id=artist.id).all()
            assert len(shows) == 0
    
    def test_cannot_create_show_with_conflicting_show(self, app):
        """Test that show cannot be created if artist has conflicting show."""
        with app.app_context():
            # Setup: Create artist, venue
            artist = Artist(name="Conflict Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create availability slot for entire day
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("00:00", "%H:%M").time(),
                end_time=datetime.strptime("23:59", "%H:%M").time(),
                is_available=True
            )
            db.session.add(availability)
            db.session.flush()
            
            # Create existing show: Monday 14:00-16:00
            existing_show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime(2026, 9, 7, 14, 0),
                end_time=datetime(2026, 9, 7, 16, 0)
            )
            db.session.add(existing_show)
            db.session.commit()
            
            # Try to create overlapping show: Monday 15:00-17:00
            show_date = datetime(2026, 9, 7, 15, 0)
            show_dto = ShowDTO(
                id=None,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=show_date.isoformat(),
                end_time=(show_date + timedelta(hours=2)).isoformat()
            )
            
            success, error = ShowService.create_show(show_dto)
            
            assert success is False
            assert error is not None
            assert "already has a show" in error.lower() or "conflict" in error.lower()
            
            # Verify second show was NOT created
            shows = Show.query.filter_by(artist_id=artist.id).all()
            assert len(shows) == 1  # Only the original show
    
    def test_can_create_non_overlapping_shows(self, app):
        """Test that multiple non-overlapping shows can be created for same artist."""
        with app.app_context():
            # Setup: Create artist, venue
            artist = Artist(name="Multi-Show Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create availability slot for entire day
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("00:00", "%H:%M").time(),
                end_time=datetime.strptime("23:59", "%H:%M").time(),
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()
            
            # Create first show: Monday 14:00-16:00
            show1_date = datetime(2026, 9, 7, 14, 0)
            show1_dto = ShowDTO(
                id=None,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=show1_date.isoformat(),
                end_time=(show1_date + timedelta(hours=2)).isoformat()
            )
            success1, error1 = ShowService.create_show(show1_dto)
            assert success1 is True
            
            # Create second show: Monday 17:00-19:00 (after first show)
            show2_date = datetime(2026, 9, 7, 17, 0)
            show2_dto = ShowDTO(
                id=None,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=show2_date.isoformat(),
                end_time=(show2_date + timedelta(hours=2)).isoformat()
            )
            success2, error2 = ShowService.create_show(show2_dto)
            assert success2 is True
            
            # Verify both shows were created
            shows = Show.query.filter_by(artist_id=artist.id).all()
            assert len(shows) == 2
    
    def test_update_show_within_available_time(self, app):
        """Test that show can be updated to different time if still available."""
        with app.app_context():
            # Setup: Create artist, venue, availability
            artist = Artist(name="Update Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create availability: Monday 09:00-17:00
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("17:00", "%H:%M").time(),
                is_available=True
            )
            db.session.add(availability)
            db.session.flush()
            
            # Create initial show: Monday 10:00-12:00
            show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime(2026, 9, 7, 10, 0),
                end_time=datetime(2026, 9, 7, 12, 0)
            )
            db.session.add(show)
            db.session.commit()
            
            # Update show to different time: 14:00-16:00 (still available)
            new_start = datetime(2026, 9, 7, 14, 0)
            update_dto = ShowDTO(
                id=show.id,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=new_start.isoformat(),
                end_time=(new_start + timedelta(hours=2)).isoformat()
            )
            
            success, error = ShowService.update_show(show.id, update_dto)
            
            assert success is True
            assert error is None
            
            # Verify show was updated
            updated_show = Show.query.get(show.id)
            assert updated_show.start_time == new_start
    
    def test_cannot_update_show_to_blackout_time(self, app):
        """Test that show cannot be updated to blackout time."""
        with app.app_context():
            # Setup: Create artist, venue
            artist = Artist(name="Update Blackout Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create availability with blackout: Monday 09:00-17:00 available,
            # but 12:00-13:00 blackout
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("17:00", "%H:%M").time(),
                is_available=True
            )
            blackout = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("12:00", "%H:%M").time(),
                end_time=datetime.strptime("13:00", "%H:%M").time(),
                is_available=False
            )
            db.session.add(availability)
            db.session.add(blackout)
            db.session.flush()
            
            # Create show at 10:00-12:00 (valid)
            show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime(2026, 9, 7, 10, 0),
                end_time=datetime(2026, 9, 7, 12, 0)
            )
            db.session.add(show)
            db.session.commit()
            
            # Try to update to blackout time: 12:00-13:00
            new_start = datetime(2026, 9, 7, 12, 0)
            update_dto = ShowDTO(
                id=show.id,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=new_start.isoformat(),
                end_time=(new_start + timedelta(hours=1)).isoformat()
            )
            
            success, error = ShowService.update_show(show.id, update_dto)
            
            assert success is False
            assert error is not None
            assert "Blackout" in error or "unavailable" in error.lower()
            
            # Verify show was NOT updated
            unchanged_show = Show.query.get(show.id)
            assert unchanged_show.start_time == datetime(2026, 9, 7, 10, 0)
    
    def test_date_exception_blocks_show_creation(self, app):
        """Test that date exception overrides weekly availability."""
        with app.app_context():
            # Setup: Create artist, venue
            artist = Artist(name="Exception Artist")
            venue = Venue(name="Test Venue", city="Test City", state="TS")
            db.session.add(artist)
            db.session.add(venue)
            db.session.flush()
            
            # Create availability: Monday 09:00-17:00
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=datetime.strptime("09:00", "%H:%M").time(),
                end_time=datetime.strptime("17:00", "%H:%M").time(),
                is_available=True
            )
            db.session.add(availability)
            db.session.flush()
            
            # Create exception for Sept 7 (Monday) - all day unavailable
            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=datetime(2026, 9, 7).date(),
                start_time=datetime.strptime("00:00", "%H:%M").time(),
                end_time=datetime.strptime("23:59", "%H:%M").time(),
                is_available=False,
                reason="Festival tour"
            )
            db.session.add(exception)
            db.session.commit()
            
            # Try to create show on Sept 7 at 14:00 (normally available, but exception)
            show_date = datetime(2026, 9, 7, 14, 0)
            show_dto = ShowDTO(
                id=None,
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=show_date.isoformat(),
                end_time=(show_date + timedelta(hours=2)).isoformat()
            )
            
            success, error = ShowService.create_show(show_dto)
            
            assert success is False
            assert error is not None
            assert "Festival tour" in error or "unavailable" in error.lower()
