"""Tests for VenueService with real database queries."""

import pytest
from datetime import datetime, timedelta
from app import app
from dal import db, Venue, Artist, Show, Genre
from services.venue import VenueService
from dto.venue import VenueDTO


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


class TestVenueService:
    """Test cases for VenueService with real database queries."""
    
    def test_get_venues_grouped_by_location_empty(self, client):
        """Test getting venues when database is empty."""
        with app.app_context():
            result = VenueService.get_venues_grouped_by_location()
            assert result == []
    
    def test_get_venues_grouped_by_location_single(self, client):
        """Test grouping venues by location with single venue."""
        with app.app_context():
            venue = Venue(
                name='Test Venue',
                city='San Francisco',
                state='CA',
                address='123 Test St',
                phone='555-1234'
            )
            db.session.add(venue)
            db.session.commit()
            
            result = VenueService.get_venues_grouped_by_location()
            assert len(result) == 1
            assert result[0]['city'] == 'San Francisco'
            assert result[0]['state'] == 'CA'
            assert len(result[0]['venues']) == 1
            assert result[0]['venues'][0]['name'] == 'Test Venue'
    
    def test_get_venues_grouped_by_location_multiple(self, client):
        """Test grouping multiple venues by location."""
        with app.app_context():
            venue1 = Venue(name='Venue 1', city='SF', state='CA', address='123 St')
            venue2 = Venue(name='Venue 2', city='SF', state='CA', address='456 St')
            venue3 = Venue(name='Venue 3', city='NYC', state='NY', address='789 Ave')
            db.session.add_all([venue1, venue2, venue3])
            db.session.commit()
            
            result = VenueService.get_venues_grouped_by_location()
            assert len(result) == 2
            # Find SF group
            sf_group = next((g for g in result if g['city'] == 'SF'), None)
            assert sf_group is not None
            assert len(sf_group['venues']) == 2
    
    def test_get_venues_grouped_by_location_with_shows(self, client):
        """Test venue grouping includes upcoming show counts."""
        with app.app_context():
            # Create genre
            genre = Genre(name='Jazz')
            db.session.add(genre)
            db.session.commit()
            
            # Create artist and venue
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA', address='123 St')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            # Create future show
            future_show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=30, hours=2)
            )
            db.session.add(future_show)
            db.session.commit()
            
            result = VenueService.get_venues_grouped_by_location()
            assert len(result) == 1
            assert result[0]['venues'][0]['num_upcoming_shows'] == 1
    
    def test_show_venue_by_venue_id(self, client):
        """Test retrieving venue details by ID."""
        with app.app_context():
            # Create genre
            genre = Genre(name='Jazz')
            db.session.add(genre)
            db.session.commit()
            
            venue = Venue(
                name='Test Venue',
                city='SF',
                state='CA',
                phone='555-1234',
                website='http://test.com'
            )
            venue.genres.append(genre)
            db.session.add(venue)
            db.session.commit()
            
            result = VenueService.show_venue_by_venue_id(venue.id)
            assert result is not None
            assert result['name'] == 'Test Venue'
            assert result['city'] == 'SF'
            assert 'Jazz' in result['genres']
    
    def test_show_venue_by_venue_id_not_found(self, client):
        """Test retrieving non-existent venue."""
        with app.app_context():
            result = VenueService.show_venue_by_venue_id(9999)
            assert result is None
    
    def test_show_venue_separates_past_and_upcoming_shows(self, client):
        """Test that venue details separate past and upcoming shows."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            # Add past show
            past_show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime(2020, 1, 1, 12, 0, 0),
                end_time=datetime(2020, 1, 1, 14, 0, 0)
            )
            # Add upcoming show
            upcoming_show = Show(
                venue_id=venue.id,
                artist_id=artist.id,
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=30, hours=2)
            )
            db.session.add_all([past_show, upcoming_show])
            db.session.commit()
            
            result = VenueService.show_venue_by_venue_id(venue.id)
            assert len(result['past_shows']) == 1
            assert len(result['upcoming_shows']) == 1
            assert result['past_shows_count'] == 1
            assert result['upcoming_shows_count'] == 1
    
    def test_search_venue_by_name_empty(self, client):
        """Test searching venues when none match."""
        with app.app_context():
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            
            result = VenueService.search_venue_by_name('NonExistent')
            assert result['count'] == 0
            assert result['data'] == []
    
    def test_search_venue_by_name_partial(self, client):
        """Test partial name search for venues."""
        with app.app_context():
            venue1 = Venue(name='The Musical Hop', city='SF', state='CA')
            venue2 = Venue(name='Park Square', city='NYC', state='NY')
            db.session.add_all([venue1, venue2])
            db.session.commit()
            
            result = VenueService.search_venue_by_name('Musical')
            assert result['count'] == 1
            assert result['data'][0]['name'] == 'The Musical Hop'
    
    def test_search_venue_case_insensitive(self, client):
        """Test that venue search is case-insensitive."""
        with app.app_context():
            venue = Venue(name='The Musical Hop', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            
            result = VenueService.search_venue_by_name('musical')
            assert result['count'] == 1
            assert result['data'][0]['name'] == 'The Musical Hop'
    
    def test_create_venue_basic(self, client):
        """Test creating a new venue."""
        with app.app_context():
            venue_dto = create_venue_dto(
                name='New Venue',
                city='SF',
                state='CA'
            )
            
            success, error = VenueService.create_venue(venue_dto)
            assert success is True
            assert error is None
            
            # Verify it was created
            created_venue = Venue.query.filter_by(name='New Venue').first()
            assert created_venue is not None
            assert created_venue.city == 'SF'
    
    def test_create_venue_with_genres(self, client):
        """Test creating venue with genres."""
        with app.app_context():
            # Create genres
            genre1 = Genre(name='Jazz')
            genre2 = Genre(name='Rock')
            db.session.add_all([genre1, genre2])
            db.session.commit()
            
            venue_dto = create_venue_dto(
                name='New Venue',
                city='SF',
                state='CA',
                genres=['Jazz', 'Rock']
            )
            
            success, error = VenueService.create_venue(venue_dto)
            assert success is True
            
            # Verify genres were added
            created_venue = Venue.query.filter_by(name='New Venue').first()
            genre_names = [g.name for g in created_venue.genres]
            assert 'Jazz' in genre_names
            assert 'Rock' in genre_names
    
    def test_create_venue_with_invalid_genre(self, client):
        """Test creating venue with non-existent genre."""
        with app.app_context():
            venue_dto = create_venue_dto(
                name='New Venue',
                city='SF',
                state='CA',
                genres=['NonExistentGenre']
            )
            
            success, error = VenueService.create_venue(venue_dto)
            # Should still succeed but with no genres added
            assert success is True
            
            created_venue = Venue.query.filter_by(name='New Venue').first()
            assert len(created_venue.genres) == 0
    
    def test_update_venue_basic(self, client):
        """Test updating venue fields."""
        with app.app_context():
            venue = Venue(name='Old Name', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            
            update_dto = create_venue_dto(
                name='New Name',
                city='NYC',
                state='NY'
            )
            
            success, error = VenueService.update_venue(venue.id, update_dto)
            assert success is True
            
            # Verify update
            updated_venue = Venue.query.get(venue.id)
            assert updated_venue.name == 'New Name'
            assert updated_venue.city == 'NYC'
    
    def test_update_venue_genres(self, client):
        """Test updating venue genres."""
        with app.app_context():
            genre1 = Genre(name='Jazz')
            genre2 = Genre(name='Rock')
            db.session.add_all([genre1, genre2])
            db.session.commit()
            
            venue = Venue(name='Test Venue', city='SF', state='CA')
            venue.genres.append(genre1)
            db.session.add(venue)
            db.session.commit()
            
            update_dto = create_venue_dto(
                name='Test Venue',
                city='SF',
                state='CA',
                genres=['Rock']
            )
            
            success, error = VenueService.update_venue(venue.id, update_dto)
            assert success is True
            
            # Verify genres were updated
            updated_venue = Venue.query.get(venue.id)
            genre_names = [g.name for g in updated_venue.genres]
            assert 'Rock' in genre_names
            assert 'Jazz' not in genre_names
    
    def test_update_venue_not_found(self, client):
        """Test updating non-existent venue."""
        with app.app_context():
            update_dto = create_venue_dto(name='New Name')
            success, error = VenueService.update_venue(9999, update_dto)
            assert success is False
            assert error is not None
    
    def test_delete_venue(self, client):
        """Test deleting a venue."""
        with app.app_context():
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
            
            VenueService.delete_venue(venue_id)
            
            deleted = Venue.query.get(venue_id)
            assert deleted is None
    
    def test_delete_venue_not_found(self, client):
        """Test deleting non-existent venue."""
        with app.app_context():
            # Should not raise error
            VenueService.delete_venue(9999)
