#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import VenueForm, ArtistForm, ShowForm
from datetime import datetime
from models import Venue, Artist, Show, setup_db
from constants import HOME_PAGE_TEMPLATE, NEW_VENUE_TEMPLATE, ARTISTS_PAGE_TEMPLATE, \
  SEARCH_ARTISTS_TEMPLATE, SHOW_ARTIST_TEMPLATE, SHOWS_TEMPLATE, SHOW_VENUE_TEMPLATE, ERROR_404, \
  ERROR_500, VENUES_TEMPLATE, SEARCH_VENUES_TEMPLATE, EDIT_VENUE_TEMPLATE, EDIT_ARTIST_TEMPLATE, NEW_ARTIST_TEMPLATE, NEW_SHOW_TEMPLATE
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = setup_db(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, date_format='medium'):
  date = dateutil.parser.parse(value)
  if date_format == 'full':
      date_format="EEEE MMMM, d, y 'at' h:mma"
  elif date_format == 'medium':
      date_format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, date_format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template(HOME_PAGE_TEMPLATE)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data_areas = []
  locations = Venue.query.with_entities(Venue.city, Venue.state)\
        .group_by(Venue.city, Venue.state).all()
  
  for location in locations:
    venue_items = []
    venues = Venue.query.filter_by(city=location.city).filter_by(state=location.state).all()

    for venue in venues:
      upcoming_shows = db.session \
                    .query(Show) \
                    .filter(Show.venue_id == venue.id, Show.start_time > datetime.now()) \
                    .all()

      venue_items.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': upcoming_shows.count
      })

    data_areas.append({
            'city': location.city,
            'state': location.state,
            'venues': venue_items
        })

  return render_template(VENUES_TEMPLATE, areas=data_areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.with_entities(Venue.id, Venue.name)\
          .filter(Venue.name.ilike(f'%{search_term}%'))

  data_venues = []
  for venue in venues:
    upcoming_shows = db.session \
            .query(Show) \
            .filter(Show.venue_id == venue.id) \
            .filter(Show.start_time > datetime.now()) \
            .all()

    data_venues.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': upcoming_shows.count
    })

  results = {
    "count": venues.count(),
    "data": data_venues
  }
  return render_template(SEARCH_VENUES_TEMPLATE, results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data_venue = db.session.get(Venue, venue_id)

  upcoming_shows = Show.query \
        .filter(Show.venue_id == venue_id) \
        .filter(Show.start_time > datetime.now()) \
        .all()
  
  if len(upcoming_shows) > 0:
    data_upcoming_shows = []

    for upcoming_show in upcoming_shows:
      artist = db.session.get(Artist, upcoming_show.artist_id)

      data_upcoming_shows.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(upcoming_show.start_time),
    })

    data_venue.upcoming_shows = data_upcoming_shows
    data_venue.upcoming_shows_count = data_upcoming_shows.count

  past_shows = Show.query \
        .filter(Show.venue_id == venue_id, Show.start_time < datetime.now()) \
        .all()

  if len(past_shows) > 0:
    data_past_shows = []

    for past_show in past_shows:
      artist = db.session.get(Artist, past_show.artist_id)

      data_past_shows.append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(past_show.start_time),
      })

    # Add shows data
    data_venue.past_shows = data_past_shows
    data_venue.past_shows_count = data_past_shows.count

  return render_template(SHOW_VENUE_TEMPLATE, venue=data_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template(NEW_VENUE_TEMPLATE, form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try: 
    venue = Venue(name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      seeking_talent = True if 'seeking_talent' in request.form else False,
      seeking_description = request.form['seeking_description'])

    db.session.add(venue)
    db.session.commit()
  except Exception: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.', 'danger ')
  else: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!', 'success')
  return render_template(HOME_PAGE_TEMPLATE)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(sys.exc_info())
    print(e)
    return render_template(ERROR_500, error=str(e))
  finally: 
    db.session.close()

  if error:
    flash('An error occurred. Venue could not be deleted.', 'danger')
  if not error:
    flash('Venue was successfully deleted!', 'success')

  return redirect(url_for('home'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data_artists = []

  artists = Artist.query \
        .with_entities(Artist.id, Artist.name) \
        .order_by('id') \
        .all()

  for artist in artists:
    data_artists.append({
        'id': artist.id,
        'name': artist.name,
    })

  return render_template(ARTISTS_PAGE_TEMPLATE, artists=data_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  
  artists = Artist.query.with_entities(Artist.id, Artist.name)\
          .filter(Artist.name.ilike(f'%{search_term}%'))
  
  data_artists = []
  for artist in artists:
    upcoming_shows = db.session.query(Show)\
            .filter(Show.artist_id == artist.id, Show.start_time > datetime.now())\
            .all()

    data_artists.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': upcoming_shows.count
    })

  response = {
    "count": artists.count(),
    "data": data_artists
  }
  return render_template(SEARCH_ARTISTS_TEMPLATE, results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data_artist = db.session.get(Artist, artist_id)

  upcoming_shows = Show.query \
        .filter(Show.artist_id == artist_id, Show.start_time > datetime.now()) \
        .all()
  
  if len(upcoming_shows) > 0:
    data_upcoming_shows = []

    for upcoming_show in upcoming_shows:
      venue = db.session.get(Venue, upcoming_show.venue_id)

      data_upcoming_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(upcoming_show.start_time),
      })

    data_artist.upcoming_shows = data_upcoming_shows
    data_artist.upcoming_shows_count = data_upcoming_shows.count

  past_shows = Show.query \
        .filter(Show.artist_id == artist_id) \
        .filter(Show.start_time < datetime.now()) \
        .all()

  if len(past_shows) > 0:
    data_past_shows = []

    for past_show in past_shows:
      venue = db.session.get(Venue, past_show.venue_id)

      data_past_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(past_show.start_time),
      })

    data_artist.past_shows = data_past_shows
    data_artist.past_shows_count = data_past_shows.count

  return render_template(SHOW_ARTIST_TEMPLATE, artist=data_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.get(Artist, artist_id)
  form = ArtistForm()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template(EDIT_ARTIST_TEMPLATE, form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try: 
    artist = db.session.get(Artist, artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
  except Exception: 
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.get(Venue, venue_id)

  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  
  return render_template(EDIT_VENUE_TEMPLATE, form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try: 
    venue = db.session.get(Venue, venue_id)

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    
    db.session.commit()
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error:
    flash(
      'An error occurred. Venue ' + request.form['name'] + ' could not be updated.',
      'danger'
    )
  if not error:
    flash(
      'Venue ' + request.form['name'] + ' was successfully updated!',
      'success'
    )

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template(NEW_ARTIST_TEMPLATE, form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try: 
    artist = Artist(name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      seeking_venue = True if 'seeking_venue' in request.form else False ,
      seeking_description = request.form['seeking_description'])

    db.session.add(artist)
    db.session.commit()
  except Exception: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
  return render_template(HOME_PAGE_TEMPLATE)


#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []

  shows = db.session \
      .query(
        Venue.name,
        Artist.name,
        Artist.image_link,
        Show.venue_id,
        Show.artist_id,
        Show.start_time
      ) \
      .filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id)

  for show in shows:
    data.append({
      'venue_name': show[0],
      'artist_name': show[1],
      'artist_image_link': show[2],
      'venue_id': show[3],
      'artist_id': show[4],
      'start_time': str(show[5])
    })

  return render_template(SHOWS_TEMPLATE, shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template(NEW_SHOW_TEMPLATE, form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    show = Show(start_time=request.form['start_time'],
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'])

    db.session.add(show)
    db.session.commit()
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show could not be listed.', 'danger')
  else:
    flash('Show was successfully listed!', 'success')

  return render_template(HOME_PAGE_TEMPLATE)

@app.errorhandler(404)
def not_found_error(error):
    return render_template(ERROR_404), 404

@app.errorhandler(500)
def server_error(error):
    return render_template(ERROR_500), 500


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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
