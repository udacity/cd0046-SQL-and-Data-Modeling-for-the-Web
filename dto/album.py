"""Data Transfer Objects for Album and Song."""

from typing import List, Optional
from datetime import date, datetime


class SongDTO:
    """Data Transfer Object for Song.
    
    Represents song data in a format suitable for service/controller layers.
    """
    
    def __init__(self, id: Optional[int] = None, title: str = '', duration: Optional[int] = None,
                 track_number: Optional[int] = None, genre: str = '', 
                 spotify_track_id: str = '', spotify_link: str = '', 
                 album_id: Optional[int] = None):
        """Initialize SongDTO.
        
        Args:
            id: Song ID (None for new songs)
            title: Song title
            duration: Duration in seconds
            track_number: Track position on album
            genre: Song genre
            spotify_track_id: Spotify track identifier
            spotify_link: URL to song on Spotify
            album_id: ID of the album this song belongs to
        """
        self.id = id
        self.title = title
        self.duration = duration
        self.track_number = track_number
        self.genre = genre
        self.spotify_track_id = spotify_track_id
        self.spotify_link = spotify_link
        self.album_id = album_id
    
    def format_duration(self) -> str:
        """Format duration from seconds to MM:SS format."""
        if not self.duration:
            return '0:00'
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f'{minutes}:{seconds:02d}'


class AlbumDTO:
    """Data Transfer Object for Album.
    
    Represents album data in a format suitable for service/controller layers.
    """
    
    def __init__(self, id: Optional[int] = None, artist_id: Optional[int] = None,
                 title: str = '', release_date: Optional[date] = None,
                 description: str = '', image_link: str = '', spotify_link: str = '',
                 songs: Optional[List[SongDTO]] = None, artist_name: str = ''):
        """Initialize AlbumDTO.
        
        Args:
            id: Album ID (None for new albums)
            artist_id: ID of the artist who created this album
            title: Album title
            release_date: Album release date
            description: Album description/notes
            image_link: URL to album cover art
            spotify_link: URL to album on Spotify
            songs: List of SongDTO objects in this album
            artist_name: Name of the artist (for display purposes)
        """
        self.id = id
        self.artist_id = artist_id
        self.title = title
        self.release_date = release_date
        self.description = description
        self.image_link = image_link
        self.spotify_link = spotify_link
        self.songs = songs or []
        self.artist_name = artist_name
    
    def song_count(self) -> int:
        """Return the number of songs in the album."""
        return len(self.songs)
    
    def total_duration(self) -> int:
        """Calculate total album duration in seconds."""
        return sum(song.duration or 0 for song in self.songs)
    
    def format_total_duration(self) -> str:
        """Format total album duration as MM:SS."""
        total_seconds = self.total_duration()
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f'{minutes}:{seconds:02d}'
