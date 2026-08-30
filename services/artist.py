"""
Business logic layer for artist-related operations.
"""
from datetime import datetime
from dal.artist import Artist
from dal.show import Show
from dal.venue import Venue
from dal.genre import Genre
from dto.artist import ArtistDTO
from dal import db
from services.common import CommonService


class ArtistService():
    def get_all_artists():
        """Get all artists.
        
        Returns a list of all artists in the database.
        """
        artists = Artist.query.all()
        return [{
            "id": artist.id,
            "name": artist.name,
        } for artist in artists]

    @staticmethod
    def show_artist_by_artist_id(artist_id: int):
        """Get artist details by ID.
        
        Returns artist data with all fields and show information.
        """
        artist = Artist.query.get(artist_id)
        
        if not artist:
            return None
        
        # Query all shows for this artist
        shows = Show.query.filter_by(artist_id=artist_id).all()
        
        now = datetime.now()
        past_shows = []
        upcoming_shows = []
        
        for show in shows:
            # Get venue info
            venue = Venue.query.get(show.venue_id)
            if not venue:
                continue
            
            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.isoformat()
            }
            
            if show.start_time < now:
                past_shows.append(show_data)
            else:
                upcoming_shows.append(show_data)
        
        # Build artist response - convert genres relationship to list of names
        genres = [g.name for g in artist.genres]
        
        return {
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    @staticmethod
    def search_artist_by_name(search_term: str):
        """Search artists by name (case-insensitive, partial string match).
        
        Returns matching artists with basic info.
        """
        # Query artists where name contains search_term (case-insensitive)
        artists = Artist.query.filter(
            Artist.name.ilike(f'%{search_term}%')
        ).all()
        
        results = []
        now = datetime.now()
        
        for artist in artists:
            # Count upcoming shows for this artist
            upcoming_shows = Show.query.filter(
                Show.artist_id == artist.id,
                Show.start_time >= now
            ).count()
            
            results.append({
                "id": artist.id,
                "name": artist.name,
                "city": artist.city,
                "state": artist.state,
                "num_upcoming_shows": upcoming_shows,
            })
        
        return {
            "count": len(results),
            "data": results
        }

    @staticmethod
    def validate_artist_form_data(form_data):
        """Validate and convert form data to ArtistDTO.
        
        Returns (validation_errors_dict, artist_dto)
        validation_errors_dict is None if no errors, or dict like {'phone': 'error msg', 'image_link': 'error msg'}
        """
        errors = {}
        genres = form_data.getlist('genres') if hasattr(form_data, 'getlist') else []
        
        # Extract seeking_venue (WTForms sends 'y' for checked, nothing for unchecked)
        seeking_venue = form_data.get('seeking_venue') == 'y'
        seeking_description = form_data.get('seeking_description', '')
        
        phone = form_data.get('phone', '').strip()
        facebook_link = form_data.get('facebook_link', '').strip()
        website_link = form_data.get('website_link', '').strip()
        image_link = form_data.get('image_link', '').strip()
        
        # Validate phone number
        phone_valid, phone_error = CommonService.validate_phone(phone)
        if not phone_valid:
            errors['phone'] = phone_error
        
        # Validate image link
        img_valid, img_error = CommonService.validate_url(image_link, "Image link")
        if not img_valid:
            errors['image_link'] = img_error
        
        # Validate facebook link
        fb_valid, fb_error = CommonService.validate_url(facebook_link, "Facebook link")
        if not fb_valid:
            errors['facebook_link'] = fb_error
        
        # Validate website link
        web_valid, web_error = CommonService.validate_url(website_link, "Website link")
        if not web_valid:
            errors['website_link'] = web_error
        
        # If any validation errors, return them
        if errors:
            return errors, None
        
        data = ArtistDTO(
            id=None,
            name=form_data.get('name', ''),
            city=form_data.get('city', ''),
            state=form_data.get('state', ''),
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website_link,
            genres=genres,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )
        return None, data

    @staticmethod
    def create_artist(artist_dto: ArtistDTO):
        """Create a new artist in the database.
        
        Returns (success, error_message)
        """
        try:
            artist = Artist(
                name=artist_dto.name,
                city=artist_dto.city,
                state=artist_dto.state,
                phone=artist_dto.phone,
                image_link=artist_dto.image_link,
                facebook_link=artist_dto.facebook_link,
                website=artist_dto.website,
                seeking_venue=artist_dto.seeking_venue,
                seeking_description=artist_dto.seeking_description
            )
            
            # Link genres to artist from artist_dto.genres (genre names)
            from dal.genre import Genre
            if artist_dto.genres:
                for genre_name in artist_dto.genres:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if genre:
                        artist.genres.append(genre)
            
            db.session.add(artist)
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_artist(artist_id: int, artist_dto: ArtistDTO):
        """Update an existing artist.
        
        Returns (success, error_message)
        """
        try:
            # Find the artist
            artist = Artist.query.get(artist_id)
            if not artist:
                return False, f"Artist with id {artist_id} not found"
            
            # Update artist fields
            artist.name = artist_dto.name
            artist.city = artist_dto.city
            artist.state = artist_dto.state
            artist.phone = artist_dto.phone
            artist.image_link = artist_dto.image_link
            artist.facebook_link = artist_dto.facebook_link
            artist.website = artist_dto.website
            artist.seeking_venue = artist_dto.seeking_venue
            artist.seeking_description = artist_dto.seeking_description
            
            # Update genres relationship from artist_dto.genres
            from dal.genre import Genre
            if artist_dto.genres is not None:
                # Clear existing genres
                artist.genres.clear()
                # Add new genres
                for genre_name in artist_dto.genres:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if genre:
                        artist.genres.append(genre)
            
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_artist(artist_id: int):
        """Delete an artist from the database.
        
        First checks if artist has any shows. If they do, deletion is prevented
        and an error message is returned. If deletion proceeds, all associated
        availability slots are cascade deleted.
        
        Returns (success, error_message)
        """
        try:
            artist = Artist.query.get(artist_id)
            if not artist:
                return False, "Artist not found"
            
            # Check if artist has any shows
            from dal.show import Show
            shows = Show.query.filter_by(artist_id=artist_id).all()
            if shows:
                upcoming_shows = [s for s in shows if s.start_time > datetime.now()]
                if upcoming_shows:
                    return (
                        False,
                        f"Cannot delete artist with upcoming shows. "
                        f"Please cancel or reschedule {len(upcoming_shows)} show(s) first."
                    )
            
            # Artist has no shows - safe to delete
            # Availability slots will cascade delete via FK constraint
            db.session.delete(artist)
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_recent_artists(limit: int = 10):
        """Get the most recently created artists.
        
        Returns a list of the N most recent artists, ordered by creation date.
        """
        try:
            artists = Artist.query.order_by(
                Artist.created_at.desc()
            ).limit(limit).all()
            
            return [{
                "id": artist.id,
                "name": artist.name,
                "city": artist.city,
                "state": artist.state,
                "image_link": artist.image_link,
            } for artist in artists]
        except Exception as e:
            return []

    @staticmethod
    def search_artist_by_location(city: str = None, state: str = None, genres: list = None):
        """Search artists by city, state, and/or genres.
        
        Returns matching artists with upcoming shows count.
        """
        query = Artist.query
        
        if city:
            query = query.filter(Artist.city.ilike(f'%{city}%'))
        
        if state:
            query = query.filter(Artist.state.ilike(f'%{state}%'))
        
        # If genres are specified, filter artists that have at least one of the genres
        if genres:
            query = query.join(Artist.genres).filter(Genre.name.in_(genres)).distinct()
        
        artists = query.all()
        
        results = []
        now = datetime.now()
        
        for artist in artists:
            # Count upcoming shows for this artist
            upcoming_shows = Show.query.filter(
                Show.artist_id == artist.id,
                Show.start_time >= now
            ).count()
            
            results.append({
                "id": artist.id,
                "name": artist.name,
                "city": artist.city,
                "state": artist.state,
                "num_upcoming_shows": upcoming_shows,
            })
        
        return {
            "count": len(results),
            "data": results
        }
