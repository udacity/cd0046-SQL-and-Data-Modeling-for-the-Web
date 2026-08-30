"""
SQLAlchemy models for Artist availability management.
"""
from datetime import datetime
from dal import db


class ArtistAvailability(db.Model):
    """Artist's recurring weekly availability schedule.
    
    Stores time slots for each day of the week when an artist is available or unavailable.
    day_of_week: 0=Monday, 1=Tuesday, ..., 6=Sunday
    start_time/end_time: time objects (e.g., 18:00, 23:00)
    is_available: true=available slot, false=blackout/unavailable
    """
    __tablename__ = 'artist_availability'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6: Mon-Sun
    start_time = db.Column(db.Time, nullable=False)      # e.g., 18:00
    end_time = db.Column(db.Time, nullable=False)        # e.g., 23:00
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Ensure no duplicate schedule entries for same day/time
    __table_args__ = (
        db.UniqueConstraint('artist_id', 'day_of_week', 'start_time', 'end_time', 
                           name='uq_artist_availability_slot'),
    )

    def __repr__(self):
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        avail_str = "Available" if self.is_available else "Unavailable"
        return f"<ArtistAvailability {day_names[self.day_of_week]} {self.start_time}-{self.end_time} ({avail_str})>"


class ArtistAvailabilityException(db.Model):
    """Date-specific availability exceptions that override weekly schedule.
    
    Used for holidays, tours, special events, etc.
    If an exception exists for a date, it overrides the weekly recurring schedule for that date.
    exception_date: the specific date this exception applies to
    is_available: overrides the weekly schedule (true=available, false=unavailable)
    reason: optional description (e.g., "Holiday", "Tour", "Studio Session")
    """
    __tablename__ = 'artist_availability_exception'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable=False)
    exception_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=False)
    reason = db.Column(db.String(200), nullable=True)  # "Holiday", "Tour", etc
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # One exception per artist per date
    __table_args__ = (
        db.UniqueConstraint('artist_id', 'exception_date', 
                           name='uq_artist_availability_exception'),
    )

    def __repr__(self):
        avail_str = "Available" if self.is_available else "Unavailable"
        reason_str = f" ({self.reason})" if self.reason else ""
        return f"<ArtistAvailabilityException {self.exception_date} {self.start_time}-{self.end_time} ({avail_str}){reason_str}>"
