"""Unit tests for Album and Song services."""

import pytest
from datetime import date
from dal import db, Album, Song, Artist
from dto.album import AlbumDTO, SongDTO
from services.album import AlbumService
from services.song import SongService


class TestAlbumService:
    """Test Album service CRUD operations and validation."""
    
    def test_get_all_albums_empty(self, client):
        """Test getting all albums when none exist."""
        albums = AlbumService.get_all_albums()
        assert albums == []
    
    def test_get_all_albums_returns_all(self, client):
        """Test getting all albums returns complete list."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album1 = Album(artist_id=artist.id, title='Album 1', release_date=date(2024, 1, 1))
        album2 = Album(artist_id=artist.id, title='Album 2', release_date=date(2024, 6, 1))
        db.session.add_all([album1, album2])
        db.session.commit()
        
        albums = AlbumService.get_all_albums()
        assert len(albums) == 2
    
    def test_get_albums_by_artist(self, client):
        """Test getting albums for a specific artist."""
        artist1 = Artist(name='Artist 1', city='SF', state='CA')
        artist2 = Artist(name='Artist 2', city='NYC', state='NY')
        db.session.add_all([artist1, artist2])
        db.session.commit()
        
        album1 = Album(artist_id=artist1.id, title='Album 1')
        album2 = Album(artist_id=artist1.id, title='Album 2')
        album3 = Album(artist_id=artist2.id, title='Album 3')
        db.session.add_all([album1, album2, album3])
        db.session.commit()
        
        albums = AlbumService.get_albums_by_artist(artist1.id)
        assert len(albums) == 2
        assert all(a.artist_id == artist1.id for a in albums)
    
    def test_get_albums_by_artist_nonexistent(self, client):
        """Test getting albums for non-existent artist."""
        albums = AlbumService.get_albums_by_artist(9999)
        assert albums == []
    
    def test_get_album_by_id(self, client):
        """Test getting a single album by ID."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album', description='Test Description')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        result = AlbumService.get_album_by_id(album_id)
        assert result is not None
        assert result.title == 'Test Album'
        assert result.description == 'Test Description'
    
    def test_get_album_by_id_nonexistent(self, client):
        """Test getting non-existent album."""
        result = AlbumService.get_album_by_id(9999)
        assert result is None
    
    def test_create_album_success(self, client):
        """Test creating a new album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        
        album_dto = AlbumDTO(
            artist_id=artist_id,
            title='New Album',
            release_date=date(2024, 1, 1),
            description='Test album'
        )
        
        success, error = AlbumService.create_album(album_dto)
        assert success is True
        assert error is None
        
        # Verify album was created
        album = Album.query.filter_by(title='New Album').first()
        assert album is not None
        assert album.artist_id == artist_id
    
    def test_create_album_invalid_artist(self, client):
        """Test creating album with non-existent artist."""
        album_dto = AlbumDTO(
            artist_id=9999,
            title='New Album'
        )
        
        success, error = AlbumService.create_album(album_dto)
        assert success is False
        assert 'not found' in error.lower()
    
    def test_update_album(self, client):
        """Test updating an album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Original Title')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        album_dto = AlbumDTO(
            id=album_id,
            artist_id=artist.id,
            title='Updated Title',
            description='Updated description'
        )
        
        success, error = AlbumService.update_album(album_id, album_dto)
        assert success is True
        
        # Verify album was updated
        db.session.refresh(album)
        assert album.title == 'Updated Title'
        assert album.description == 'Updated description'
    
    def test_update_album_nonexistent(self, client):
        """Test updating non-existent album."""
        album_dto = AlbumDTO(title='New Title')
        success, error = AlbumService.update_album(9999, album_dto)
        assert success is False
    
    def test_delete_album(self, client):
        """Test deleting an album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Delete Me')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        success, error = AlbumService.delete_album(album_id)
        assert success is True
        
        # Verify album was deleted
        album = Album.query.get(album_id)
        assert album is None
    
    def test_delete_album_nonexistent(self, client):
        """Test deleting non-existent album."""
        success, error = AlbumService.delete_album(9999)
        assert success is False
    
    def test_validate_album_form_data_valid(self, client):
        """Test validating valid album form data."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        
        form_data = {
            'title': 'Test Album',
            'artist_id': str(artist_id),
            'release_date': '2024-01-15',
            'description': 'Test description',
            'image_link': 'https://example.com/image.jpg',
            'spotify_link': 'https://open.spotify.com/album/12345'
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert errors == {}
        assert album_dto is not None
        assert album_dto.title == 'Test Album'
        assert album_dto.artist_id == artist_id
    
    def test_validate_album_form_data_missing_title(self, client):
        """Test validation fails without title."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        
        form_data = {
            'title': '',
            'artist_id': str(artist_id)
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'title' in errors
        assert album_dto is None
    
    def test_validate_album_form_data_invalid_artist(self, client):
        """Test validation fails with invalid artist."""
        form_data = {
            'title': 'Test Album',
            'artist_id': '9999'
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'artist_id' in errors
    
    def test_validate_album_form_data_invalid_date(self, client):
        """Test validation fails with invalid date."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
        
        form_data = {
            'title': 'Test Album',
            'artist_id': str(artist_id),
            'release_date': 'invalid-date'
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'release_date' in errors


class TestSongService:
    """Test Song service CRUD operations and validation."""
    
    def test_get_songs_by_album_empty(self, client):
        """Test getting songs from empty album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Empty Album')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        songs = SongService.get_songs_by_album(album_id)
        assert songs == []
    
    def test_get_songs_by_album(self, client):
        """Test getting songs from album."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song1 = Song(album_id=album.id, title='Song 1', track_number=1)
        song2 = Song(album_id=album.id, title='Song 2', track_number=2)
        db.session.add_all([song1, song2])
        db.session.commit()
        album_id = album.id
        
        songs = SongService.get_songs_by_album(album_id)
        assert len(songs) == 2
        # Should be sorted by track number
        assert songs[0].title == 'Song 1'
        assert songs[1].title == 'Song 2'
    
    def test_get_song_by_id(self, client):
        """Test getting a single song by ID."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Test Song', duration=180, genre='Rock')
        db.session.add(song)
        db.session.commit()
        song_id = song.id
        
        result = SongService.get_song_by_id(song_id)
        assert result is not None
        assert result.title == 'Test Song'
        assert result.duration == 180
        assert result.genre == 'Rock'
    
    def test_get_song_by_id_nonexistent(self, client):
        """Test getting non-existent song."""
        result = SongService.get_song_by_id(9999)
        assert result is None
    
    def test_create_song_success(self, client):
        """Test creating a new song."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        song_dto = SongDTO(
            album_id=album_id,
            title='New Song',
            duration=240,
            track_number=1,
            genre='Rock'
        )
        
        success, error = SongService.create_song(song_dto)
        assert success is True
        assert error is None
        
        # Verify song was created
        song = Song.query.filter_by(title='New Song').first()
        assert song is not None
        assert song.album_id == album_id
    
    def test_create_song_invalid_album(self, client):
        """Test creating song with non-existent album."""
        song_dto = SongDTO(
            album_id=9999,
            title='New Song'
        )
        
        success, error = SongService.create_song(song_dto)
        assert success is False
        assert 'not found' in error.lower()
    
    def test_update_song(self, client):
        """Test updating a song."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Original Title', duration=180)
        db.session.add(song)
        db.session.commit()
        song_id = song.id
        
        song_dto = SongDTO(
            id=song_id,
            album_id=album.id,
            title='Updated Title',
            duration=240,
            genre='Rock'
        )
        
        success, error = SongService.update_song(song_id, song_dto)
        assert success is True
        
        # Verify song was updated
        db.session.refresh(song)
        assert song.title == 'Updated Title'
        assert song.duration == 240
    
    def test_update_song_nonexistent(self, client):
        """Test updating non-existent song."""
        song_dto = SongDTO(title='New Title')
        success, error = SongService.update_song(9999, song_dto)
        assert success is False
    
    def test_delete_song(self, client):
        """Test deleting a song."""
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
        
        success, error = SongService.delete_song(song_id)
        assert success is True
        
        # Verify song was deleted
        song = Song.query.get(song_id)
        assert song is None
    
    def test_delete_song_nonexistent(self, client):
        """Test deleting non-existent song."""
        success, error = SongService.delete_song(9999)
        assert success is False
    
    def test_validate_song_form_data_valid(self, client):
        """Test validating valid song form data."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        album_id = album.id
        
        form_data = {
            'title': 'Test Song',
            'track_number': '1',
            'duration': '240',
            'genre': 'Rock',
            'spotify_link': 'https://open.spotify.com/track/12345'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, album_id)
        assert errors == {}
        assert song_dto is not None
        assert song_dto.title == 'Test Song'
        assert song_dto.duration == 240
    
    def test_validate_song_form_data_missing_title(self, client):
        """Test validation fails without title."""
        form_data = {'title': ''}
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert 'title' in errors
        assert song_dto is None
    
    def test_validate_song_form_data_invalid_duration(self, client):
        """Test validation fails with invalid duration."""
        form_data = {
            'title': 'Test Song',
            'duration': 'not-a-number'
        }
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert 'duration' in errors
    
    def test_song_dto_format_duration(self, client):
        """Test SongDTO duration formatting."""
        song = SongDTO(title='Test', duration=180)  # 3 minutes
        assert song.format_duration() == '3:00'
        
        song2 = SongDTO(title='Test', duration=245)  # 4:05
        assert song2.format_duration() == '4:05'
    
    def test_album_dto_song_count(self, client):
        """Test AlbumDTO song count."""
        songs = [
            SongDTO(title='Song 1'),
            SongDTO(title='Song 2'),
            SongDTO(title='Song 3')
        ]
        album = AlbumDTO(title='Test', songs=songs)
        assert album.song_count() == 3
    
    def test_album_dto_total_duration(self, client):
        """Test AlbumDTO total duration calculation."""
        songs = [
            SongDTO(title='Song 1', duration=180),
            SongDTO(title='Song 2', duration=240),
            SongDTO(title='Song 3', duration=120)
        ]
        album = AlbumDTO(title='Test', songs=songs)
        assert album.total_duration() == 540
        assert album.format_total_duration() == '9:00'
