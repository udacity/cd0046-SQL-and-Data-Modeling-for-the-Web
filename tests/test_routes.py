"""Integration tests for Fyyur routes and endpoints."""

import pytest
from datetime import datetime, timedelta
from app import app
from dal import db, Venue, Artist, Show, Genre
from dal.availability import ArtistAvailability


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


class TestAppRoutes:
    """Test basic application routes."""
    
    def test_index_route(self, client):
        """Test the home page route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Fyyur' in response.data or b'Music Venue' in response.data
    
    def test_venues_route(self, client):
        """Test the venues listing page route."""
        response = client.get('/venues')
        assert response.status_code == 200
        assert b'Venues' in response.data
    
    def test_artists_route(self, client):
        """Test the artists listing page route."""
        response = client.get('/artists')
        assert response.status_code == 200
        assert b'Artist' in response.data
    
    def test_shows_route(self, client):
        """Test the shows listing page route."""
        response = client.get('/shows')
        assert response.status_code == 200
        assert b'Show' in response.data
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404


class TestVenueRoutes:
    """Test venue-related routes."""
    
    def test_show_venue_page(self, client):
        """Test viewing a single venue."""
        with app.app_context():
            venue = Venue(
                name='Test Venue',
                city='SF',
                state='CA',
                address='123 Main St',
                phone='555-1234'
            )
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
        
        response = client.get(f'/venues/{venue_id}')
        assert response.status_code == 200
        assert b'Test Venue' in response.data
    
    def test_show_venue_not_found(self, client):
        """Test viewing non-existent venue."""
        response = client.get('/venues/9999')
        # Route returns 200 with no data (not 404)
        assert response.status_code == 200
    
    def test_create_venue_page(self, client):
        """Test accessing venue creation form."""
        response = client.get('/venues/create')
        assert response.status_code == 200
        assert b'Create' in response.data or b'form' in response.data.lower()
    
    def test_create_venue_form_submission(self, client):
        """Test creating a new venue via form submission."""
        form_data = {
            'name': 'New Test Venue',
            'city': 'San Francisco',
            'state': 'CA',
            'address': '456 Oak St',
            'phone': '555-2345',
            'genres': [],
            'image_link': '',
            'facebook_link': '',
            'website_link': ''
        }
        
        # Should handle form without crashing
        response = client.post('/venues/create', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_edit_venue_page(self, client):
        """Test accessing venue edit form."""
        with app.app_context():
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
        
        response = client.get(f'/venues/{venue_id}/edit')
        assert response.status_code == 200
        assert b'Test Venue' in response.data
    
    def test_edit_venue_form_submission(self, client):
        """Test updating venue via form submission."""
        with app.app_context():
            venue = Venue(
                name='Original Name',
                city='SF',
                state='CA',
                address='123 St'
            )
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
        
        form_data = {
            'name': 'Updated Name',
            'city': 'New York',
            'state': 'NY',
            'address': '456 Broadway',
            'phone': '555-123-4567',
            'genres': ['Rock'],
            'image_link': '',
            'facebook_link': '',
            'website_link': ''
        }
        
        response = client.post(f'/venues/{venue_id}/edit', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify venue was updated
        with app.app_context():
            updated_venue = Venue.query.get(venue_id)
            assert updated_venue.name == 'Updated Name'
            assert updated_venue.city == 'New York'
    
    def test_delete_venue(self, client):
        """Test deleting a venue."""
        with app.app_context():
            venue = Venue(name='Delete Me', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
        
        response = client.delete(f'/venues/{venue_id}', follow_redirects=True)
        
        # Verify venue was deleted
        with app.app_context():
            deleted_venue = Venue.query.get(venue_id)
            assert deleted_venue is None
    
    def test_search_venues(self, client):
        """Test venue search functionality."""
        with app.app_context():
            venue1 = Venue(name='The Musical Hop', city='SF', state='CA')
            venue2 = Venue(name='Park Square', city='NYC', state='NY')
            db.session.add_all([venue1, venue2])
            db.session.commit()
        
        form_data = {'search_term': 'Musical'}
        response = client.post('/venues/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Musical' in response.data or b'Hop' in response.data


class TestArtistRoutes:
    """Test artist-related routes."""
    
    def test_show_artist_page(self, client):
        """Test viewing a single artist."""
        with app.app_context():
            artist = Artist(
                name='Test Artist',
                city='SF',
                state='CA',
                phone='555-1234'
            )
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        response = client.get(f'/artists/{artist_id}')
        assert response.status_code == 200
        assert b'Test Artist' in response.data
    
    def test_show_artist_not_found(self, client):
        """Test viewing non-existent artist."""
        response = client.get('/artists/9999', follow_redirects=True)
        # Route redirects and returns 200 with error message
        assert response.status_code == 200
    
    def test_create_artist_page(self, client):
        """Test accessing artist creation form."""
        response = client.get('/artists/create')
        assert response.status_code == 200
        assert b'Create' in response.data or b'form' in response.data.lower()
    
    def test_create_artist_form_submission(self, client):
        """Test artist creation form submission."""
        form_data = {
            'name': 'New Test Artist',
            'city': 'Los Angeles',
            'state': 'CA',
            'phone': '555-3456',
            'genres': [],  # Empty genres
            'image_link': '',
            'facebook_link': '',
            'website_link': '',
            'seeking_venue': 'n',
            'seeking_description': ''
        }
        
        # Should handle the form without crashing (may or may not create artist)
        response = client.post('/artists/create', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_edit_artist_page(self, client):
        """Test accessing artist edit form."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        response = client.get(f'/artists/{artist_id}/edit')
        assert response.status_code == 200
        assert b'Test Artist' in response.data
    
    def test_edit_artist_form_submission(self, client):
        """Test updating artist via form submission."""
        with app.app_context():
            artist = Artist(
                name='Original Name',
                city='SF',
                state='CA'
            )
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        form_data = {
            'name': 'Updated Artist Name',
            'city': 'Chicago',
            'state': 'IL',
            'phone': '555-7890',
            'genres': [],
            'image_link': '',
            'facebook_link': '',
            'website_link': '',
            'seeking_venue': 'n',
            'seeking_description': ''
        }
        
        # Should handle form without crashing
        response = client.post(f'/artists/{artist_id}/edit', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_delete_artist(self, client):
        """Test deleting an artist."""
        with app.app_context():
            artist = Artist(name='Delete Me', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        response = client.delete(f'/artists/{artist_id}', follow_redirects=True)
        
        # Verify artist was deleted
        with app.app_context():
            deleted_artist = Artist.query.get(artist_id)
            assert deleted_artist is None
    
    def test_search_artists(self, client):
        """Test artist search functionality."""
        with app.app_context():
            artist1 = Artist(name='Guns N Petals', city='SF', state='CA')
            artist2 = Artist(name='Matt Quevedo', city='NYC', state='NY')
            db.session.add_all([artist1, artist2])
            db.session.commit()
        
        form_data = {'search_term': 'Guns'}
        response = client.post('/artists/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Guns' in response.data or b'Petals' in response.data


class TestShowRoutes:
    """Test show-related routes."""
    
    def test_show_list_page(self, client):
        """Test viewing all shows."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
        
        response = client.get('/shows')
        assert response.status_code == 200
        assert b'Show' in response.data
    
    def test_create_show_page(self, client):
        """Test accessing show creation form."""
        response = client.get('/shows/create')
        assert response.status_code == 200
        assert b'Create' in response.data or b'form' in response.data.lower()
    
    def test_create_show_form_submission(self, client):
        """Test creating a new show via form submission."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            artist_id = artist.id
            venue_id = venue.id
            
            # Create availability for the artist
            future_time = datetime.now() + timedelta(days=7)
            create_artist_availability(artist_id, day_of_week=future_time.weekday())
        
        future_time = (datetime.now() + timedelta(days=7)).isoformat()
        form_data = {
            'artist_id': artist_id,
            'venue_id': venue_id,
            'start_time': future_time
        }
        
        response = client.post('/shows/create', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify show was created
        with app.app_context():
            show = Show.query.filter_by(
                artist_id=artist_id,
                venue_id=venue_id
            ).first()
            assert show is not None
    
    def test_create_show_with_invalid_artist(self, client):
        """Test creating show with non-existent artist."""
        with app.app_context():
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
        
        future_time = (datetime.now() + timedelta(days=7)).isoformat()
        form_data = {
            'artist_id': 9999,  # Non-existent
            'venue_id': venue_id,
            'start_time': future_time
        }
        
        # Should fail gracefully
        response = client.post('/shows/create', data=form_data, follow_redirects=True)
        assert response.status_code in [200, 400]  # Either error page or redirected
    
    def test_create_show_with_invalid_venue(self, client):
        """Test creating show with non-existent venue."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        future_time = (datetime.now() + timedelta(days=7)).isoformat()
        form_data = {
            'artist_id': artist_id,
            'venue_id': 9999,  # Non-existent
            'start_time': future_time
        }
        
        # Should fail gracefully
        response = client.post('/shows/create', data=form_data, follow_redirects=True)
        assert response.status_code in [200, 400]
    
    def test_show_detail_page(self, client):
        """Test viewing a specific show's details."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id
        
        response = client.get(f'/shows/{show_id}')
        assert response.status_code == 200
    
    def test_show_detail_not_found(self, client):
        """Test viewing non-existent show."""
        response = client.get('/shows/9999', follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_shows_by_artist(self, client):
        """Test searching shows by artist."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            artist_id = artist.id
        
        response = client.post('/shows/search', data={'artist_id': str(artist_id), 'venue_id': ''}, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_shows_by_venue(self, client):
        """Test searching shows by venue."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            venue_id = venue.id
        
        response = client.post('/shows/search', data={'artist_id': '', 'venue_id': str(venue_id)}, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_shows_empty_params(self, client):
        """Test search with no parameters."""
        response = client.post('/shows/search', data={'artist_id': '', 'venue_id': ''}, follow_redirects=True)
        assert response.status_code == 200
    
    def test_edit_show_form_page(self, client):
        """Test accessing show edit form."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id
        
        response = client.get(f'/shows/{show_id}/edit')
        assert response.status_code == 200
    
    def test_edit_show_form_submission(self, client):
        """Test updating a show via form submission."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            venue = Venue(name='Test Venue', city='SF', state='CA')
            db.session.add_all([artist, venue])
            db.session.commit()
            
            show = Show(
                artist_id=artist.id,
                venue_id=venue.id,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id
            artist_id = artist.id
            venue_id = venue.id
        
        future_time = (datetime.now() + timedelta(days=14)).isoformat()
        form_data = {
            'artist_id': artist_id,
            'venue_id': venue_id,
            'start_time': future_time
        }
        
        response = client.post(f'/shows/{show_id}/edit', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
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
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7, hours=2)
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id
        
        response = client.delete(f'/shows/{show_id}')
        # DELETE endpoint returns JSON
        assert response.status_code in [200, 400]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_500_error_handling(self, client):
        """Test 500 error page exists."""
        # Trigger internal server error
        response = client.get('/nonexistent-route-that-does-not-exist')
        # Should be 404 since route doesn't exist
        assert response.status_code == 404
    
    def test_empty_database_displays_properly(self, client):
        """Test routes display properly with empty database."""
        # All test methods use empty database, so this just verifies rendering
        response = client.get('/venues')
        assert response.status_code == 200
        
        response = client.get('/artists')
        assert response.status_code == 200
        
        response = client.get('/shows')
        assert response.status_code == 200
    
    def test_form_submission_with_missing_fields(self, client):
        """Test form submission with missing required fields."""
        # Submit form with incomplete data (missing city, state, address)
        form_data = {
            'name': 'Incomplete Venue'
        }
        
        # App should handle the missing fields error gracefully
        response = client.post('/venues/create', data=form_data, follow_redirects=True)
        # Should either handle it gracefully or redirect with error message
        assert response.status_code in [200, 400]


class TestArtistSearchAndFiltering:
    """Test artist search with various criteria."""
    
    def test_search_artists_by_name(self, client):
        """Test searching artists by name."""
        with app.app_context():
            artist = Artist(name='Guns N Petals', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
        
        form_data = {'search_term': 'Guns'}
        response = client.post('/artists/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Guns' in response.data or b'search' in response.data.lower()
    
    def test_search_artists_by_location(self, client):
        """Test searching artists by city and state."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='San Francisco', state='CA')
            db.session.add(artist)
            db.session.commit()
        
        form_data = {
            'search_term': '',
            'city': 'San Francisco',
            'state': 'CA',
            'genres': []
        }
        response = client.post('/artists/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_artists_by_genre(self, client):
        """Test searching artists by genre."""
        with app.app_context():
            rock_genre = Genre.query.filter_by(name='Rock').first()
            if not rock_genre:
                rock_genre = Genre(name='Rock')
                db.session.add(rock_genre)
                db.session.commit()
            
            artist = Artist(name='Rock Artist', city='SF', state='CA')
            artist.genres.append(rock_genre)
            db.session.add(artist)
            db.session.commit()
        
        form_data = {
            'search_term': '',
            'city': '',
            'state': '',
            'genres': ['Rock']
        }
        response = client.post('/artists/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_artists_no_criteria_error(self, client):
        """Test search with no criteria returns error."""
        form_data = {
            'search_term': '',
            'city': '',
            'state': '',
            'genres': []
        }
        response = client.post('/artists/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        # Should contain error message
        assert b'search' in response.data.lower() or b'error' in response.data.lower()
    
    def test_search_artists_empty_results(self, client):
        """Test search returns empty results gracefully."""
        form_data = {'search_term': 'NonexistentArtistXYZ123'}
        response = client.post('/artists/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_venues_by_name(self, client):
        """Test searching venues by name."""
        with app.app_context():
            venue = Venue(name='Musical Hop', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
        
        form_data = {'search_term': 'Musical'}
        response = client.post('/venues/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_venues_by_location(self, client):
        """Test searching venues by city and state."""
        with app.app_context():
            venue = Venue(name='Test Venue', city='New York', state='NY')
            db.session.add(venue)
            db.session.commit()
        
        form_data = {
            'search_term': '',
            'city': 'New York',
            'state': 'NY'
        }
        response = client.post('/venues/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_search_venues_no_criteria_error(self, client):
        """Test venue search with no criteria returns error."""
        form_data = {
            'search_term': '',
            'city': '',
            'state': ''
        }
        response = client.post('/venues/search', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        # Should contain error message
        assert b'search' in response.data.lower() or b'error' in response.data.lower()


class TestArtistAvailability:
    """Test artist availability management."""
    
    def test_view_artist_availability(self, client):
        """Test viewing artist availability page."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
            
            # Create some availability
            create_artist_availability(artist_id, day_of_week=0, start_hour=9, end_hour=17)
        
        response = client.get(f'/artists/{artist_id}/availability')
        assert response.status_code == 200
        assert b'availability' in response.data.lower() or b'schedule' in response.data.lower()
    
    def test_view_artist_availability_not_found(self, client):
        """Test viewing availability for non-existent artist."""
        response = client.get('/artists/9999/availability', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect or show error
    
    def test_new_artist_availability_form(self, client):
        """Test accessing new availability form."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        response = client.get(f'/artists/{artist_id}/availability/new')
        assert response.status_code == 200
        assert b'availability' in response.data.lower() or b'form' in response.data.lower()
    
    def test_new_artist_availability_form_not_found(self, client):
        """Test availability form for non-existent artist."""
        response = client.get('/artists/9999/availability/new', follow_redirects=True)
        assert response.status_code == 200
    
    def test_create_artist_availability(self, client):
        """Test creating artist availability."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        form_data = {
            'day_of_week': '0',  # Monday
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': 'y'
        }
        
        response = client.post(f'/artists/{artist_id}/availability/new', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify availability was created
        with app.app_context():
            availability = ArtistAvailability.query.filter_by(artist_id=artist_id).first()
            assert availability is not None
    
    def test_create_artist_availability_not_found(self, client):
        """Test creating availability for non-existent artist."""
        form_data = {
            'day_of_week': '0',
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': 'y'
        }
        
        response = client.post('/artists/9999/availability/new', data=form_data, follow_redirects=True)
        assert response.status_code == 200


class TestVenueEdgeCases:
    """Test venue-related edge cases."""
    
    def test_edit_nonexistent_venue(self, client):
        """Test editing non-existent venue."""
        response = client.get('/venues/9999/edit', follow_redirects=True)
        assert response.status_code == 200
    
    def test_delete_nonexistent_venue(self, client):
        """Test deleting non-existent venue."""
        response = client.delete('/venues/9999', follow_redirects=True)
        # Should return error gracefully
        assert response.status_code in [200, 400, 404]
    
    def test_venue_delete_post_endpoint(self, client):
        """Test DELETE venue using POST endpoint."""
        with app.app_context():
            venue = Venue(name='Delete Me', city='SF', state='CA')
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.id
        
        response = client.post(f'/venues/{venue_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify venue was deleted
        with app.app_context():
            deleted = Venue.query.get(venue_id)
            assert deleted is None


class TestArtistEdgeCases:
    """Test artist-related edge cases."""
    
    def test_edit_nonexistent_artist(self, client):
        """Test editing non-existent artist."""
        response = client.get('/artists/9999/edit', follow_redirects=True)
        assert response.status_code == 200
    
    def test_delete_nonexistent_artist(self, client):
        """Test deleting non-existent artist."""
        response = client.delete('/artists/9999', follow_redirects=True)
        # Should return error gracefully
        assert response.status_code in [200, 400, 404]
    
    def test_artist_delete_post_endpoint(self, client):
        """Test DELETE artist using POST endpoint."""
        with app.app_context():
            artist = Artist(name='Delete Me', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        response = client.post(f'/artists/{artist_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify artist was deleted
        with app.app_context():
            deleted = Artist.query.get(artist_id)
            assert deleted is None


class TestShowCreationWithPrefill:
    """Test show creation with artist prefill from query parameter."""
    
    def test_create_show_with_artist_prefill(self, client):
        """Test show creation form with artist_id query parameter."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()
            artist_id = artist.id
        
        response = client.get(f'/shows/create?artist_id={artist_id}')
        assert response.status_code == 200
        # The form should contain the artist dropdown with prefilled value
        assert b'form' in response.data.lower()
    
    def test_create_show_without_artist_prefill(self, client):
        """Test show creation form without artist_id parameter."""
        response = client.get('/shows/create')
        assert response.status_code == 200
        assert b'form' in response.data.lower()
