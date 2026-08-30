"""
Unit tests for Availability DAL models and related operations.
Tests for ArtistAvailability and ArtistAvailabilityException models.
"""
import pytest
from datetime import datetime, time, date, timedelta
from sqlalchemy.exc import IntegrityError

from app import app
from dal import db, Artist
from dal.availability import ArtistAvailability, ArtistAvailabilityException


class TestArtistAvailability:
    """Test suite for ArtistAvailability model."""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Set up test database before each test."""
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_create_artist_availability(self, client):
        """Test creating a basic artist availability record."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=time(18, 0),  # 6 PM
                end_time=time(23, 0),    # 11 PM
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()

            retrieved = ArtistAvailability.query.get(availability.id)
            assert retrieved is not None
            assert retrieved.artist_id == artist.id
            assert retrieved.day_of_week == 0
            assert retrieved.start_time == time(18, 0)
            assert retrieved.end_time == time(23, 0)
            assert retrieved.is_available is True

    def test_artist_availability_default_is_available(self, client):
        """Test that is_available defaults to True."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=1,  # Tuesday
                start_time=time(20, 0),
                end_time=time(22, 0)
            )
            db.session.add(availability)
            db.session.commit()

            retrieved = ArtistAvailability.query.get(availability.id)
            assert retrieved.is_available is True

    def test_artist_availability_created_at_set(self, client):
        """Test that created_at is automatically set."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            before = datetime.utcnow()
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=2,  # Wednesday
                start_time=time(19, 0),
                end_time=time(23, 0),
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()
            after = datetime.utcnow()

            retrieved = ArtistAvailability.query.get(availability.id)
            assert retrieved.created_at is not None
            assert before <= retrieved.created_at <= after

    def test_artist_availability_all_days_of_week(self, client):
        """Test that all days of week (0-6) can be stored."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day_num in range(7):
                availability = ArtistAvailability(
                    artist_id=artist.id,
                    day_of_week=day_num,
                    start_time=time(18, 0),
                    end_time=time(23, 0),
                    is_available=True
                )
                db.session.add(availability)
            db.session.commit()

            for day_num in range(7):
                retrieved = ArtistAvailability.query.filter_by(
                    artist_id=artist.id,
                    day_of_week=day_num
                ).first()
                assert retrieved is not None
                assert retrieved.day_of_week == day_num

    def test_artist_availability_unique_constraint(self, client):
        """Test that duplicate availability slots cannot be created."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Create first availability
            availability1 = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_available=True
            )
            db.session.add(availability1)
            db.session.commit()

            # Try to create duplicate
            availability2 = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Same Monday
                start_time=time(18, 0),  # Same time
                end_time=time(23, 0),    # Same time
                is_available=False
            )
            db.session.add(availability2)
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_artist_availability_different_times_same_day(self, client):
        """Test that different time slots on the same day are allowed."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Morning slot
            morning = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=time(9, 0),
                end_time=time(12, 0),
                is_available=True
            )
            db.session.add(morning)

            # Evening slot
            evening = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Same Monday
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_available=True
            )
            db.session.add(evening)
            db.session.commit()

            slots = ArtistAvailability.query.filter_by(
                artist_id=artist.id,
                day_of_week=0
            ).all()
            assert len(slots) == 2

    def test_artist_availability_is_available_false(self, client):
        """Test creating unavailable/blackout slots."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Blackout slot
            blackout = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=3,  # Thursday
                start_time=time(14, 0),
                end_time=time(16, 0),
                is_available=False  # Unavailable/blackout
            )
            db.session.add(blackout)
            db.session.commit()

            retrieved = ArtistAvailability.query.get(blackout.id)
            assert retrieved.is_available is False

    def test_artist_availability_repr(self, client):
        """Test the string representation of availability."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=0,  # Monday
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_available=True
            )
            db.session.add(availability)
            db.session.commit()

            repr_str = repr(availability)
            assert 'ArtistAvailability' in repr_str
            assert 'Monday' in repr_str
            assert '18:00' in repr_str
            assert '23:00' in repr_str
            assert 'Available' in repr_str

    def test_artist_availability_repr_unavailable(self, client):
        """Test string representation for unavailable slots."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=6,  # Sunday
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False
            )
            db.session.add(availability)
            db.session.commit()

            repr_str = repr(availability)
            assert 'Sunday' in repr_str
            assert 'Unavailable' in repr_str

    def test_artist_availability_multiple_artists(self, client):
        """Test that availability records are properly isolated per artist."""
        with app.app_context():
            artist1 = Artist(name='Artist 1', city='SF', state='CA')
            artist2 = Artist(name='Artist 2', city='LA', state='CA')
            db.session.add_all([artist1, artist2])
            db.session.commit()

            # Artist 1 available Monday 18:00-23:00
            avail1 = ArtistAvailability(
                artist_id=artist1.id,
                day_of_week=0,
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_available=True
            )

            # Artist 2 available Tuesday 20:00-22:00
            avail2 = ArtistAvailability(
                artist_id=artist2.id,
                day_of_week=1,
                start_time=time(20, 0),
                end_time=time(22, 0),
                is_available=True
            )
            db.session.add_all([avail1, avail2])
            db.session.commit()

            artist1_avail = ArtistAvailability.query.filter_by(artist_id=artist1.id).all()
            artist2_avail = ArtistAvailability.query.filter_by(artist_id=artist2.id).all()

            assert len(artist1_avail) == 1
            assert len(artist2_avail) == 1
            assert artist1_avail[0].day_of_week == 0
            assert artist2_avail[0].day_of_week == 1


