"""Business logic for Song management."""

from dal import db, Song, Album
from dto.album import SongDTO
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SongService:
    """Service for managing songs."""
    
    @staticmethod
    def get_songs_by_album(album_id: int) -> List[SongDTO]:
        """Get all songs for a specific album.
        
        Args:
            album_id: ID of the album
            
        Returns:
            List of SongDTO objects, sorted by track number
        """
        try:
            songs = Song.query.filter_by(album_id=album_id).order_by(
                Song.track_number.asc(),
                Song.id.asc()  # Fallback to ID if no track number
            ).all()
            return [SongService._song_to_dto(song) for song in songs]
        except Exception as e:
            logger.error(f"Error fetching songs for album {album_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_song_by_id(song_id: int) -> Optional[SongDTO]:
        """Get a single song by ID.
        
        Args:
            song_id: ID of the song
            
        Returns:
            SongDTO object or None if not found
        """
        try:
            song = Song.query.get(song_id)
            if not song:
                return None
            return SongService._song_to_dto(song)
        except Exception as e:
            logger.error(f"Error fetching song {song_id}: {str(e)}")
            return None
    
    @staticmethod
    def create_song(song_dto: SongDTO) -> Tuple[bool, Optional[str]]:
        """Create a new song in the database.
        
        Args:
            song_dto: SongDTO with song data
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            # Verify album exists
            album = Album.query.get(song_dto.album_id)
            if not album:
                return False, f"Album with ID {song_dto.album_id} not found"
            
            # Create song record
            song = Song(
                album_id=song_dto.album_id,
                title=song_dto.title,
                duration=song_dto.duration,
                track_number=song_dto.track_number,
                genre=song_dto.genre,
                spotify_track_id=song_dto.spotify_track_id,
                spotify_link=song_dto.spotify_link
            )
            
            db.session.add(song)
            db.session.commit()
            logger.info(f"Successfully created song '{song.title}' in album {song_dto.album_id}")
            return True, None
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error creating song: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def update_song(song_id: int, song_dto: SongDTO) -> Tuple[bool, Optional[str]]:
        """Update an existing song.
        
        Args:
            song_id: ID of the song to update
            song_dto: SongDTO with updated data
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            song = Song.query.get(song_id)
            if not song:
                return False, f"Song with ID {song_id} not found"
            
            # Update fields
            song.title = song_dto.title
            song.duration = song_dto.duration
            song.track_number = song_dto.track_number
            song.genre = song_dto.genre
            song.spotify_track_id = song_dto.spotify_track_id
            song.spotify_link = song_dto.spotify_link
            
            db.session.commit()
            logger.info(f"Successfully updated song {song_id}")
            return True, None
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error updating song: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def delete_song(song_id: int) -> Tuple[bool, Optional[str]]:
        """Delete a song.
        
        Args:
            song_id: ID of the song to delete
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            song = Song.query.get(song_id)
            if not song:
                return False, f"Song with ID {song_id} not found"
            
            song_title = song.title
            db.session.delete(song)
            db.session.commit()
            logger.info(f"Successfully deleted song {song_id} ({song_title})")
            return True, None
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error deleting song: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def validate_song_form_data(form_data, album_id: int) -> Tuple[Dict[str, str], Optional[SongDTO]]:
        """Validate song form data.
        
        Args:
            form_data: Form data dictionary from request.form
            album_id: ID of the album the song belongs to
            
        Returns:
            Tuple of (validation_errors: dict, song_dto: SongDTO or None)
            If validation fails, returns (errors_dict, None)
            If validation passes, returns ({}, song_dto)
        """
        errors = {}
        
        # Title is required
        title = form_data.get('title', '').strip()
        if not title:
            errors['title'] = 'Song title is required'
        elif len(title) > 255:
            errors['title'] = 'Song title must be less than 255 characters'
        
        # Track number is optional but must be positive if provided
        track_number = form_data.get('track_number', '').strip()
        if track_number:
            try:
                track_number = int(track_number)
                if track_number < 0:
                    errors['track_number'] = 'Track number must be positive'
            except ValueError:
                errors['track_number'] = 'Track number must be a whole number'
        else:
            track_number = None
        
        # Duration is optional but must be positive if provided
        duration = form_data.get('duration', '').strip()
        if duration:
            try:
                duration = int(duration)
                if duration < 0:
                    errors['duration'] = 'Duration must be positive'
            except ValueError:
                errors['duration'] = 'Duration must be a whole number'
        else:
            duration = None
        
        # Genre is optional
        genre = form_data.get('genre', '').strip()
        
        # Spotify link is optional but must be valid if provided
        spotify_link = form_data.get('spotify_link', '').strip()
        if spotify_link and not spotify_link.startswith('https://open.spotify.com/'):
            errors['spotify_link'] = 'Spotify link must start with https://open.spotify.com/'
        
        if errors:
            return errors, None
        
        # Create and return SongDTO
        song_dto = SongDTO(
            album_id=album_id,
            title=title,
            duration=duration,
            track_number=track_number,
            genre=genre,
            spotify_link=spotify_link
        )
        
        return {}, song_dto
    
    @staticmethod
    def _song_to_dto(song: Song) -> SongDTO:
        """Convert Song model to SongDTO.
        
        Args:
            song: Song model instance
            
        Returns:
            SongDTO with song data
        """
        return SongDTO(
            id=song.id,
            album_id=song.album_id,
            title=song.title,
            duration=song.duration,
            track_number=song.track_number,
            genre=song.genre,
            spotify_track_id=song.spotify_track_id,
            spotify_link=song.spotify_link
        )
