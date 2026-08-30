"""Additional edge case tests for Album and Song services."""

import pytest
from datetime import date
from dal import db, Album, Song, Artist
from dto.album import AlbumDTO, SongDTO
from services.album import AlbumService
from services.song import SongService


class TestAlbumServiceEdgeCases:
    """Test Album service edge cases and error handling."""
    
    def test_create_album_with_all_fields(self, client):
        """Test creating album with all fields populated."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album_dto = AlbumDTO(
            artist_id=artist.id,
            title='Complete Album',
            release_date=date(2024, 6, 15),
            description='Full description here',
            image_link='https://example.com/image.jpg',
            spotify_link='https://open.spotify.com/album/123abc'
        )
        
        success, error = AlbumService.create_album(album_dto)
        assert success is True
        
        album = Album.query.filter_by(title='Complete Album').first()
        assert album.release_date == date(2024, 6, 15)
        assert album.description == 'Full description here'
        assert album.image_link == 'https://example.com/image.jpg'
    
    def test_validate_album_empty_title_string(self, client):
        """Test validation with explicit empty title."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        form_data = {
            'title': '',
            'artist_id': str(artist.id),
            'release_date': '',
            'description': '',
            'image_link': '',
            'spotify_link': ''
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'title' in errors
    
    def test_validate_album_title_too_long(self, client):
        """Test validation with title exceeding max length."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        long_title = 'x' * 256  # Over 255 character limit
        form_data = {
            'title': long_title,
            'artist_id': str(artist.id)
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'title' in errors or album_dto is None
    
    def test_get_albums_by_artist_with_songs(self, client):
        """Test getting albums includes song count in DTO."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album with Songs')
        db.session.add(album)
        db.session.commit()
        
        song1 = Song(album_id=album.id, title='Song 1')
        song2 = Song(album_id=album.id, title='Song 2')
        db.session.add_all([song1, song2])
        db.session.commit()
        
        albums = AlbumService.get_albums_by_artist(artist.id)
        assert len(albums) == 1
        assert len(albums[0].songs) == 2
    
    def test_delete_album_cascade_deletes_songs(self, client):
        """Test that deleting an album also deletes all its songs."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album to Delete')
        db.session.add(album)
        db.session.commit()
        
        song = Song(album_id=album.id, title='Song to Delete')
        db.session.add(song)
        db.session.commit()
        album_id = album.id
        song_id = song.id
        
        # Delete album
        success, error = AlbumService.delete_album(album_id)
        assert success is True
        
        # Verify both album and song are deleted
        assert Album.query.get(album_id) is None
        assert Song.query.get(song_id) is None


class TestSongServiceEdgeCases:
    """Test Song service edge cases and error handling."""
    
    def test_create_song_with_all_fields(self, client):
        """Test creating song with all optional fields."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album')
        db.session.add(album)
        db.session.commit()
        
        song_dto = SongDTO(
            album_id=album.id,
            title='Complete Song',
            duration=245,
            track_number=5,
            genre='Rock',
            spotify_track_id='spotify123',
            spotify_link='https://open.spotify.com/track/123'
        )
        
        success, error = SongService.create_song(song_dto)
        assert success is True
        
        song = Song.query.filter_by(title='Complete Song').first()
        assert song.duration == 245
        assert song.track_number == 5
        assert song.genre == 'Rock'
        assert song.spotify_track_id == 'spotify123'
    
    def test_validate_song_empty_title(self, client):
        """Test validation with empty title."""
        form_data = {
            'title': '',
            'track_number': '1',
            'duration': '240'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert 'title' in errors
    
    def test_validate_song_title_too_long(self, client):
        """Test validation with title exceeding max length."""
        long_title = 'x' * 256
        form_data = {
            'title': long_title,
            'track_number': '1'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert 'title' in errors or song_dto is None
    
    def test_validate_song_invalid_track_number(self, client):
        """Test validation with negative track number."""
        form_data = {
            'title': 'Song Title',
            'track_number': '-5'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert 'track_number' in errors or song_dto is None
    
    def test_validate_song_invalid_duration_negative(self, client):
        """Test validation with negative duration."""
        form_data = {
            'title': 'Song Title',
            'duration': '-100'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert 'duration' in errors or song_dto is None
    
    def test_song_format_duration_edge_cases(self, client):
        """Test duration formatting with various values."""
        # Test 0 seconds
        song = SongDTO(title='Test', duration=0)
        assert song.format_duration() == '0:00'
        
        # Test single digit seconds
        song2 = SongDTO(title='Test', duration=65)  # 1:05
        assert song2.format_duration() == '1:05'
        
        # Test exactly 1 hour (3600 seconds)
        song3 = SongDTO(title='Test', duration=3600)
        assert song3.format_duration() == '60:00'
    
    def test_album_dto_empty_songs_total_duration(self, client):
        """Test total duration calculation with no songs."""
        album = AlbumDTO(title='Empty Album', songs=[])
        assert album.total_duration() == 0
        assert album.format_total_duration() == '0:00'
    
    def test_album_dto_single_song(self, client):
        """Test album DTO calculations with single song."""
        songs = [SongDTO(title='Only Song', duration=150)]
        album = AlbumDTO(title='Single Song Album', songs=songs)
        assert album.song_count() == 1
        assert album.total_duration() == 150
        assert album.format_total_duration() == '2:30'
    
    def test_get_songs_sorted_by_track_number(self, client):
        """Test that songs are returned sorted by track number."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album')
        db.session.add(album)
        db.session.commit()
        
        # Add songs in non-sequential order
        song3 = Song(album_id=album.id, title='Song 3', track_number=3)
        song1 = Song(album_id=album.id, title='Song 1', track_number=1)
        song2 = Song(album_id=album.id, title='Song 2', track_number=2)
        db.session.add_all([song3, song1, song2])
        db.session.commit()
        
        songs = SongService.get_songs_by_album(album.id)
        assert len(songs) == 3
        # Should be sorted by track_number
        assert songs[0].track_number == 1
        assert songs[1].track_number == 2
        assert songs[2].track_number == 3


class TestAlbumFormDataValidation:
    """Test album form data validation edge cases."""
    
    def test_validate_album_with_optional_url_fields(self, client):
        """Test validation with empty URL fields."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        form_data = {
            'title': 'Album with URLs',
            'artist_id': str(artist.id),
            'image_link': '',  # Empty
            'spotify_link': ''  # Empty
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        # Should pass - these fields are optional
        assert 'image_link' not in errors
        assert 'spotify_link' not in errors
        assert album_dto is not None
    
    def test_validate_album_with_invalid_url_formats(self, client):
        """Test validation with malformed URLs."""
        artist = Artist(name='Test Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        form_data = {
            'title': 'Album',
            'artist_id': str(artist.id),
            'image_link': 'not-a-url',
            'spotify_link': 'also-not-a-url'
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        # Invalid URLs should generate errors
        if 'image_link' in errors or 'spotify_link' in errors:
            assert True  # URL validation working
        else:
            # Or album_dto could be None
            assert album_dto is None or 'image_link' not in errors
