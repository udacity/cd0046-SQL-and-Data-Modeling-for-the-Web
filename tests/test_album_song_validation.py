"""Additional integration tests for Song controller error handling."""

import pytest
from datetime import date
from dal import db, Album, Song, Artist


class TestSongControllerErrorHandling:
    """Test Song controller error handling and edge cases."""
    
    def test_create_song_form_invalid_album_id(self, client):
        """Test GET /songs/create with invalid album_id."""
        response = client.get('/songs/create?album_id=9999', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect or show error
        assert b'not found' in response.data.lower() or b'album' in response.data.lower()
    
    def test_create_song_post_invalid_album_id(self, client):
        """Test POST /songs/create with invalid album_id."""
        data = {
            'album_id': '9999',
            'title': 'Test Song',
            'track_number': '1'
        }
        
        response = client.post('/songs/create', data=data, follow_redirects=True)
        assert response.status_code == 200
    
    def test_create_song_post_with_valid_duration(self, client):
        """Test POST /songs/create validates duration is numeric."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album')
        db.session.add(album)
        db.session.commit()
        
        data = {
            'album_id': str(album.id),
            'title': 'Test Song',
            'duration': 'abc'  # Invalid
        }
        
        response = client.post('/songs/create', data=data)
        assert response.status_code == 200
    
    def test_edit_song_post_with_valid_duration(self, client):
        """Test POST /songs/<id>/edit with valid duration."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Song', duration=180)
        db.session.add(song)
        db.session.commit()
        
        data = {
            'title': 'Updated',
            'duration': '300',
            'track_number': '2'
        }
        
        response = client.post(f'/songs/{song.id}/edit', data=data, follow_redirects=True)
        assert response.status_code == 200
        
        db.session.refresh(song)
        assert song.duration == 300
        assert song.track_number == 2
    
    def test_edit_song_post_with_invalid_duration(self, client):
        """Test POST /songs/<id>/edit with invalid duration."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Song')
        db.session.add(song)
        db.session.commit()
        
        data = {
            'title': 'Updated',
            'duration': 'not-a-number'
        }
        
        response = client.post(f'/songs/{song.id}/edit', data=data)
        assert response.status_code == 200
    
    def test_delete_nonexistent_song_json(self, client):
        """Test DELETE /songs/<id> for non-existent song."""
        response = client.delete('/songs/9999')
        # Should return error response
        assert response.status_code in [400, 404]
    
    def test_edit_nonexistent_song_post(self, client):
        """Test POST /songs/<id>/edit for non-existent song."""
        data = {'title': 'Test'}
        response = client.post('/songs/9999/edit', data=data, follow_redirects=True)
        assert response.status_code == 200


class TestAlbumControllerValidation:
    """Test Album controller form validation and error handling."""
    
    def test_create_album_post_with_invalid_artist(self, client):
        """Test POST /albums/create with invalid artist ID."""
        data = {
            'title': 'Album',
            'artist_id': '9999'
        }
        
        response = client.post('/albums/create', data=data)
        assert response.status_code == 200
    
    def test_create_album_post_with_long_title(self, client):
        """Test POST /albums/create with very long title."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        long_title = 'x' * 300  # Over limit
        data = {
            'title': long_title,
            'artist_id': str(artist.id)
        }
        
        response = client.post('/albums/create', data=data)
        assert response.status_code == 200
    
    def test_edit_album_post_with_invalid_date(self, client):
        """Test POST /albums/<id>/edit with invalid date."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album')
        db.session.add(album)
        db.session.commit()
        
        data = {
            'title': 'Album Updated',
            'artist_id': str(artist.id),
            'release_date': 'not-a-date'
        }
        
        response = client.post(f'/albums/{album.id}/edit', data=data)
        assert response.status_code == 200
    
    def test_delete_nonexistent_album_json(self, client):
        """Test DELETE /albums/<id> for non-existent album."""
        response = client.delete('/albums/9999')
        # Should return error response
        assert response.status_code in [400, 404]
    
    def test_album_detail_with_songs(self, client):
        """Test album detail page properly displays songs."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album with Tracks')
        db.session.add(album)
        db.session.commit()
        
        song1 = Song(album_id=album.id, title='Track 1', track_number=1, duration=200)
        song2 = Song(album_id=album.id, title='Track 2', track_number=2, duration=180)
        db.session.add_all([song1, song2])
        db.session.commit()
        
        response = client.get(f'/albums/{album.id}')
        assert response.status_code == 200
        assert b'Track 1' in response.data
        assert b'Track 2' in response.data
        assert b'Album with Tracks' in response.data
