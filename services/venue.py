from datetime import datetime
from dal.venue import Venue
from dal.show import Show
from dal.artist import Artist
from dal.genre import Genre
from dto.venue import VenueDTO
from dal import db
from services.common import CommonService

class VenueService():
    def get_venues_grouped_by_location():
        """Get all venues grouped by city and state.
        
        Returns a list of dictionaries with structure:
        [{
            "city": "San Francisco",
            "state": "CA",
            "venues": [{"id": 1, "name": "...", "num_upcoming_shows": 0}, ...]
        }, ...]
        """
        venues = Venue.query.all()
        now = datetime.now()
        
        # Group venues by city and state
        grouped = {}
        for venue in venues:
            key = (venue.city, venue.state)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(venue)
        
        # Transform into expected format
        data = []
        for (city, state), venue_list in grouped.items():
            venues_formatted = []
            for v in venue_list:
                # Count upcoming shows for this venue
                num_upcoming_shows = Show.query.filter(
                    Show.venue_id == v.id,
                    Show.start_time >= now
                ).count()
                
                venues_formatted.append({
                    "id": v.id,
                    "name": v.name,
                    "num_upcoming_shows": num_upcoming_shows
                })
            
            data.append({
                "city": city,
                "state": state,
                "venues": venues_formatted
            })
        
        return data

    @staticmethod
    def show_venue_by_venue_id(venue_id):
        """Get venue details by ID with past and upcoming shows.
        
        Returns venue data with all fields, shows separated by date.
        """
        venue = Venue.query.get(venue_id)
        
        if not venue:
            return None
        
        # Query all shows for this venue
        shows = Show.query.filter_by(venue_id=venue_id).all()
        
        now = datetime.now()
        past_shows = []
        upcoming_shows = []
        
        for show in shows:
            # Get artist info
            artist = Artist.query.get(show.artist_id)
            if not artist:
                continue
            
            show_data = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.isoformat()
            }
            
            if show.start_time < now:
                past_shows.append(show_data)
            else:
                upcoming_shows.append(show_data)
        
        # Build venue response - convert genres relationship to list of names
        genres = [g.name for g in venue.genres]
        
        return {
            "id": venue.id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    @staticmethod
    def search_venue_by_name(search_term):
        """Search venues by name (case-insensitive, partial string match).
        
        Returns matching venues with upcoming shows count.
        """
        # Query venues where name contains search_term (case-insensitive)
        venues = Venue.query.filter(
            Venue.name.ilike(f'%{search_term}%')
        ).all()
        
        results = []
        now = datetime.now()
        
        for venue in venues:
            # Count upcoming shows for this venue
            upcoming_shows = Show.query.filter(
                Show.venue_id == venue.id,
                Show.start_time >= now
            ).count()
            
            results.append({
                "id": venue.id,
                "name": venue.name,
                "city": venue.city,
                "state": venue.state,
                "num_upcoming_shows": upcoming_shows,
            })
        
        return {
            "count": len(results),
            "data": results
        }

    @staticmethod
    def validate_venue_form_data(form_data):
        """Validate venue form data and collect all errors.
        
        Returns (validation_errors_dict, venue_dto)
        validation_errors_dict is None if no errors, or dict like {'phone': 'error msg', 'image_link': 'error msg'}
        """
        errors = {}
        try:
            genres = form_data.getlist('genres') if hasattr(form_data, 'getlist') else []
            
            # Extract seeking_talent (WTForms sends 'y' for checked, nothing for unchecked)
            seeking_talent = form_data.get('seeking_talent') == 'y'
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
            
            data = VenueDTO(
                id=None,
                name=form_data['name'],
                city=form_data['city'],
                state=form_data['state'],
                address=form_data['address'],
                phone=phone,
                image_link=image_link,
                facebook_link=facebook_link,
                website=website_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description,
                genres=genres
            )
            return None, data
        except (KeyError, AttributeError) as e:
            return {'general': f"Missing required field: {str(e)}"}, None

    @staticmethod
    def create_venue(venue_dto: VenueDTO):
        """Create a new venue in the database.
        
        Returns (success, error_message)
        """
        try:
            venue = Venue(
                name=venue_dto.name,
                city=venue_dto.city,
                state=venue_dto.state,
                address=venue_dto.address,
                phone=venue_dto.phone,
                image_link=venue_dto.image_link,
                facebook_link=venue_dto.facebook_link,
                website=venue_dto.website,
                seeking_talent=venue_dto.seeking_talent,
                seeking_description=venue_dto.seeking_description
            )
            
            # Link genres to venue from venue_dto.genres (genre names)
            from dal.genre import Genre
            if venue_dto.genres:
                for genre_name in venue_dto.genres:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if genre:
                        venue.genres.append(genre)
            
            db.session.add(venue)
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_venue(venue_id:int, venue_dto:VenueDTO):
        try:
            # Find the venue
            venue = Venue.query.get(venue_id)
            if not venue:
                return False, f"Venue with id {venue_id} not found"
            
            # Update venue fields
            venue.name = venue_dto.name
            venue.city = venue_dto.city
            venue.state = venue_dto.state
            venue.address = venue_dto.address
            venue.phone = venue_dto.phone
            venue.image_link = venue_dto.image_link
            venue.facebook_link = venue_dto.facebook_link
            venue.website = venue_dto.website
            venue.seeking_talent = venue_dto.seeking_talent
            venue.seeking_description = venue_dto.seeking_description
            
            # Update genres relationship from venue_dto.genres
            from dal.genre import Genre
            if venue_dto.genres is not None:
                # Clear existing genres
                venue.genres.clear()
                # Add new genres
                for genre_name in venue_dto.genres:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if genre:
                        venue.genres.append(genre)
            
            # Commit changes
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_venue(venue_id: int):
        """Delete a venue from the database.
        
        First checks if venue has any shows. If they do, deletion is prevented
        and an error message is returned.
        
        Returns (success, error_message)
        """
        try:
            venue = Venue.query.get(venue_id)
            if not venue:
                return False, "Venue not found"
            
            # Check if venue has any shows
            from dal.show import Show
            from datetime import datetime
            shows = Show.query.filter_by(venue_id=venue_id).all()
            if shows:
                upcoming_shows = [s for s in shows if s.start_time > datetime.now()]
                if upcoming_shows:
                    return (
                        False,
                        f"Cannot delete venue with upcoming shows. "
                        f"Please cancel or reschedule {len(upcoming_shows)} show(s) first."
                    )
            
            # Venue has no upcoming shows - safe to delete
            db.session.delete(venue)
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_recent_venues(limit: int = 10):
        """Get the most recently created venues.
        
        Returns a list of the N most recent venues, ordered by creation date.
        """
        try:
            venues = Venue.query.order_by(
                Venue.created_at.desc()
            ).limit(limit).all()
            
            return [{
                "id": venue.id,
                "name": venue.name,
                "city": venue.city,
                "state": venue.state,
                "image_link": venue.image_link,
            } for venue in venues]
        except Exception as e:
            return []

    @staticmethod
    def search_venue_by_location(city: str = None, state: str = None, genres: list = None):
        """Search venues by city, state, and/or genres.
        
        Returns matching venues with upcoming shows count.
        """
        query = Venue.query
        
        if city:
            query = query.filter(Venue.city.ilike(f'%{city}%'))
        
        if state:
            query = query.filter(Venue.state.ilike(f'%{state}%'))
        
        # If genres are specified, filter venues that have at least one of the genres
        if genres:
            query = query.join(Venue.genres).filter(Genre.name.in_(genres)).distinct()
        
        venues = query.all()
        
        results = []
        now = datetime.now()
        
        for venue in venues:
            # Count upcoming shows for this venue
            upcoming_shows = Show.query.filter(
                Show.venue_id == venue.id,
                Show.start_time >= now
            ).count()
            
            results.append({
                "id": venue.id,
                "name": venue.name,
                "city": venue.city,
                "state": venue.state,
                "num_upcoming_shows": upcoming_shows,
            })
        
        return {
            "count": len(results),
            "data": results
        }