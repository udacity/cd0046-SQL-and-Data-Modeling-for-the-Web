"""
Service for managing artist availability.

Implements the "Blackout Always Wins" logic:
- If ANY overlapping slot is marked unavailable, the artist is unavailable
- Date exceptions override weekly recurring availability
- Existing shows are checked for double-booking
"""

import logging
from datetime import datetime, time, timedelta
from dal.availability import ArtistAvailability, ArtistAvailabilityException
from dal.show import Show
from dal import db

logger = logging.getLogger(__name__)


class AvailabilityService:
    """Service for checking and managing artist availability."""
    
    @staticmethod
    def is_artist_available(artist_id, start_datetime, end_datetime, exclude_show_id=None):
        """
        Check if an artist is available for a given time slot.
        
        Implements "Blackout Always Wins" logic:
        1. Check date-specific exceptions first (highest priority)
        2. Check weekly recurring availability 
        3. Check for double-booking
        
        Args:
            artist_id (int): Artist ID to check
            start_datetime (datetime): Start of requested time slot
            end_datetime (datetime): End of requested time slot
            exclude_show_id (int, optional): Show ID to exclude from double-booking check
        
        Returns:
            tuple: (is_available, reason)
                - is_available (bool): Whether artist is available
                - reason (str): Explanation of availability status
        """
        
        try:
            # Step 1: Check date-specific exceptions (highest priority)
            exception_result = AvailabilityService._check_exception(
                artist_id, start_datetime, end_datetime
            )
            if exception_result is not None:
                return exception_result
            
            # Step 2: Check weekly recurring availability
            weekly_result = AvailabilityService._check_weekly_availability(
                artist_id, start_datetime, end_datetime
            )
            if not weekly_result[0]:
                return weekly_result
            
            # Step 3: Check for double-booking
            double_booking = AvailabilityService._check_double_booking(
                artist_id, start_datetime, end_datetime, exclude_show_id
            )
            if not double_booking[0]:
                return double_booking
            
            # Artist is available!
            return (True, "Artist is available for this time slot")
        
        except Exception as e:
            logger.exception(f"Error checking availability for artist {artist_id}: {str(e)}")
            return (False, f"Error checking availability: {str(e)}")
    
    @staticmethod
    def _check_exception(artist_id, start_datetime, end_datetime):
        """
        Check if a date-specific exception exists for the requested time.
        
        Returns:
            tuple or None: (is_available, reason) or None if no exception applies
        """
        exception_date = start_datetime.date()
        
        # Find exceptions for this date
        exceptions = ArtistAvailabilityException.query.filter(
            ArtistAvailabilityException.artist_id == artist_id,
            ArtistAvailabilityException.exception_date == exception_date
        ).all()
        
        if not exceptions:
            return None  # No exception for this date
        
        # Check if any exception overlaps the requested time
        for exc in exceptions:
            if AvailabilityService._times_overlap(
                start_datetime.time(),
                end_datetime.time(),
                exc.start_time,
                exc.end_time
            ):
                logger.info(
                    f"Artist {artist_id} has exception on {exception_date}: "
                    f"available={exc.is_available}, reason={exc.reason}"
                )
                
                if exc.is_available:
                    return (True, f"Available on {exception_date} (exception: {exc.reason})")
                else:
                    return (False, f"Unavailable on {exception_date} (exception: {exc.reason})")
        
        return None  # Exception exists but doesn't overlap requested time
    
    @staticmethod
    def _check_weekly_availability(artist_id, start_datetime, end_datetime):
        """
        Check weekly recurring availability.
        
        Implements "Blackout Always Wins": If ANY overlapping slot is unavailable, reject.
        
        Returns:
            tuple: (is_available, reason)
        """
        day_of_week = start_datetime.weekday()  # 0=Monday, 6=Sunday
        start_time = start_datetime.time()
        end_time = end_datetime.time()
        
        # Find all availability slots for this day
        slots = ArtistAvailability.query.filter(
            ArtistAvailability.artist_id == artist_id,
            ArtistAvailability.day_of_week == day_of_week
        ).all()
        
        if not slots:
            # No availability defined for this day - artist is unavailable
            logger.info(f"Artist {artist_id} has no availability for day {day_of_week}")
            return (False, "No availability defined for this day")
        
        # Check for overlaps
        overlapping_slots = [
            slot for slot in slots
            if AvailabilityService._times_overlap(start_time, end_time, slot.start_time, slot.end_time)
        ]
        
        if not overlapping_slots:
            # No slots overlap the requested time
            logger.info(f"Artist {artist_id} has no overlapping slots for {start_time}-{end_time}")
            return (False, "No availability during this time slot")
        
        # BLACKOUT ALWAYS WINS: If ANY overlapping slot is unavailable, reject
        for slot in overlapping_slots:
            if not slot.is_available:
                logger.info(
                    f"Artist {artist_id} is blocked by blackout: {slot.start_time}-{slot.end_time}"
                )
                return (False, f"Blackout period: {slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}")
        
        # All overlapping slots are available
        logger.info(f"Artist {artist_id} is available for {start_time}-{end_time}")
        return (True, "Available during this time slot")
    
    @staticmethod
    def _check_double_booking(artist_id, start_datetime, end_datetime, exclude_show_id=None):
        """
        Check if artist has any existing shows that conflict with this time slot.
        
        Returns:
            tuple: (is_available, reason) where is_available=False means there's a conflict
        """
        
        # Find shows for this artist that overlap the requested time
        conflicting_shows = Show.query.filter(
            Show.artist_id == artist_id,
            # Show starts before requested end time AND
            Show.start_time < end_datetime,
            # Show ends after requested start time
            Show.end_time > start_datetime
        )
        
        # Exclude the current show if updating
        if exclude_show_id:
            conflicting_shows = conflicting_shows.filter(Show.id != exclude_show_id)
        
        conflicting_shows = conflicting_shows.all()
        
        if conflicting_shows:
            conflict = conflicting_shows[0]
            logger.warning(
                f"Artist {artist_id} has conflicting show: {conflict.start_time} - {conflict.end_time}"
            )
            return (
                False,  # NOT available due to conflicting show
                f"Artist already has a show at {conflict.start_time.strftime('%Y-%m-%d %H:%M')}"
            )
        
        return (True, "No conflicting shows")
    
    @staticmethod
    def _times_overlap(start1, end1, start2, end2):
        """
        Check if two time ranges overlap.
        
        Args:
            start1, end1: First time range (time objects)
            start2, end2: Second time range (time objects)
        
        Returns:
            bool: True if ranges overlap
        """
        # Times overlap if: start1 < end2 AND start2 < end1
        return start1 < end2 and start2 < end1
    
    @staticmethod
    def summarize_artist_availability(artist_id):
        """
        Generate a human-readable summary of artist's availability.
        
        Returns:
            str: Formatted availability summary
        """
        try:
            slots = ArtistAvailability.query.filter(
                ArtistAvailability.artist_id == artist_id
            ).all()
            
            if not slots:
                return "No availability defined"
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            summary_lines = []
            
            for day in range(7):
                day_slots = [s for s in slots if s.day_of_week == day]
                if not day_slots:
                    continue
                
                day_name = day_names[day]
                availability_parts = []
                
                for slot in sorted(day_slots, key=lambda s: s.start_time):
                    status = "Available" if slot.is_available else "Unavailable (Blackout)"
                    time_range = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
                    availability_parts.append(f"{time_range} ({status})")
                
                summary_lines.append(f"{day_name}: {', '.join(availability_parts)}")
            
            return "\n".join(summary_lines) if summary_lines else "No availability defined"
        
        except Exception as e:
            logger.exception(f"Error summarizing availability for artist {artist_id}: {str(e)}")
            return f"Error retrieving availability: {str(e)}"

    @staticmethod
    def get_artist_availability_summary(artist_id):
        """
        Get structured artist availability data for display on booking form.
        
        Returns:
            dict: Contains 'recurring_slots' and 'exceptions' lists, or None if error
        """
        try:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Get recurring slots (both available and unavailable)
            recurring_slots = []
            slots = ArtistAvailability.query.filter(
                ArtistAvailability.artist_id == artist_id
            ).order_by(ArtistAvailability.day_of_week, ArtistAvailability.start_time).all()
            
            for slot in slots:
                day_name = day_names[slot.day_of_week]
                time_range = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
                status = "Available" if slot.is_available else "❌ Unavailable (Blackout)"
                recurring_slots.append(f"{day_name}: {time_range} - {status}")
            
            # Get upcoming exceptions (next 30 days)
            from datetime import datetime, timedelta
            today = datetime.now().date()
            thirty_days_later = today + timedelta(days=30)
            
            exception_list = []
            exceptions = ArtistAvailabilityException.query.filter(
                ArtistAvailabilityException.artist_id == artist_id,
                ArtistAvailabilityException.exception_date >= today,
                ArtistAvailabilityException.exception_date <= thirty_days_later
            ).order_by(ArtistAvailabilityException.exception_date).all()
            
            for exc in exceptions:
                reason = f" ({exc.reason})" if exc.reason else ""
                time_range = f"{exc.start_time.strftime('%H:%M')}-{exc.end_time.strftime('%H:%M')}"
                status = "Available (Exception)" if exc.is_available else "❌ Unavailable (Exception)"
                exception_list.append(f"{exc.exception_date}: {time_range} - {status}{reason}")
            
            return {
                'recurring_slots': recurring_slots,
                'exceptions': exception_list
            }
        
        except Exception as e:
            logger.exception(f"Error getting availability summary for artist {artist_id}: {str(e)}")
            return None
