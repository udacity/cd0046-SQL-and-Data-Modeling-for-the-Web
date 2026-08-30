"""Tests for ShowService with real database queries."""

import pytest
from datetime import datetime, timedelta
from app import app
from dal import db, Venue, Artist, Show, Genre
from dal.availability import ArtistAvailability
from services.show import ShowService
from dto.show import ShowDTO


def create_show_dto(artist_id, venue_id, start_time):
    """Helper to create ShowDTO objects."""
    return ShowDTO(
        id=None,
        artist_id=artist_id,
        venue_id=venue_id,
        start_time=start_time.isoformat() if isinstance(start_time, datetime) else start_time
    )


def create_artist_availability(artist_id, day_of_week=0, start_hour=0, end_hour=23):
    """Helper to create artist availability for testing.
    
    By default creates all-day availability (00:00-23:59) for easier testing.
    """
    availability = ArtistAvailability(
        artist_id=artist_id,
        day_of_week=day_of_week,
        start_time=datetime.strptime(f"{start_hour:02d}:00", "%H:%M").time(),
        end_time=datetime.strptime(f"{end_hour:02d}:59", "%H:%M").time(),
        is_available=True
    )
    db.session.add(availability)
    db.session.commit()
    return availability


class TestShowService:
    """Test cases for ShowService with real database queries."""
    
    def test_get_all_shows_empty(self, client):
        """Test getting shows when database is empty."""
        with app.app_context():
            result = ShowService.get_all_shows()
            assert result == []
    
    def test_get_all_shows_with_data(self, client):
        """Test retrieving all shows with venue and artist data."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=30, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            
            result = ShowService.get_all_shows()
            assert len(result) == 1
            assert result[0]['artist_id'] == artist.id
            assert result[0]['venue_id'] == venue.id
            assert result[0]['artist_name'] == 'Test Artist'
            assert result[0]['venue_name'] == 'Test Venue'
    
    def test_show_show_by_show_id(self, client):
        """Test retrieving show details by ID."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            start_time = datetime.now() + timedelta(days=30)
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=2)
            )
            db.session.add(show)
            db.session.commit()
            
            result = ShowService.show_show_by_show_id(show.id)
            assert result is not None
            assert result['artist_id'] == artist.id
            assert result['venue_id'] == venue.id
            assert result['artist_name'] == 'Test Artist'
            assert result['venue_name'] == 'Test Venue'
    
    def test_show_show_by_show_id_not_found(self, client):
        """Test retrieving non-existent show."""
        with app.app_context():
            result = ShowService.show_show_by_show_id(9999)
            assert result is None
    
    def test_search_show_by_artist_and_venue(self, client):
        """Test searching shows by artist and venue."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=30, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            
            result = ShowService.search_show_by_artist_and_venue(
                artist_id=artist.id,
                venue_id=venue.id
            )
            assert len(result) == 1
            assert result[0]['artist_id'] == artist.id
            assert result[0]['venue_id'] == venue.id
    
    def test_search_show_by_artist_only(self, client):
        """Test searching shows by artist only."""
        with app.app_context():
            artist1 = Artist(name='Artist 1', city='SF', state='CA')
            artist2 = Artist(name='Artist 2', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist1, artist2, venue])
            db.session.commit()
            
            show1 = Show(artist_id=artist1.id, venue_id=venue.id, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
            show2 = Show(artist_id=artist2.id, venue_id=venue.id, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
            db.session.add_all([show1, show2])
            db.session.commit()
            
            result = ShowService.search_show_by_artist_and_venue(artist_id=artist1.id)
            assert len(result) == 1
            assert result[0]['artist_id'] == artist1.id
    
    def test_search_show_by_venue_only(self, client):
        """Test searching shows by venue only."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue1 = Venue(name='Venue 1', city='SF', state='CA')
            venue2 = Venue(name='Venue 2', city='SF', state='CA')
            db.session.add_all([artist, venue1, venue2])
            db.session.commit()
            
            show1 = Show(artist_id=artist.id, venue_id=venue1.id, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
            show2 = Show(artist_id=artist.id, venue_id=venue2.id, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
            db.session.add_all([show1, show2])
            db.session.commit()
            
            result = ShowService.search_show_by_artist_and_venue(venue_id=venue1.id)
            assert len(result) == 1
            assert result[0]['venue_id'] == venue1.id
    
    def test_create_show(self, client):
        """Test creating a new show."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            # Create availability for the artist
            start_time = datetime.now() + timedelta(days=30)
            day_of_week = start_time.weekday()
            create_artist_availability(artist.id, day_of_week=day_of_week)
            
            show_dto = create_show_dto(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=start_time
            )
            
            success, error = ShowService.create_show(show_dto)
            assert success is True
            assert error is None
            
            # Verify it was created
            created_show = Show.query.filter_by(
                artist_id=artist.id,
                venue_id=venue.id
            ).first()
            assert created_show is not None
    
    def test_create_show_with_z_timezone(self, client):
        """Test creating show with Z timezone in ISO format."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            # Create availability for Thursday (Dec 25, 2025 is a Thursday)
            create_artist_availability(artist.id, day_of_week=3)
            
            show_dto = ShowDTO(
                id=None,
                artist_id=artist.id,
                venue_id=venue.id,
                start_time='2025-12-25T19:30:00Z'
            )
            
            success, error = ShowService.create_show(show_dto)
            assert success is True
            
            # Verify it was created
            created_show = Show.query.filter_by(
                artist_id=artist.id,
                venue_id=venue.id
            ).first()
            assert created_show is not None
    
    def test_update_show(self, client):
        """Test updating show details."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            original_time = datetime.now() + timedelta(days=30)
            # Create availability for original day
            create_artist_availability(artist.id, day_of_week=original_time.weekday())
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=original_time,
                end_time=original_time + timedelta(hours=2)
            )
            db.session.add(show)
            db.session.commit()
            
            new_time = datetime.now() + timedelta(days=60)
            # Create availability for new day
            create_artist_availability(artist.id, day_of_week=new_time.weekday())
            
            update_dto = ShowDTO(
                id=show.id,
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=new_time.isoformat()
            )
            
            success, error = ShowService.update_show(show.id, update_dto)
            assert success is True
            
            # Verify update
            updated_show = Show.query.get(show.id)
            # Compare dates (times might differ slightly due to isoformat)
            assert updated_show.start_time.date() == new_time.date()
    
    def test_update_show_not_found(self, client):
        """Test updating non-existent show."""
        with app.app_context():
            new_time = datetime.now() + timedelta(days=30)
            update_dto = ShowDTO(
                id=None,
                artist_id=1,
                venue_id=1,
                start_time=new_time.isoformat()
            )
            success, error = ShowService.update_show(9999, update_dto)
            assert success is False
            assert error is not None
    
    def test_delete_show(self, client):
        """Test deleting a show."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=30, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id
            
            ShowService.delete_show(show_id)
            
            deleted = Show.query.get(show_id)
            assert deleted is None
    
    def test_delete_show_not_found(self, client):
        """Test deleting non-existent show."""
        with app.app_context():
            # Should not raise error
            ShowService.delete_show(9999)
