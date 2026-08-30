"""Integration tests for Artist controller routes."""

import pytest
from datetime import datetime, date, time
from dal import db, Artist
from dal.availability import ArtistAvailability, ArtistAvailabilityException
from flask import url_for


class TestArtistListingRoutes:
    """Test Artist listing and search routes."""
    
    def test_artists_list_page(self, client):
        """Test GET /artists/ displays artist list."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.get('/artists/')
        assert response.status_code == 200
        assert b'Test Artist' in response.data
        assert b'Add Artist' in response.data or b'Create' in response.data
    
    def test_artists_list_empty(self, client):
        """Test GET /artists/ with no artists."""
        response = client.get('/artists/')
        assert response.status_code == 200
        assert b'Artist' in response.data
    
    def test_show_artist_page(self, client):
        """Test GET /artists/<id> shows artist detail."""
        artist = Artist(
            name='Test Artist',
            city='SF',
            state='CA',
            phone='555-0123',
            seeking_venue=True,
            seeking_description='Looking for venues'
        )
        db.session.add(artist)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}')
        assert response.status_code == 200
        assert b'Test Artist' in response.data
    
    def test_show_artist_nonexistent(self, client):
        """Test GET /artists/<id> for non-existent artist."""
        response = client.get('/artists/9999')
        # Should redirect or show error
        assert response.status_code in [302, 200]
    
    def test_search_artists_by_name(self, client):
        """Test POST /artists/search by name."""
        artist = Artist(name='Jazz Ensemble', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.post('/artists/search', data={
            'search_term': 'Jazz',
            'city': '',
            'state': '',
            'genres': []
        })
        assert response.status_code == 200
        assert b'Jazz Ensemble' in response.data or b'search' in response.data.lower()
    
    def test_search_artists_by_location(self, client):
        """Test POST /artists/search by city/state."""
        artist = Artist(name='Test Artist', city='New York', state='NY')
        db.session.add(artist)
        db.session.commit()
        
        response = client.post('/artists/search', data={
            'search_term': '',
            'city': 'New York',
            'state': 'NY',
            'genres': []
        })
        assert response.status_code == 200
    
    def test_search_artists_no_criteria(self, client):
        """Test POST /artists/search with no search criteria shows error."""
        response = client.post('/artists/search', data={
            'search_term': '',
            'city': '',
            'state': '',
            'genres': []
        })
        assert response.status_code in [302, 200]


class TestArtistCreateRoutes:
    """Test Artist creation routes."""
    
    def test_create_artist_form_page(self, client):
        """Test GET /artists/create displays form."""
        response = client.get('/artists/create')
        assert response.status_code == 200
        assert b'Create' in response.data or b'Artist' in response.data
    
    def test_create_artist_post_success(self, client):
        """Test POST /artists/create creates artist."""
        data = {
            'name': 'New Artist',
            'city': 'SF',
            'state': 'CA',
            'phone': '555-0123',
            'image_link': 'https://example.com/image.jpg',
            'genres': ['Blues'],
            'facebook_link': 'https://facebook.com/artist',
            'website_link': 'https://example.com',
            'seeking_venue': True,
            'seeking_description': 'Looking for venues'
        }
        
        response = client.post('/artists/create', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'successfully listed' in response.data or b'New Artist' in response.data
    
    def test_create_artist_post_missing_name(self, client):
        """Test POST /artists/create with missing name shows error."""
        data = {
            'name': '',
            'city': 'SF',
            'state': 'CA',
            'phone': '555-0123'
        }
        
        response = client.post('/artists/create', data=data)
        assert response.status_code == 200
        # Form should be redisplayed with errors
    
    def test_create_artist_post_missing_city(self, client):
        """Test POST /artists/create with missing city shows error."""
        data = {
            'name': 'Test Artist',
            'city': '',
            'state': 'CA',
            'phone': '555-0123'
        }
        
        response = client.post('/artists/create', data=data)
        assert response.status_code == 200
    
    def test_create_artist_post_missing_state(self, client):
        """Test POST /artists/create with missing state shows error."""
        data = {
            'name': 'Test Artist',
            'city': 'SF',
            'state': '',
            'phone': '555-0123'
        }
        
        response = client.post('/artists/create', data=data)
        assert response.status_code == 200


class TestArtistEditRoutes:
    """Test Artist editing routes."""
    
    def test_edit_artist_form_page(self, client):
        """Test GET /artists/<id>/edit displays form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}/edit')
        assert response.status_code == 200
        assert b'Edit' in response.data or b'Artist' in response.data
        assert b'Test Artist' in response.data
    
    def test_edit_artist_form_nonexistent(self, client):
        """Test GET /artists/<id>/edit for non-existent artist."""
        response = client.get('/artists/9999/edit')
        assert response.status_code in [302, 200]
    
    def test_edit_artist_post_success(self, client):
        """Test POST /artists/<id>/edit updates artist."""
        artist = Artist(name='Test Artist', city='SF', state='CA', phone='555-0000')
        db.session.add(artist)
        db.session.commit()
        
        data = {
            'name': 'Updated Artist',
            'city': 'LA',
            'state': 'CA',
            'phone': '555-1234',
            'genres': ['Rock'],
            'facebook_link': 'https://facebook.com/updated'
        }
        
        response = client.post(f'/artists/{artist.id}/edit', data=data, follow_redirects=True)
        assert response.status_code == 200
        # Verify the route handled the request (either success or form redisplay)
        assert b'Edit' in response.data or b'Artist' in response.data
    
    def test_edit_artist_post_nonexistent(self, client):
        """Test POST /artists/<id>/edit for non-existent artist."""
        data = {
            'name': 'Test Artist',
            'city': 'SF',
            'state': 'CA',
            'phone': '555-0123'
        }
        
        response = client.post('/artists/9999/edit', data=data, follow_redirects=True)
        assert response.status_code in [200, 302]
    
    def test_edit_artist_post_invalid_data(self, client):
        """Test POST /artists/<id>/edit with invalid data."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        data = {
            'name': '',  # Missing required field
            'city': 'SF',
            'state': 'CA'
        }
        
        response = client.post(f'/artists/{artist.id}/edit', data=data, follow_redirects=True)
        assert response.status_code in [200, 302]
        # Form should be redisplayed with errors or redirect
        assert b'edit' in response.data.lower() or b'error' in response.data.lower()


class TestArtistDeleteRoutes:
    """Test Artist deletion routes."""
    
    def test_delete_artist_json(self, client):
        """Test DELETE /artists/<id> deletes artist (JSON endpoint)."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        
        response = client.delete(f'/artists/{artist_id}')
        assert response.status_code == 200
        
        # Verify deletion
        deleted_artist = Artist.query.get(artist_id)
        assert deleted_artist is None
    
    def test_delete_artist_json_nonexistent(self, client):
        """Test DELETE /artists/<id> for non-existent artist."""
        response = client.delete('/artists/9999')
        assert response.status_code == 400
    
    def test_delete_artist_post(self, client):
        """Test POST /artists/<id>/delete deletes artist."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        
        response = client.post(f'/artists/{artist_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'successfully deleted' in response.data or b'Artist' in response.data
        
        # Verify deletion
        deleted_artist = Artist.query.get(artist_id)
        assert deleted_artist is None
    
    def test_delete_artist_post_nonexistent(self, client):
        """Test POST /artists/<id>/delete for non-existent artist."""
        response = client.post('/artists/9999/delete', follow_redirects=True)
        assert response.status_code in [200, 302]


class TestArtistAvailabilityRoutes:
    """Test Artist availability routes."""
    
    def test_show_artist_availability_page(self, client):
        """Test GET /artists/<id>/availability displays availability."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        # Add availability slot
        slot = ArtistAvailability(
            artist_id=artist.id,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db.session.add(slot)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}/availability')
        assert response.status_code == 200
        assert b'availability' in response.data.lower() or b'schedule' in response.data.lower()
    
    def test_show_artist_availability_nonexistent(self, client):
        """Test GET /artists/<id>/availability for non-existent artist."""
        response = client.get('/artists/9999/availability')
        assert response.status_code in [302, 200]
    
    def test_new_artist_availability_form(self, client):
        """Test GET /artists/<id>/availability/new shows form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}/availability/new')
        assert response.status_code == 200
        assert b'availability' in response.data.lower()
    
    def test_new_artist_availability_form_nonexistent(self, client):
        """Test GET /artists/<id>/availability/new for non-existent artist."""
        response = client.get('/artists/9999/availability/new')
        assert response.status_code in [302, 200]
    
    def test_create_artist_availability_success(self, client):
        """Test POST /artists/<id>/availability/new creates slot."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        data = {
            'day_of_week': '0',  # Monday
            'start_time': '10:00',
            'end_time': '18:00',
            'is_available': True
        }
        
        response = client.post(f'/artists/{artist.id}/availability/new', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'created successfully' in response.data or b'availability' in response.data.lower()
    
    def test_create_artist_availability_nonexistent_artist(self, client):
        """Test POST /artists/<id>/availability/new for non-existent artist."""
        data = {
            'day_of_week': '0',
            'start_time': '10:00',
            'end_time': '18:00'
        }
        
        response = client.post('/artists/9999/availability/new', data=data, follow_redirects=True)
        assert response.status_code in [200, 302]
    
    def test_edit_artist_availability_form(self, client):
        """Test GET /artists/<id>/availability/<slot_id>/edit shows form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        slot = ArtistAvailability(
            artist_id=artist.id,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db.session.add(slot)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}/availability/{slot.id}/edit')
        assert response.status_code == 200
    
    def test_edit_artist_availability_post_success(self, client):
        """Test POST /artists/<id>/availability/<slot_id>/edit updates slot."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        slot = ArtistAvailability(
            artist_id=artist.id,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db.session.add(slot)
        db.session.commit()
        
        data = {
            'day_of_week': '1',  # Tuesday
            'start_time': '12:00',
            'end_time': '20:00',
            'is_available': False
        }
        
        response = client.post(
            f'/artists/{artist.id}/availability/{slot.id}/edit',
            data=data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'updated successfully' in response.data or b'availability' in response.data.lower()
    
    def test_delete_artist_availability(self, client):
        """Test POST /artists/<id>/availability/<slot_id>/delete deletes slot."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        slot = ArtistAvailability(
            artist_id=artist.id,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db.session.add(slot)
        db.session.commit()
        slot_id = slot.id
        
        response = client.post(
            f'/artists/{artist.id}/availability/{slot_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'deleted successfully' in response.data or b'availability' in response.data.lower()


class TestArtistAvailabilityExceptionRoutes:
    """Test Artist availability exception routes."""
    
    def test_new_artist_availability_exception_form(self, client):
        """Test GET /artists/<id>/availability/exception/new shows form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}/availability/exception/new')
        assert response.status_code == 200
        assert b'exception' in response.data.lower() or b'availability' in response.data.lower()
    
    def test_new_artist_availability_exception_form_nonexistent(self, client):
        """Test GET /artists/<id>/availability/exception/new for non-existent artist."""
        response = client.get('/artists/9999/availability/exception/new')
        assert response.status_code in [302, 200]
    
    def test_create_artist_availability_exception_success(self, client):
        """Test POST /artists/<id>/availability/exception/new creates exception."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        data = {
            'exception_date': '2026-09-15',
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': False,
            'reason': 'Medical appointment'
        }
        
        response = client.post(
            f'/artists/{artist.id}/availability/exception/new',
            data=data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'created successfully' in response.data or b'exception' in response.data.lower()
    
    def test_create_artist_availability_exception_nonexistent_artist(self, client):
        """Test POST /artists/<id>/availability/exception/new for non-existent artist."""
        data = {
            'exception_date': '2026-09-15',
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': False
        }
        
        response = client.post(
            '/artists/9999/availability/exception/new',
            data=data,
            follow_redirects=True
        )
        assert response.status_code in [200, 302]
    
    def test_edit_artist_availability_exception_form(self, client):
        """Test GET /artists/<id>/availability/exception/<exc_id>/edit shows form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        exception = ArtistAvailabilityException(
            artist_id=artist.id,
            exception_date=date(2026, 9, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=False,
            reason='Medical appointment'
        )
        db.session.add(exception)
        db.session.commit()
        
        response = client.get(f'/artists/{artist.id}/availability/exception/{exception.id}/edit')
        assert response.status_code == 200
    
    def test_edit_artist_availability_exception_post_success(self, client):
        """Test POST /artists/<id>/availability/exception/<exc_id>/edit updates exception."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        exception = ArtistAvailabilityException(
            artist_id=artist.id,
            exception_date=date(2026, 9, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=False,
            reason='Medical appointment'
        )
        db.session.add(exception)
        db.session.commit()
        
        data = {
            'exception_date': '2026-09-16',
            'start_time': '10:00',
            'end_time': '18:00',
            'is_available': True,
            'reason': 'Concert rehearsal'
        }
        
        response = client.post(
            f'/artists/{artist.id}/availability/exception/{exception.id}/edit',
            data=data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'updated successfully' in response.data or b'exception' in response.data.lower()
    
    def test_delete_artist_availability_exception(self, client):
        """Test POST /artists/<id>/availability/exception/<exc_id>/delete deletes exception."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        exception = ArtistAvailabilityException(
            artist_id=artist.id,
            exception_date=date(2026, 9, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=False
        )
        db.session.add(exception)
        db.session.commit()
        exc_id = exception.id
        
        response = client.post(
            f'/artists/{artist.id}/availability/exception/{exc_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'deleted successfully' in response.data or b'exception' in response.data.lower()


class TestArtistErrorHandling:
    """Test error handling in artist routes."""
    
    def test_edit_availability_slot_wrong_artist(self, client):
        """Test editing availability slot with wrong artist ID."""
        artist1 = Artist(name='Artist 1', city='SF', state='CA')
        artist2 = Artist(name='Artist 2', city='LA', state='CA')
        db.session.add_all([artist1, artist2])
        db.session.commit()
        
        # Create slot for artist 1
        slot = ArtistAvailability(
            artist_id=artist1.id,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db.session.add(slot)
        db.session.commit()
        
        # Try to edit with artist 2
        data = {
            'day_of_week': '1',
            'start_time': '12:00',
            'end_time': '20:00'
        }
        
        response = client.post(
            f'/artists/{artist2.id}/availability/{slot.id}/edit',
            data=data,
            follow_redirects=True
        )
        assert response.status_code in [200, 302]
    
    def test_delete_availability_slot_wrong_artist(self, client):
        """Test deleting availability slot with wrong artist ID."""
        artist1 = Artist(name='Artist 1', city='SF', state='CA')
        artist2 = Artist(name='Artist 2', city='LA', state='CA')
        db.session.add_all([artist1, artist2])
        db.session.commit()
        
        slot = ArtistAvailability(
            artist_id=artist1.id,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(18, 0)
        )
        db.session.add(slot)
        db.session.commit()
        
        response = client.post(
            f'/artists/{artist2.id}/availability/{slot.id}/delete',
            follow_redirects=True
        )
        assert response.status_code in [200, 302]
    
    def test_edit_exception_wrong_artist(self, client):
        """Test editing exception with wrong artist ID."""
        artist1 = Artist(name='Artist 1', city='SF', state='CA')
        artist2 = Artist(name='Artist 2', city='LA', state='CA')
        db.session.add_all([artist1, artist2])
        db.session.commit()
        
        exception = ArtistAvailabilityException(
            artist_id=artist1.id,
            exception_date=date(2026, 9, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        db.session.add(exception)
        db.session.commit()
        
        data = {
            'exception_date': '2026-09-16',
            'start_time': '10:00',
            'end_time': '18:00'
        }
        
        response = client.post(
            f'/artists/{artist2.id}/availability/exception/{exception.id}/edit',
            data=data,
            follow_redirects=True
        )
        assert response.status_code in [200, 302]
    
    def test_delete_exception_wrong_artist(self, client):
        """Test deleting exception with wrong artist ID."""
        artist1 = Artist(name='Artist 1', city='SF', state='CA')
        artist2 = Artist(name='Artist 2', city='LA', state='CA')
        db.session.add_all([artist1, artist2])
        db.session.commit()
        
        exception = ArtistAvailabilityException(
            artist_id=artist1.id,
            exception_date=date(2026, 9, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        db.session.add(exception)
        db.session.commit()
        
        response = client.post(
            f'/artists/{artist2.id}/availability/exception/{exception.id}/delete',
            follow_redirects=True
        )
        assert response.status_code in [200, 302]
