#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime
import dateutil.parser
import babel
import jinja2
from markupsafe import Markup
from flask import Flask, render_template, request, Response, flash, redirect, url_for

if not hasattr(jinja2, 'Markup'):
    jinja2.Markup = Markup

from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import or_
from forms import *
from extensions import db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import Artist, Venue, Show


def init_db():
    with app.app_context():
        db.create_all()


init_db()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


def _serialize_show(show):
  return {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'start_time': show.start_time.isoformat()
  }


def _serialize_venue_for_detail(venue):
  upcoming_shows = []
  past_shows = []
  current_time = datetime.now()

  for show in venue.shows:
    show_data = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
    }
    if show.start_time > current_time:
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  return {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres or [],
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website': venue.website_link,
      'facebook_link': venue.facebook_link,
      'seeking_talent': venue.seeking_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link,
      'upcoming_shows': upcoming_shows,
      'past_shows': past_shows,
      'upcoming_shows_count': len(upcoming_shows),
      'past_shows_count': len(past_shows),
  }


def _serialize_artist_for_detail(artist):
  upcoming_shows = []
  past_shows = []
  current_time = datetime.now()

  for show in artist.shows:
    show_data = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.isoformat()
    }
    if show.start_time > current_time:
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  return {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres or [],
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website_link,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
      'upcoming_shows': upcoming_shows,
      'past_shows': past_shows,
      'upcoming_shows_count': len(upcoming_shows),
      'past_shows_count': len(past_shows),
  }

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues_by_location = {}
  current_time = datetime.now()

  for venue in Venue.query.order_by(Venue.state, Venue.city, Venue.name).all():
    key = (venue.city, venue.state)
    if key not in venues_by_location:
      venues_by_location[key] = {
          'city': venue.city,
          'state': venue.state,
          'venues': []
      }

    upcoming_count = sum(1 for show in venue.shows if show.start_time > current_time)
    venues_by_location[key]['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': upcoming_count
    })

  areas = list(venues_by_location.values())
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '').strip()
  current_time = datetime.now()

  if search_term:
    venues = Venue.query.filter(
        or_(
            Venue.name.ilike(f'%{search_term}%'),
            Venue.city.ilike(f'%{search_term}%'),
            Venue.state.ilike(f'%{search_term}%'),
            Venue.address.ilike(f'%{search_term}%')
        )
    ).all()
  else:
    venues = []

  data = []
  for venue in venues:
    upcoming_count = sum(1 for show in venue.shows if show.start_time > current_time)
    data.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': upcoming_count
    })

  response = {
      'count': len(data),
      'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  data = _serialize_venue_for_detail(venue)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  if not form.name.data or not form.city.data or not form.state.data or not form.address.data or not form.genres.data:
    flash('Please complete all required venue fields.')
    return render_template('forms/new_venue.html', form=form)

  existing_venue = Venue.query.filter_by(
      name=form.name.data.strip(),
      city=form.city.data.strip(),
      state=form.state.data,
      address=form.address.data.strip()
  ).first()

  if existing_venue:
    flash('A venue with that name and address already exists.')
    return render_template('forms/new_venue.html', form=form)

  venue = Venue(
      name=form.name.data.strip(),
      city=form.city.data.strip(),
      state=form.state.data,
      address=form.address.data.strip(),
      phone=form.phone.data.strip() or None,
      image_link=form.image_link.data.strip() or None,
      facebook_link=form.facebook_link.data.strip() or None,
      website_link=form.website_link.data.strip() or None,
      seeking_talent=bool(form.seeking_talent.data),
      seeking_description=form.seeking_description.data.strip() or None,
      genres=list(form.genres.data)
  )

  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
    return redirect(url_for('show_venue', venue_id=venue.id))
  except Exception:
    db.session.rollback()
    flash('An error occurred. Venue could not be listed.')
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = [{
      'id': artist.id,
      'name': artist.name,
  } for artist in Artist.query.order_by(Artist.name).all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').strip()
  current_time = datetime.now()

  if search_term:
    artists = Artist.query.filter(
        or_(
            Artist.name.ilike(f'%{search_term}%'),
            Artist.city.ilike(f'%{search_term}%'),
            Artist.state.ilike(f'%{search_term}%')
        )
    ).all()
  else:
    artists = []

  data = []
  for artist in artists:
    upcoming_count = sum(1 for show in artist.shows if show.start_time > current_time)
    data.append({
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': upcoming_count
    })

  response = {
      'count': len(data),
      'data': data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  data = _serialize_artist_for_detail(artist)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  form.genres.data = artist.genres or []
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(request.form, obj=artist)

  if not form.name.data or not form.city.data or not form.state.data or not form.genres.data:
    flash('Please complete all required artist fields.')
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  artist.name = form.name.data.strip()
  artist.city = form.city.data.strip()
  artist.state = form.state.data
  artist.phone = form.phone.data.strip() or None
  artist.image_link = form.image_link.data.strip() or None
  artist.facebook_link = form.facebook_link.data.strip() or None
  artist.website_link = form.website_link.data.strip() or None
  artist.seeking_venue = bool(form.seeking_venue.data)
  artist.seeking_description = form.seeking_description.data.strip() or None
  artist.genres = list(form.genres.data)

  try:
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  except Exception:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated.')
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  form.genres.data = venue.genres or []
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form, obj=venue)

  if not form.name.data or not form.city.data or not form.state.data or not form.address.data or not form.genres.data:
    flash('Please complete all required venue fields.')
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  venue.name = form.name.data.strip()
  venue.city = form.city.data.strip()
  venue.state = form.state.data
  venue.address = form.address.data.strip()
  venue.phone = form.phone.data.strip() or None
  venue.image_link = form.image_link.data.strip() or None
  venue.facebook_link = form.facebook_link.data.strip() or None
  venue.website_link = form.website_link.data.strip() or None
  venue.seeking_talent = bool(form.seeking_talent.data)
  venue.seeking_description = form.seeking_description.data.strip() or None
  venue.genres = list(form.genres.data)

  try:
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  except Exception:
    db.session.rollback()
    flash('An error occurred. Venue could not be updated.')
    return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if not form.name.data or not form.city.data or not form.state.data or not form.genres.data:
    flash('Please complete all required artist fields.')
    return render_template('forms/new_artist.html', form=form)

  existing_artist = Artist.query.filter_by(name=form.name.data.strip()).first()
  if existing_artist:
    flash('An artist with that name already exists.')
    return render_template('forms/new_artist.html', form=form)

  artist = Artist(
      name=form.name.data.strip(),
      city=form.city.data.strip(),
      state=form.state.data,
      phone=form.phone.data.strip() or None,
      image_link=form.image_link.data.strip() or None,
      facebook_link=form.facebook_link.data.strip() or None,
      website_link=form.website_link.data.strip() or None,
      seeking_venue=bool(form.seeking_venue.data),
      seeking_description=form.seeking_description.data.strip() or None,
      genres=list(form.genres.data)
  )

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist.id))
  except Exception:
    db.session.rollback()
    flash('An error occurred. Artist could not be listed.')
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = [_serialize_show(show) for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  if not form.artist_id.data or not form.venue_id.data or not form.start_time.data:
    flash('Please complete all required show fields.')
    return render_template('forms/new_show.html', form=form)

  artist = Artist.query.get(int(form.artist_id.data))
  venue = Venue.query.get(int(form.venue_id.data))

  if not artist or not venue:
    flash('Please choose a valid artist and venue.')
    return render_template('forms/new_show.html', form=form)

  show = Show(
      artist_id=artist.id,
      venue_id=venue.id,
      start_time=form.start_time.data
  )

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  except Exception:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
