"""Tests for ArtistService with real database queries."""

import pytest
from datetime import datetime, timedelta
from app import app
from dal import db, Venue, Artist, Show, Genre
from services.artist import ArtistService
from dto.artist import ArtistDTO


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


class TestArtistService:
    """Test cases for ArtistService with real database queries."""
    
    def test_get_all_artists_empty(self, client):
        """Test getting artists when database is empty."""
        with app.app_context():
            result = ArtistService.get_all_artists()
            assert result == []
    
    def test_get_all_artists_multiple(self, client):
        """Test retrieving all artists."""
        with app.app_context():
            artist1 = Artist(name='Artist 1', city='SF', state='CA')
            artist2 = Artist(name='Artist 2', city='NYC', state='NY')
            db.session.add_all([artist1, artist2])
            db.session.commit()
            
            result = ArtistService.get_all_artists()
            assert len(result) == 2
            names = [a['name'] for a in result]
            assert 'Artist 1' in names
            assert 'Artist 2' in names
    
    def test_show_artist_by_artist_id(self, client):
        """Test retrieving artist details by ID."""
        with app.app_context():
            genre = Genre(name='Rock')
            db.session.add(genre)
            db.session.commit()
            
            artist = Artist(
                name='Test Artist',
                city='SF',
                state='CA',
                phone='555-1234'
            )
            artist.genres.append(genre)
            db.session.add(artist)
            db.session.commit()
            
            result = ArtistService.show_artist_by_artist_id(artist.id)
            assert result is not None
            assert result['name'] == 'Test Artist'
            assert 'Rock' in result['genres']
    
    def test_show_artist_by_artist_id_not_found(self, client):
        """Test retrieving non-existent artist."""
        with app.app_context():
            result = ArtistService.show_artist_by_artist_id(9999)
            assert result is None
    
    def test_show_artist_separates_past_and_upcoming_shows(self, client):
        """Test that artist details separate past and upcoming shows."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            past_show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime(2020, 1, 1, 12, 0, 0),
                end_time=datetime(2020, 1, 1, 14, 0, 0)
            )
            upcoming_show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=30),
                end_time=datetime.now() + timedelta(days=30, hours=2)
            )
            db.session.add_all([past_show, upcoming_show])
            db.session.commit()
            
            result = ArtistService.show_artist_by_artist_id(artist.id)
            assert len(result['past_shows']) == 1
            assert len(result['upcoming_shows']) == 1
            assert result['past_shows_count'] == 1
            assert result['upcoming_shows_count'] == 1
    
    def test_search_artist_by_name_empty(self, client):
        """Test searching artists when none match."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            
            result = ArtistService.search_artist_by_name('NonExistent')
            assert result['count'] == 0
            assert result['data'] == []
    
    def test_search_artist_by_name_partial(self, client):
        """Test partial name search for artists."""
        with app.app_context():
            artist1 = Artist(name='Guns N Petals', city='SF', state='CA')
            artist2 = Artist(name='Matt Quevedo', city='NYC', state='NY')
            db.session.add_all([artist1, artist2])
            db.session.commit()
            
            result = ArtistService.search_artist_by_name('Guns')
            assert result['count'] == 1
            assert result['data'][0]['name'] == 'Guns N Petals'
    
    def test_search_artist_case_insensitive(self, client):
        """Test that artist search is case-insensitive."""
        with app.app_context():
            artist = Artist(name='Guns N Petals', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            
            result = ArtistService.search_artist_by_name('guns')
            assert result['count'] == 1
            assert result['data'][0]['name'] == 'Guns N Petals'
    
    def test_create_artist_basic(self, client):
        """Test creating a new artist."""
        with app.app_context():
            artist_dto = create_artist_dto(
                name='New Artist',
                city='SF',
                state='CA'
            )
            
            success, error = ArtistService.create_artist(artist_dto)
            assert success is True
            assert error is None
            
            # Verify it was created
            created_artist = Artist.query.filter_by(name='New Artist').first()
            assert created_artist is not None
            assert created_artist.city == 'SF'
    
    def test_create_artist_with_genres(self, client):
        """Test creating artist with genres."""
        with app.app_context():
            genre1 = Genre(name='Jazz')
            genre2 = Genre(name='Rock')
            db.session.add_all([genre1, genre2])
            db.session.commit()
            
            artist_dto = create_artist_dto(
                name='New Artist',
                city='SF',
                state='CA',
                genres=['Jazz', 'Rock']
            )
            
            success, error = ArtistService.create_artist(artist_dto)
            assert success is True
            
            # Verify genres were added
            created_artist = Artist.query.filter_by(name='New Artist').first()
            genre_names = [g.name for g in created_artist.genres]
            assert 'Jazz' in genre_names
            assert 'Rock' in genre_names
    
    def test_update_artist_basic(self, client):
        """Test updating artist fields."""
        with app.app_context():
            artist = Artist(name='Old Name', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            
            update_dto = create_artist_dto(
                name='New Name',
                city='NYC',
                state='NY'
            )
            
            success, error = ArtistService.update_artist(artist.id, update_dto)
            assert success is True
            
            # Verify update
            updated_artist = Artist.query.get(artist.id)
            assert updated_artist.name == 'New Name'
            assert updated_artist.city == 'NYC'
    
    def test_update_artist_genres(self, client):
        """Test updating artist genres."""
        with app.app_context():
            genre1 = Genre(name='Jazz')
            genre2 = Genre(name='Rock')
            db.session.add_all([genre1, genre2])
            db.session.commit()
            
            artist = Artist(name='Test Artist', city='SF', state='CA')
            artist.genres.append(genre1)
            db.session.add(artist)
            db.session.commit()
            
            update_dto = create_artist_dto(
                name='Test Artist',
                city='SF',
                state='CA',
                genres=['Rock']
            )
            
            success, error = ArtistService.update_artist(artist.id, update_dto)
            assert success is True
            
            # Verify genres were updated
            updated_artist = Artist.query.get(artist.id)
            genre_names = [g.name for g in updated_artist.genres]
            assert 'Rock' in genre_names
            assert 'Jazz' not in genre_names
    
    def test_update_artist_not_found(self, client):
        """Test updating non-existent artist."""
        with app.app_context():
            update_dto = create_artist_dto(name='New Name')
            success, error = ArtistService.update_artist(9999, update_dto)
            assert success is False
            assert error is not None
    
    def test_delete_artist(self, client):
        """Test deleting an artist."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
            
            ArtistService.delete_artist(artist_id)
            
            deleted = Artist.query.get(artist_id)
            assert deleted is None
    
    def test_delete_artist_not_found(self, client):
        """Test deleting non-existent artist."""
        with app.app_context():
            # Should not raise error
            ArtistService.delete_artist(9999)
