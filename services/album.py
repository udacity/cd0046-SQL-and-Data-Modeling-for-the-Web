"""Business logic for Album management."""

from dal import db, Album, Song, Artist
from dto.album import AlbumDTO, SongDTO
from typing import List, Tuple, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlbumService:
    """Service for managing albums."""
    
    @staticmethod
    def get_all_albums() -> List[AlbumDTO]:
        """Get all albums from the database, sorted by release date (newest first).
        
        Returns:
            List of AlbumDTO objects
        """
        try:
            albums = Album.query.order_by(Album.release_date.desc()).all()
            return [AlbumService._album_to_dto(album) for album in albums]
        except Exception as e:
            logger.error(f"Error fetching all albums: {str(e)}")
            return []
    
    @staticmethod
    def get_albums_by_artist(artist_id: int) -> List[AlbumDTO]:
        """Get all albums for a specific artist.
        
        Args:
            artist_id: ID of the artist
            
        Returns:
            List of AlbumDTO objects for the artist, sorted by release date (newest first)
        """
        try:
            albums = Album.query.filter_by(artist_id=artist_id).order_by(
                Album.release_date.desc()
            ).all()
            return [AlbumService._album_to_dto(album) for album in albums]
        except Exception as e:
            logger.error(f"Error fetching albums for artist {artist_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_album_by_id(album_id: int) -> Optional[AlbumDTO]:
        """Get a single album by ID with all its songs.
        
        Args:
            album_id: ID of the album
            
        Returns:
            AlbumDTO object or None if not found
        """
        try:
            album = Album.query.get(album_id)
            if not album:
                return None
            return AlbumService._album_to_dto(album)
        except Exception as e:
            logger.error(f"Error fetching album {album_id}: {str(e)}")
            return None
    
    @staticmethod
    def create_album(album_dto: AlbumDTO) -> Tuple[bool, Optional[str]]:
        """Create a new album in the database.
        
        Args:
            album_dto: AlbumDTO with album data
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            # Verify artist exists
            artist = Artist.query.get(album_dto.artist_id)
            if not artist:
                return False, f"Artist with ID {album_dto.artist_id} not found"
            
            # Create album record
            album = Album(
                artist_id=album_dto.artist_id,
                title=album_dto.title,
                release_date=album_dto.release_date,
                description=album_dto.description,
                image_link=album_dto.image_link,
                spotify_link=album_dto.spotify_link
            )
            
            db.session.add(album)
            db.session.commit()
            logger.info(f"Successfully created album '{album.title}' for artist {album_dto.artist_id}")
            return True, None
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error creating album: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def update_album(album_id: int, album_dto: AlbumDTO) -> Tuple[bool, Optional[str]]:
        """Update an existing album.
        
        Args:
            album_id: ID of the album to update
            album_dto: AlbumDTO with updated data
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            album = Album.query.get(album_id)
            if not album:
                return False, f"Album with ID {album_id} not found"
            
            # Update fields
            album.title = album_dto.title
            album.release_date = album_dto.release_date
            album.description = album_dto.description
            album.image_link = album_dto.image_link
            album.spotify_link = album_dto.spotify_link
            
            db.session.commit()
            logger.info(f"Successfully updated album {album_id}")
            return True, None
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error updating album: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def delete_album(album_id: int) -> Tuple[bool, Optional[str]]:
        """Delete an album and all associated songs.
        
        Args:
            album_id: ID of the album to delete
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            album = Album.query.get(album_id)
            if not album:
                return False, f"Album with ID {album_id} not found"
            
            album_title = album.title
            db.session.delete(album)
            db.session.commit()
            logger.info(f"Successfully deleted album {album_id} ({album_title})")
            return True, None
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error deleting album: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def validate_album_form_data(form_data) -> Tuple[Dict[str, str], Optional[AlbumDTO]]:
        """Validate album form data.
        
        Args:
            form_data: Form data dictionary from request.form
            
        Returns:
            Tuple of (validation_errors: dict, album_dto: AlbumDTO or None)
            If validation fails, returns (errors_dict, None)
            If validation passes, returns ({}, album_dto)
        """
        errors = {}
        
        # Title is required
        title = form_data.get('title', '').strip()
        if not title:
            errors['title'] = 'Album title is required'
        elif len(title) > 255:
            errors['title'] = 'Album title must be less than 255 characters'
        
        # Artist ID is required
        try:
            artist_id = int(form_data.get('artist_id', 0))
            if artist_id <= 0:
                errors['artist_id'] = 'Artist is required'
            else:
                # Verify artist exists
                artist = Artist.query.get(artist_id)
                if not artist:
                    errors['artist_id'] = f'Artist with ID {artist_id} not found'
        except (ValueError, TypeError):
            errors['artist_id'] = 'Invalid artist ID'
        
        # Release date is optional but must be valid if provided
        release_date = form_data.get('release_date', '').strip()
        if release_date:
            try:
                from datetime import datetime
                release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
            except ValueError:
                errors['release_date'] = 'Invalid date format. Use YYYY-MM-DD'
        else:
            release_date = None
        
        # Image link is optional but must be valid URL if provided
        image_link = form_data.get('image_link', '').strip()
        if image_link and not (image_link.startswith('http://') or image_link.startswith('https://')):
            errors['image_link'] = 'Image link must be a valid HTTP/HTTPS URL'
        
        # Spotify link is optional but must be valid URL if provided
        spotify_link = form_data.get('spotify_link', '').strip()
        if spotify_link and not spotify_link.startswith('https://open.spotify.com/'):
            errors['spotify_link'] = 'Spotify link must start with https://open.spotify.com/'
        
        # Description is optional
        description = form_data.get('description', '').strip()
        
        if errors:
            return errors, None
        
        # Create and return AlbumDTO
        album_dto = AlbumDTO(
            artist_id=artist_id,
            title=title,
            release_date=release_date,
            description=description,
            image_link=image_link,
            spotify_link=spotify_link
        )
        
        return {}, album_dto
    
    @staticmethod
    def _album_to_dto(album: Album) -> AlbumDTO:
        """Convert Album model to AlbumDTO.
        
        Args:
            album: Album model instance
            
        Returns:
            AlbumDTO with album data
        """
        songs = [AlbumService._song_to_dto(song) for song in album.songs]
        artist_name = album.artist.name if album.artist else ''
        
        return AlbumDTO(
            id=album.id,
            artist_id=album.artist_id,
            title=album.title,
            release_date=album.release_date,
            description=album.description,
            image_link=album.image_link,
            spotify_link=album.spotify_link,
            songs=songs,
            artist_name=artist_name
        )
    
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
