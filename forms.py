from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TimeField, DateField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, Optional, Regexp, ValidationError, NumberRange
from forms_constants import STATE_CHOICES, GENRE_CHOICES

# US Phone number regex: accepts formats like (123) 456-7890, 123-456-7890, 1234567890, +1-123-456-7890
US_PHONE_REGEX = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'

class OptionalURL(URL):
    """URL validator that allows empty fields."""
    def __call__(self, form, field):
        if field.data:  # Only validate if field has data
            super().__call__(form, field)

class ShowForm(FlaskForm):
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        coerce=int
    )
    venue_id = SelectField(
        'venue_id',
        validators=[DataRequired()],
        coerce=int
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        format='%Y-%m-%d %H:%M'
    )
    end_time = DateTimeField(
        'end_time',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M'
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=STATE_CHOICES
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[Optional(), Regexp(
            US_PHONE_REGEX,
            message='Phone number must be a valid US phone number (e.g., 123-456-7890 or (123) 456-7890)'
        )]
    )
    image_link = StringField(
        'image_link',
        validators=[OptionalURL(require_tld=True, message='Image link must be a valid URL with a domain')]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=GENRE_CHOICES
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[OptionalURL(require_tld=True, message='Facebook link must be a valid URL with a domain')]
    )
    website_link = StringField(
        'website_link',
        validators=[OptionalURL(require_tld=True, message='Website link must be a valid URL with a domain')]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=STATE_CHOICES
    )
    phone = StringField(
        'phone',
        validators=[Optional(), Regexp(
            US_PHONE_REGEX,
            message='Phone number must be a valid US phone number (e.g., 123-456-7890 or (123) 456-7890)'
        )]
    )
    image_link = StringField(
        'image_link',
        validators=[OptionalURL(require_tld=True, message='Image link must be a valid URL with a domain')]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=GENRE_CHOICES
     )
    facebook_link = StringField(
        'facebook_link',
        validators=[OptionalURL(require_tld=True, message='Facebook link must be a valid URL with a domain')]
     )

    website_link = StringField(
        'website_link',
        validators=[OptionalURL(require_tld=True, message='Website link must be a valid URL with a domain')]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )


class ArtistAvailabilityForm(FlaskForm):
    """Form for setting recurring weekly artist availability."""
    day_of_week = SelectField(
        'day_of_week',
        validators=[DataRequired()],
        choices=[
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday')
        ]
    )
    start_time = TimeField(
        'start_time',
        validators=[DataRequired()],
        format='%H:%M'
    )
    end_time = TimeField(
        'end_time',
        validators=[DataRequired()],
        format='%H:%M'
    )
    is_available = BooleanField(
        'is_available',
        default=True
    )


class ArtistAvailabilityExceptionForm(FlaskForm):
    """Form for setting date-specific availability exceptions."""
    exception_date = DateField(
        'exception_date',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    start_time = TimeField(
        'start_time',
        validators=[DataRequired()],
        format='%H:%M'
    )
    end_time = TimeField(
        'end_time',
        validators=[DataRequired()],
        format='%H:%M'
    )
    is_available = BooleanField(
        'is_available',
        default=False
    )
    reason = StringField(
        'reason',
        validators=[Optional()],
        description='e.g., Holiday, Tour, Studio Session'
    )


class AlbumForm(FlaskForm):
    """Form for creating and editing albums."""
    title = StringField(
        'title',
        validators=[DataRequired()],
        description='Album title'
    )
    release_date = DateField(
        'release_date',
        validators=[Optional()],
        format='%Y-%m-%d',
        description='Album release date (YYYY-MM-DD)'
    )
    description = TextAreaField(
        'description',
        validators=[Optional()],
        description='Album description or notes'
    )
    image_link = StringField(
        'image_link',
        validators=[OptionalURL(require_tld=True, message='Album cover must be a valid URL with a domain')],
        description='URL to album cover art'
    )
    spotify_link = StringField(
        'spotify_link',
        validators=[Optional()],
        description='Spotify album URL (must start with https://open.spotify.com/)'
    )
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        coerce=int,
        description='Artist'
    )


class SongForm(FlaskForm):
    """Form for creating and editing songs."""
    title = StringField(
        'title',
        validators=[DataRequired()],
        description='Song title'
    )
    track_number = IntegerField(
        'track_number',
        validators=[Optional(), NumberRange(min=0)],
        description='Track number on album'
    )
    duration = IntegerField(
        'duration',
        validators=[Optional(), NumberRange(min=0)],
        description='Duration in seconds'
    )
    genre = StringField(
        'genre',
        validators=[Optional()],
        description='Song genre'
    )
    spotify_link = StringField(
        'spotify_link',
        validators=[Optional()],
        description='Spotify track URL (must start with https://open.spotify.com/)'
    )



class AlbumForm(FlaskForm):
    """Form for creating and editing albums."""
    title = StringField(
        'title',
        validators=[DataRequired()],
        description='Album title'
    )
    release_date = DateField(
        'release_date',
        validators=[Optional()],
        format='%Y-%m-%d',
        description='Album release date (YYYY-MM-DD)'
    )
    description = TextAreaField(
        'description',
        validators=[Optional()],
        description='Album description or notes'
    )
    image_link = StringField(
        'image_link',
        validators=[OptionalURL(require_tld=True, message='Album cover must be a valid URL with a domain')],
        description='URL to album cover art'
    )
    spotify_link = StringField(
        'spotify_link',
        validators=[Optional()],
        description='Spotify album URL (must start with https://open.spotify.com/)'
    )
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        coerce=int,
        description='Artist'
    )


class SongForm(FlaskForm):
    """Form for creating and editing songs."""
    title = StringField(
        'title',
        validators=[DataRequired()],
        description='Song title'
    )
    track_number = IntegerField(
        'track_number',
        validators=[Optional(), NumberRange(min=0)],
        description='Track number on album'
    )
    duration = IntegerField(
        'duration',
        validators=[Optional(), NumberRange(min=0)],
        description='Duration in seconds'
    )
    genre = StringField(
        'genre',
        validators=[Optional()],
        description='Song genre'
    )
    spotify_link = StringField(
        'spotify_link',
        validators=[Optional()],
        description='Spotify track URL (must start with https://open.spotify.com/)'
    )
