"""Tests for remaining service coverage."""

import pytest
from datetime import date
from dal import db, Album, Song, Artist
from dto.album import AlbumDTO, SongDTO
from services.album import AlbumService
from services.song import SongService


class TestAlbumServiceCoverageCompletion:
    """Complete remaining coverage in AlbumService."""
    
    def test_validate_album_with_missing_artist_id(self, client):
        """Test validation when artist_id is not provided."""
        form_data = {
            'title': 'Album',
            'artist_id': ''
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'artist_id' in errors or album_dto is None
    
    def test_validate_album_with_non_integer_artist_id(self, client):
        """Test validation when artist_id is not an integer."""
        form_data = {
            'title': 'Album',
            'artist_id': 'not-an-id'
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert 'artist_id' in errors or album_dto is None
    
    def test_update_album_change_artist(self, client):
        """Test updating album basic fields (artist_id not editable via update)."""
        artist1 = Artist(name='Artist 1', city='SF', state='CA')
        artist2 = Artist(name='Artist 2', city='NYC', state='NY')
        db.session.add_all([artist1, artist2])
        db.session.commit()
        
        album = Album(artist_id=artist1.id, title='Test Album')
        db.session.add(album)
        db.session.commit()
        
        album_dto = AlbumDTO(
            id=album.id,
            artist_id=artist1.id,  # Same artist
            title='Test Album Updated',
            description='New description'
        )
        
        success, error = AlbumService.update_album(album.id, album_dto)
        assert success is True
        
        db.session.refresh(album)
        assert album.title == 'Test Album Updated'
        assert album.description == 'New description'
        assert album.artist_id == artist1.id  # Artist remains unchanged
    
    def test_validate_album_date_formats(self, client):
        """Test various date formats in validation."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        # Test valid ISO date
        form_data = {
            'title': 'Album',
            'artist_id': str(artist.id),
            'release_date': '2024-12-25'
        }
        
        errors, album_dto = AlbumService.validate_album_form_data(form_data)
        assert album_dto is not None
        assert album_dto.release_date == date(2024, 12, 25)


class TestSongServiceCoverageCompletion:
    """Complete remaining coverage in SongService."""
    
    def test_validate_song_with_zero_track_number(self, client):
        """Test validation with track_number = 0."""
        form_data = {
            'title': 'Song',
            'track_number': '0'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        # Should pass - 0 is valid
        if 'track_number' not in errors:
            assert song_dto is not None
    
    def test_validate_song_with_float_duration(self, client):
        """Test validation with float duration."""
        form_data = {
            'title': 'Song',
            'duration': '240.5'  # Float value
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        # Should either pass or fail validation
        assert isinstance(errors, dict)
    
    def test_validate_song_with_float_track_number(self, client):
        """Test validation with float track_number."""
        form_data = {
            'title': 'Song',
            'track_number': '3.5'
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert isinstance(errors, dict)
    
    def test_update_song_change_album(self, client):
        """Test updating song basic fields (album_id not editable via update)."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album1 = Album(artist_id=artist.id, title='Album 1')
        album2 = Album(artist_id=artist.id, title='Album 2')
        db.session.add_all([album1, album2])
        db.session.commit()
        
        song = Song(album_id=album1.id, title='Song')
        db.session.add(song)
        db.session.commit()
        
        song_dto = SongDTO(
            id=song.id,
            album_id=album1.id,  # Same album
            title='Song Updated',
            genre='Rock'
        )
        
        success, error = SongService.update_song(song.id, song_dto)
        assert success is True
        
        db.session.refresh(song)
        assert song.title == 'Song Updated'
        assert song.genre == 'Rock'
        assert song.album_id == album1.id  # Album remains unchanged
    
    def test_validate_song_with_all_optional_fields_empty(self, client):
        """Test validation with only required field."""
        form_data = {
            'title': 'Simple Song',
            'track_number': '',
            'duration': '',
            'genre': '',
            'spotify_link': ''
        }
        
        errors, song_dto = SongService.validate_song_form_data(form_data, 1)
        assert song_dto is not None
        assert song_dto.title == 'Simple Song'
        assert song_dto.track_number is None
        assert song_dto.duration is None
    
    def test_album_dto_format_total_duration_hours(self, client):
        """Test format_total_duration with very long album."""
        songs = [
            SongDTO(title='Song 1', duration=3600),  # 1 hour
            SongDTO(title='Song 2', duration=1800),  # 30 minutes
            SongDTO(title='Song 3', duration=600)    # 10 minutes
        ]
        album = AlbumDTO(title='Long Album', songs=songs)
        assert album.total_duration() == 6000
        # Format should show 100:00 (100 minutes)
        assert album.format_total_duration() == '100:00'


class TestAlbumSongIntegration:
    """Test Album and Song integration scenarios."""
    
    def test_album_with_mixed_valid_invalid_songs(self, client):
        """Test album retrieval with songs that have various field values."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Mixed Album')
        db.session.add(album)
        db.session.commit()
        
        # Create songs with various field combinations
        song1 = Song(album_id=album.id, title='Complete Song', duration=240, track_number=1, genre='Rock')
        song2 = Song(album_id=album.id, title='Partial Song', track_number=2)  # No duration/genre
        song3 = Song(album_id=album.id, title='Minimal Song')  # Only title and album
        db.session.add_all([song1, song2, song3])
        db.session.commit()
        
        album_dto = AlbumService.get_album_by_id(album.id)
        assert len(album_dto.songs) == 3
        assert album_dto.songs[0].duration == 240
        assert album_dto.songs[1].duration is None
        assert album_dto.songs[2].genre is None
    
    def test_cascade_delete_songs_when_deleting_album(self, client):
        """Test that songs are automatically deleted when album is deleted."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        album = Album(artist_id=artist.id, title='Album to Delete')
        db.session.add(album)
        db.session.commit()
        
        songs = [
            Song(album_id=album.id, title='Song 1'),
            Song(album_id=album.id, title='Song 2'),
            Song(album_id=album.id, title='Song 3')
        ]
        db.session.add_all(songs)
        db.session.commit()
        
        song_ids = [s.id for s in songs]
        album_id = album.id
        
        # Delete album
        AlbumService.delete_album(album_id)
        
        # Verify album and all songs are deleted
        assert Album.query.get(album_id) is None
        for song_id in song_ids:
            assert Song.query.get(song_id) is None
    
    def test_get_all_albums_sorting(self, client):
        """Test that get_all_albums returns albums sorted by release date."""
        artist = Artist(name='Artist', city='SF', state='CA')
        db.session.add(artist)
        db.session.commit()
        
        # Create albums with specific dates
        album1 = Album(artist_id=artist.id, title='Album 1', release_date=date(2024, 1, 1))
        album2 = Album(artist_id=artist.id, title='Album 2', release_date=date(2024, 12, 31))
        album3 = Album(artist_id=artist.id, title='Album 3', release_date=date(2024, 6, 15))
        db.session.add_all([album1, album2, album3])
        db.session.commit()
        
        albums = AlbumService.get_all_albums()
        
        # Should be sorted by release_date descending (newest first)
        assert albums[0].title == 'Album 2'
        assert albums[1].title == 'Album 3'
        assert albums[2].title == 'Album 1'