class TestArtistAvailabilityException:
    """Test suite for ArtistAvailabilityException model."""

    @pytest.fixture(autouse=True)
    def setup(self, client):
        """Set up test database before each test."""
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_create_availability_exception(self, client):
        """Test creating a basic availability exception record."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),  # Christmas
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )
            db.session.add(exception)
            db.session.commit()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved is not None
            assert retrieved.artist_id == artist.id
            assert retrieved.exception_date == date(2026, 12, 25)
            assert retrieved.start_time == time(0, 0)
            assert retrieved.end_time == time(23, 59)
            assert retrieved.is_available is False
            assert retrieved.reason == 'Holiday'

    def test_availability_exception_default_is_available(self, client):
        """Test that is_available defaults to False for exceptions."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59)
            )
            db.session.add(exception)
            db.session.commit()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved.is_available is False

    def test_availability_exception_optional_reason(self, client):
        """Test that reason field is optional."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False
                # No reason provided
            )
            db.session.add(exception)
            db.session.commit()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved.reason is None

    def test_availability_exception_created_at_set(self, client):
        """Test that created_at is automatically set."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            before = datetime.utcnow()
            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )
            db.session.add(exception)
            db.session.commit()
            after = datetime.utcnow()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved.created_at is not None
            assert before <= retrieved.created_at <= after

    def test_availability_exception_unique_per_date(self, client):
        """Test that only one exception can exist per artist per date."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Create first exception for Christmas
            exception1 = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )
            db.session.add(exception1)
            db.session.commit()

            # Try to create duplicate exception for same date
            exception2 = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),  # Same date
                start_time=time(18, 0),  # Different time
                end_time=time(22, 0),
                is_available=True,
                reason='Tour'
            )
            db.session.add(exception2)
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_availability_exception_different_dates(self, client):
        """Test that different dates can have exceptions."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Christmas exception
            christmas = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )

            # New Year's exception
            new_year = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2027, 1, 1),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )
            db.session.add_all([christmas, new_year])
            db.session.commit()

            exceptions = ArtistAvailabilityException.query.filter_by(
                artist_id=artist.id
            ).all()
            assert len(exceptions) == 2

    def test_availability_exception_is_available_true(self, client):
        """Test creating exceptions that make artist available."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Exception where artist is available despite weekly schedule
            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_available=True,  # Available on this date
                reason='Special appearance'
            )
            db.session.add(exception)
            db.session.commit()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved.is_available is True

    def test_availability_exception_partial_day(self, client):
        """Test exceptions that apply to partial days."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            # Exception for afternoon only
            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(14, 0),
                end_time=time(16, 0),
                is_available=False,
                reason='Studio session'
            )
            db.session.add(exception)
            db.session.commit()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved.start_time == time(14, 0)
            assert retrieved.end_time == time(16, 0)

    def test_availability_exception_repr_available(self, client):
        """Test string representation for available exceptions."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_available=True,
                reason='Special show'
            )
            db.session.add(exception)
            db.session.commit()

            repr_str = repr(exception)
            assert 'ArtistAvailabilityException' in repr_str
            assert '2026-12-25' in repr_str
            assert '18:00' in repr_str
            assert '23:00' in repr_str
            assert 'Available' in repr_str
            assert 'Special show' in repr_str

    def test_availability_exception_repr_unavailable_no_reason(self, client):
        """Test string representation for unavailable exceptions without reason."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False
            )
            db.session.add(exception)
            db.session.commit()

            repr_str = repr(exception)
            assert 'ArtistAvailabilityException' in repr_str
            assert 'Unavailable' in repr_str
            assert '2026-12-25' in repr_str

    def test_availability_exception_multiple_artists(self, client):
        """Test that exceptions are properly isolated per artist."""
        with app.app_context():
            artist1 = Artist(name='Artist 1', city='SF', state='CA')
            artist2 = Artist(name='Artist 2', city='LA', state='CA')
            db.session.add_all([artist1, artist2])
            db.session.commit()

            # Artist 1 exception on Christmas
            exc1 = ArtistAvailabilityException(
                artist_id=artist1.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )

            # Artist 2 exception on New Year's
            exc2 = ArtistAvailabilityException(
                artist_id=artist2.id,
                exception_date=date(2027, 1, 1),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason='Holiday'
            )
            db.session.add_all([exc1, exc2])
            db.session.commit()

            artist1_exc = ArtistAvailabilityException.query.filter_by(
                artist_id=artist1.id
            ).all()
            artist2_exc = ArtistAvailabilityException.query.filter_by(
                artist_id=artist2.id
            ).all()

            assert len(artist1_exc) == 1
            assert len(artist2_exc) == 1
            assert artist1_exc[0].exception_date == date(2026, 12, 25)
            assert artist2_exc[0].exception_date == date(2027, 1, 1)

    def test_availability_exception_long_reason(self, client):
        """Test that reason field can store longer strings."""
        with app.app_context():
            artist = Artist(name='Test Artist', city='SF', state='CA')
            db.session.add(artist)
            db.session.commit()

            long_reason = 'Multi-city tour with travel days'
            exception = ArtistAvailabilityException(
                artist_id=artist.id,
                exception_date=date(2026, 12, 25),
                start_time=time(0, 0),
                end_time=time(23, 59),
                is_available=False,
                reason=long_reason
            )
            db.session.add(exception)
            db.session.commit()

            retrieved = ArtistAvailabilityException.query.get(exception.id)
            assert retrieved.reason == long_reason
