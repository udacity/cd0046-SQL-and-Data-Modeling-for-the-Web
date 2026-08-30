"""
Business logic layer for show-related operations.
"""
from datetime import datetime, timedelta
import logging
from dal.show import Show
from dal.venue import Venue
from dal.artist import Artist
from dto.show import ShowDTO
from dal import db
from services.availability import AvailabilityService

logger = logging.getLogger(__name__)


class ShowService():
    @staticmethod
    def get_all_shows():
        """Get all shows.
        
        Returns a list of all shows with venue and artist information.
        """
        shows = Show.query.all()
        results = []
        
        for show in shows:
            venue = Venue.query.get(show.venue_id)
            artist = Artist.query.get(show.artist_id)
            
            if not venue or not artist:
                continue
            
            results.append({
                "id": show.id,
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.isoformat()
            })
        
        return results

    @staticmethod
    def show_show_by_show_id(show_id: int):
        """Get show details by ID.
        
        Returns show data with all fields.
        """
        show = Show.query.get(show_id)
        
        if not show:
            return None
        
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        
        if not venue or not artist:
            return None
        
        return {
            "id": show.id,
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.isoformat(),
            "end_time": show.end_time.isoformat()
        }

    @staticmethod
    def search_show_by_artist_and_venue(artist_id: int = None, venue_id: int = None):
        """Search shows by artist and/or venue.
        
        Returns matching shows.
        """
        query = Show.query
        
        if artist_id:
            query = query.filter_by(artist_id=artist_id)
        
        if venue_id:
            query = query.filter_by(venue_id=venue_id)
        
        shows = query.all()
        results = []
        
        for show in shows:
            venue = Venue.query.get(show.venue_id)
            artist = Artist.query.get(show.artist_id)
            
            if not venue or not artist:
                continue
            
            results.append({
                "id": show.id,
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.isoformat()
            })
        
        return results

    @staticmethod
    def validate_show_form_data(form_data):
        """Validate and convert form data to ShowDTO.
        
        Returns (validation_error, show_dto)
        """
        validation_error = None
        
        data = ShowDTO(
            id=None,
            venue_id=int(form_data.get('venue_id', 0)),
            artist_id=int(form_data.get('artist_id', 0)),
            start_time=form_data.get('start_time', ''),
            end_time=form_data.get('end_time', '')
        )
        return validation_error, data

    @staticmethod
    def create_show(show_dto: ShowDTO):
        """Create a new show in the database.
        
        First checks if artist is available for the requested time using
        "Blackout Always Wins" logic (unavailable slots override available).
        
        Returns (success, error_message)
        """
        try:
            # Parse start_time string to datetime object
            start_time = datetime.fromisoformat(show_dto.start_time.replace('Z', '+00:00'))
            
            # Parse end_time if provided, otherwise default to start_time + 2 hours
            if show_dto.end_time:
                end_time = datetime.fromisoformat(show_dto.end_time.replace('Z', '+00:00'))
            else:
                end_time = start_time + timedelta(hours=2)
            
            # Check artist availability BEFORE creating the show
            is_available, availability_reason = AvailabilityService.is_artist_available(
                show_dto.artist_id,
                start_time,
                end_time
            )
            
            if not is_available:
                logger.warning(
                    f"Cannot create show: Artist {show_dto.artist_id} is not available. "
                    f"Reason: {availability_reason}"
                )
                return False, availability_reason
            
            show = Show(
                venue_id=show_dto.venue_id,
                artist_id=show_dto.artist_id,
                start_time=start_time,
                end_time=end_time
            )
            
            db.session.add(show)
            db.session.commit()
            
            logger.info(
                f"Show created successfully: Artist {show_dto.artist_id} at Venue {show_dto.venue_id} "
                f"from {start_time} to {end_time}"
            )
            return True, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating show: {str(e)}")
            return False, str(e)

    @staticmethod
    def update_show(show_id: int, show_dto: ShowDTO):
        """Update an existing show.
        
        First checks if artist is available for the requested time using
        "Blackout Always Wins" logic. Excludes the current show from
        double-booking check to allow rescheduling within available windows.
        
        Returns (success, error_message)
        """
        try:
            show = Show.query.get(show_id)
            if not show:
                return False, f"Show with id {show_id} not found"
            
            start_time = datetime.fromisoformat(show_dto.start_time.replace('Z', '+00:00'))
            
            # Update end_time if provided, otherwise default to start_time + 2 hours
            if show_dto.end_time:
                end_time = datetime.fromisoformat(show_dto.end_time.replace('Z', '+00:00'))
            else:
                end_time = start_time + timedelta(hours=2)
            
            # If artist changed, check new artist's availability
            if show_dto.artist_id != show.artist_id:
                is_available, availability_reason = AvailabilityService.is_artist_available(
                    show_dto.artist_id,
                    start_time,
                    end_time
                )
                if not is_available:
                    logger.warning(
                        f"Cannot update show {show_id}: Artist {show_dto.artist_id} is not available. "
                        f"Reason: {availability_reason}"
                    )
                    return False, availability_reason
            else:
                # Same artist, just reschedule - exclude current show from double-booking check
                is_available, availability_reason = AvailabilityService.is_artist_available(
                    show_dto.artist_id,
                    start_time,
                    end_time,
                    exclude_show_id=show_id
                )
                if not is_available:
                    logger.warning(
                        f"Cannot update show {show_id}: Artist {show_dto.artist_id} is not available. "
                        f"Reason: {availability_reason}"
                    )
                    return False, availability_reason
            
            show.venue_id = show_dto.venue_id
            show.artist_id = show_dto.artist_id
            show.start_time = start_time
            show.end_time = end_time
            
            db.session.commit()
            
            logger.info(
                f"Show {show_id} updated successfully: Artist {show_dto.artist_id} at Venue {show_dto.venue_id} "
                f"from {start_time} to {end_time}"
            )
            return True, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating show {show_id}: {str(e)}")
            return False, str(e)

    @staticmethod
    def delete_show(show_id: int):
        """Delete a show from the database.
        
        Returns (success, error_message)
        """
        try:
            show = Show.query.get(show_id)
            if not show:
                return False, "Show not found"
            
            db.session.delete(show)
            db.session.commit()
            
            logger.info(f"Show {show_id} deleted successfully")
            return True, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting show {show_id}: {str(e)}")
            return False, str(e)
