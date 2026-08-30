"""
Tests for AvailabilityService.

Tests the "Blackout Always Wins" logic:
- Blackout periods override available periods
- Date exceptions take priority over weekly recurring
- Double-booking detection
"""

import pytest
from datetime import datetime, time, timedelta, date
from services.availability import AvailabilityService
from dal import db
from dal.artist import Artist
from dal.availability import ArtistAvailability, ArtistAvailabilityException
from dal.show import Show
from dal.venue import Venue
from app import app


class TestAvailabilityService:
    """Test AvailabilityService.is_artist_available() method."""
    
    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Set up test database before each test."""
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()
    
    def test_available_when_slot_exists_and_no_blackout(self, client):
        """Artist should be available if slot exists and is marked available."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # Create Monday 9-5 available slot
            slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            db.session.add(slot)
            db.session.commit()
            
            # Monday 2-4 PM should be available
            monday_2pm = datetime(2026, 9, 7, 14, 0)  # Sept 7, 2026 is a Monday
            monday_4pm = datetime(2026, 9, 7, 16, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_2pm, monday_4pm
            )
            
            assert available is True
            assert "available" in reason.lower()
    
    def test_unavailable_when_no_slots_defined(self, client):
        """Artist should be unavailable if no availability slots exist for that day."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # No slots defined
            monday_2pm = datetime(2026, 9, 7, 14, 0)
            monday_4pm = datetime(2026, 9, 7, 16, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_2pm, monday_4pm
            )
            
            assert available is False
            assert "no availability" in reason.lower()
    
    def test_blackout_always_wins(self, client):
        """Blackout period should override available period (Blackout Always Wins)."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # Monday 9-5 available
            available_slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            
            # Monday 12-1 blackout
            blackout_slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(12, 0),
                end_time=time(13, 0),
                is_available=False
            )
            
            db.session.add_all([available_slot, blackout_slot])
            db.session.commit()
            
            # Monday 12:30-12:45 (during blackout) should be unavailable
            monday_1230 = datetime(2026, 9, 7, 12, 30)
            monday_1245 = datetime(2026, 9, 7, 12, 45)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_1230, monday_1245
            )
            
            assert available is False
            assert "blackout" in reason.lower()
    
    def test_available_outside_blackout(self, client):
        """Artist should be available outside blackout period."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # Monday 9-5 available
            available_slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            
            # Monday 12-1 blackout
            blackout_slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(12, 0),
                end_time=time(13, 0),
                is_available=False
            )
            
            db.session.add_all([available_slot, blackout_slot])
            db.session.commit()
            
            # Monday 2-4 PM (after blackout) should be available
            monday_2pm = datetime(2026, 9, 7, 14, 0)
            monday_4pm = datetime(2026, 9, 7, 16, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_2pm, monday_4pm
            )
            
            assert available is True
    
    def test_exception_overrides_weekly_availability(self, client):
        """Date exception should take priority over weekly recurring availability."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # Monday 9-5 available (recurring)
            slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            db.session.add(slot)
            
            # But Sept 7 (a Monday) has an exception: unavailable all day
            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 9, 7),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason="Holiday"
            )
            db.session.add(exception)
            db.session.commit()
            
            # Sept 7, 2-4 PM should be unavailable (exception takes priority)
            monday_2pm = datetime(2026, 9, 7, 14, 0)
            monday_4pm = datetime(2026, 9, 7, 16, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_2pm, monday_4pm
            )
            
            assert available is False
            assert "Holiday" in reason
    
    def test_double_booking_detection(self, client):
        """Should detect conflicts with existing shows."""
        with app.app_context():
            # Create test artist and venue
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            venue = Venue(name="Test Venue", city="Test City", state="CA", address="123 Main St")
            db.session.add(venue)
            db.session.commit()
            
            # Create a show Monday 2-4 PM
            existing_show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime(2026, 9, 7, 14, 0),
                end_time=datetime(2026, 9, 7, 16, 0)
            )
            db.session.add(existing_show)
            
            # Create availability slot
            slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            db.session.add(slot)
            db.session.commit()
            
            # Trying to book 1-3 PM (overlaps 2-4 PM show) should fail
            monday_1pm = datetime(2026, 9, 7, 13, 0)
            monday_3pm = datetime(2026, 9, 7, 15, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_1pm, monday_3pm
            )
            
            assert available is False
            assert "already has a show" in reason
    
    def test_exclude_show_id_from_double_booking(self, client):
        """Should allow updating a show without it conflicting with itself."""
        with app.app_context():
            # Create test artist and venue
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            venue = Venue(name="Test Venue", city="Test City", state="CA", address="123 Main St")
            db.session.add(venue)
            db.session.commit()
            
            # Create a show Monday 2-4 PM
            existing_show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime(2026, 9, 7, 14, 0),
                end_time=datetime(2026, 9, 7, 16, 0)
            )
            db.session.add(existing_show)
            
            # Create availability slot
            slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            db.session.add(slot)
            db.session.commit()
            
            # Updating the same show (2-4 PM) should be allowed
            monday_2pm = datetime(2026, 9, 7, 14, 0)
            monday_4pm = datetime(2026, 9, 7, 16, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_2pm, monday_4pm, exclude_show_id=existing_show.id
            )
            
            assert available is True
    
    def test_no_slots_outside_defined_hours(self, client):
        """Artist should be unavailable outside of defined availability hours."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # Monday 9-5 available
            slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            db.session.add(slot)
            db.session.commit()
            
            # Monday 7-8 AM (before availability) should be unavailable
            monday_7am = datetime(2026, 9, 7, 7, 0)
            monday_8am = datetime(2026, 9, 7, 8, 0)
            
            available, reason = AvailabilityService.is_artist_available(
                artist.id, monday_7am, monday_8am
            )
            
            assert available is False
            assert "no availability" in reason.lower()
    
    def test_summarize_artist_availability(self, client):
        """Should generate human-readable availability summary."""
        with app.app_context():
            # Create test artist
            artist = Artist(name="Test Artist", city="Test City", state="CA")
            db.session.add(artist)
            db.session.commit()
            
            # Monday 9-5
            monday_slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
            
            # Tuesday 10-6 with blackout 12-1
            tuesday_slot = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=1,
                start_time=time(10, 0),
                end_time=time(18, 0),
                is_available=True
            )
            
            tuesday_blackout = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=1,
                start_time=time(12, 0),
                end_time=time(13, 0),
                is_available=False
            )
            
            db.session.add_all([monday_slot, tuesday_slot, tuesday_blackout])
            db.session.commit()
            
            summary = AvailabilityService.summarize_artist_availability(artist.id)
            
            assert "Monday" in summary
            assert "09:00-17:00" in summary
            assert "Tuesday" in summary
            assert "Blackout" in summary
