"""Integration tests for Album and Song controller routes."""

import pytest
from datetime import date
from dal import db, Album, Song, Artist
from flask import url_for


class TestAlbumControllerRoutes:
    """Test Album controller routes."""
    
    def test_albums_list_page(self, client):
        """Test GET /albums/ displays album list."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album', release_date=date(2024, 1, 1))
        db.session.add(album)
        db.session.commit()
        
        response = client.get('/albums/')
        assert response.status_code == 200
        assert b'Test Album' in response.data
        assert b'Add Album' in response.data
    
    def test_albums_list_empty(self, client):
        """Test GET /albums/ with no albums."""
        response = client.get('/albums/')
        assert response.status_code == 200
        assert b'Albums' in response.data
    
    def test_album_detail_page(self, client):
        """Test GET /albums/<id> shows album detail."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album', description='Test Desc')
        db.session.add(album)
        db.session.commit()
        
        response = client.get(f'/albums/{album.id}')
        assert response.status_code == 200
        assert b'Test Album' in response.data
        assert b'Test Desc' in response.data
    
    def test_album_detail_nonexistent(self, client):
        """Test GET /albums/<id> for non-existent album."""
        response = client.get('/albums/9999')
        # Should redirect or show an error flash
        assert response.status_code in [302, 200]
    
    def test_create_album_form_page(self, client):
        """Test GET /albums/create displays form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.get('/albums/create')
        assert response.status_code == 200
        assert b'Create Album' in response.data or b'Album' in response.data
    
    def test_create_album_form_with_artist_prefill(self, client):
        """Test GET /albums/create?artist_id=X prefills artist."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        response = client.get(f'/albums/create?artist_id={artist.id}')
        assert response.status_code == 200
    
    def test_create_album_post_success(self, client):
        """Test POST /albums/create creates album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        data = {
            'title': 'New Album',
            'artist_id': str(artist.id),
            'release_date': '2024-01-15',
            'description': 'Test album'
        }
        
        response = client.post('/albums/create', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'New Album' in response.data
        
        # Verify album was created
        album = Album.query.filter_by(title='New Album').first()
        assert album is not None
    
    def test_create_album_post_missing_title(self, client):
        """Test POST /albums/create with missing title."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        data = {
            'title': '',
            'artist_id': str(artist.id)
        }
        
        response = client.post('/albums/create', data=data)
        assert response.status_code == 200
    
    def test_edit_album_form_page(self, client):
        """Test GET /albums/<id>/edit displays form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        response = client.get(f'/albums/{album.id}/edit')
        assert response.status_code == 200
        assert b'Test Album' in response.data
    
    def test_edit_album_form_nonexistent(self, client):
        """Test GET /albums/<id>/edit for non-existent album."""
        response = client.get('/albums/9999/edit')
        # Should redirect or show an error flash
        assert response.status_code in [302, 200]
    
    def test_edit_album_post_success(self, client):
        """Test POST /albums/<id>/edit updates album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Original Title')
        db.session.add(album)
        db.session.commit()
        
        data = {
            'title': 'Updated Title',
            'artist_id': str(artist.id),
            'description': 'Updated description'
        }
        
        response = client.post(f'/albums/{album.id}/edit', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Updated Title' in response.data
        
        # Verify album was updated
        db.session.refresh(album)
        assert album.title == 'Updated Title'
    
    def test_delete_album_post(self, client):
        """Test POST /albums/<id>/delete removes album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Delete Me')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        response = client.post(f'/albums/{album_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify album was deleted
        album = Album.query.get(album_id)
        assert album is None
    
    def test_delete_album_json(self, client):
        """Test DELETE /albums/<id> (JSON) removes album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Delete Me')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        response = client.delete(f'/albums/{album_id}')
        assert response.status_code in [200, 204, 302]
        
        # Verify album was deleted
        album = Album.query.get(album_id)
        assert album is None


class TestSongControllerRoutes:
    """Test Song controller routes."""
    
    def test_create_song_form_page(self, client):
        """Test GET /songs/create displays form with album context."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        response = client.get(f'/songs/create?album_id={album.id}')
        assert response.status_code == 200
    
    def test_create_song_form_no_album_id(self, client):
        """Test GET /songs/create without album_id redirects."""
        response = client.get('/songs/create', follow_redirects=True)
        assert response.status_code == 200
    
    def test_create_song_post_success(self, client):
        """Test POST /songs/create creates song."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        data = {
            'album_id': str(album.id),
            'title': 'New Song',
            'track_number': '1',
            'duration': '240',
            'genre': 'Rock'
        }
        
        response = client.post('/songs/create', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'New Song' in response.data
        
        # Verify song was created
        song = Song.query.filter_by(title='New Song').first()
        assert song is not None
    
    def test_create_song_post_missing_title(self, client):
        """Test POST /songs/create with missing title."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        data = {
            'album_id': str(album.id),
            'title': '',
            'track_number': '1'
        }
        
        response = client.post('/songs/create', data=data)
        assert response.status_code == 200
    
    def test_edit_song_form_page(self, client):
        """Test GET /songs/<id>/edit displays form."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Test Song')
        db.session.add(song)
        db.session.commit()
        
        response = client.get(f'/songs/{song.id}/edit')
        assert response.status_code == 200
        assert b'Test Song' in response.data
    
    def test_edit_song_form_nonexistent(self, client):
        """Test GET /songs/<id>/edit for non-existent song."""
        response = client.get('/songs/9999/edit')
        # Should redirect or show an error flash
        assert response.status_code in [302, 200]
    
    def test_edit_song_post_success(self, client):
        """Test POST /songs/<id>/edit updates song."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Original Title', duration=180)
        db.session.add(song)
        db.session.commit()
        
        data = {
            'title': 'Updated Title',
            'duration': '240',
            'genre': 'Rock'
        }
        
        response = client.post(f'/songs/{song.id}/edit', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Updated Title' in response.data
        
        # Verify song was updated
        db.session.refresh(song)
        assert song.title == 'Updated Title'
    
    def test_delete_song_post(self, client):
        """Test POST /songs/<id>/delete removes song."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Delete Me')
        db.session.add(song)
        db.session.commit()
        song_id = song.id
        
        response = client.post(f'/songs/{song_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify song was deleted
        song = Song.query.get(song_id)
        assert song is None
    
    def test_delete_song_json(self, client):
        """Test DELETE /songs/<id> (JSON) removes song."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Delete Me')
        db.session.add(song)
        db.session.commit()
        song_id = song.id
        
        response = client.delete(f'/songs/{song_id}')
        assert response.status_code in [200, 204, 302]
        
        # Verify song was deleted
        song = Song.query.get(song_id)
        assert song is None
