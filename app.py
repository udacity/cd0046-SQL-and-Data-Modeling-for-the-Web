#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

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
  # *DONE: replace with real venues data.
  data = []
  items = Venue.query.distinct(Venue.city, Venue.state).all()
  for item in items:
    venueObj = {
      "city": item.city,
      "state": item.state
    }
    filteredVenues = Venue.query.filter_by(city=item.city, state=item.state).all()
    formatted_venues = []
    for venue in filteredVenues:
    # *num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
      formatted_venue = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
      }
      formatted_venues.append(formatted_venue)
    venueObj["venues"] = formatted_venues
    data.append(venueObj)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # *DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # *seach for Hop should return "The Musical Hop".
  # *search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={}
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(
    Venue.name.ilike(f"%{search_term}%")
  ).all()
  response["count"] = len(venues)
  response["data"] = []
  for venue in venues:
    venueObj = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
    }
    response["data"].append(venueObj)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # *shows the venue page with the given venue_id
  # *DONE: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  past_shows_query = db.session.query(Show).join(Artist).filter(
      Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(
      Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []

  for past_show in past_shows_query:
    pastShowObj = {
      "artist_id": past_show.artist_id,
      "artist_name": past_show.artist.name,
      "artist_image_link": past_show.artist.image_link,
      "start_time": past_show.start_time.strftime('%d/%m/%Y %H:%M:%S')
    }
    past_shows.append(pastShowObj)
  setattr(venue, "past_shows", past_shows)    
  setattr(venue,"past_shows_count", len(past_shows))

  for upcoming_show in upcoming_shows_query:
    upcomingShowObj = {
      "artist_id": upcoming_show.artist_id,
      "artist_name": upcoming_show.artist.name,
      "artist_image_link": upcoming_show.artist.image_link,
      "start_time": upcoming_show.start_time.strftime('%d/%m/%Y %H:%M:%S')
    }
    upcoming_shows.append(upcomingShowObj)
  setattr(venue, "upcoming_shows", upcoming_shows)    
  setattr(venue,"upcoming_shows_count", len(upcoming_shows))

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      genres = form.genres.data
      website = form.website_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
  # *DONE: insert form data as a new Venue record in the db, instead
  # *DONE: modify data to be the data object returned from db insertion
      venue = Venue(name=name, city=city, state=state, address=address,
                    phone=phone, genres=genres, facebook_link=facebook_link, website=website,
                    image_link=image_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print('Caught Exception: ', e)
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
  # *DONE: on unsuccessful db insert, flash an error.
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be listed.')
  else:
  # *on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # *DONE: Completed this endpoint for taking a venue_id, and using
  # *SQLAlchemy ORM to delete a record, Handlng cases where the session commit could fail by rolling back.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue " + venue.name + " was deleted successfully!")
  except Exception as e:
    db.session.rollback()
    print('Caught Exception: ', e)
    print(sys.exc_info())
    flash("An error occured as venue was not deleted successfully.")
  finally:
    db.session.close()
  # !BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # !clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # *DONE: replaced artists with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # *DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # *seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # *search for "band" should return "The Wild Sax Band".
  response={}
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%")
  ).all()
  response["count"] = len(artists)
  response["data"] = []
  for artist in artists:
    artistObj = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.now()).count()
    }
    response["data"].append(artistObj)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # *shows the artist page with the given artist_id
  # *DONE: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  past_shows_query = db.session.query(Show).join(Venue).filter(
      Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(
      Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []

  for past_show in past_shows_query:
    pastShowObj = {
      "venue_id": past_show.venue_id,
      "venue_name": past_show.venue.name,
      "venue_image_link": past_show.venue.image_link,
      "start_time": past_show.start_time.strftime('%d/%m/%Y %H:%M:%S')
    }
    past_shows.append(pastShowObj)

  setattr(artist, "past_shows", past_shows)
  setattr(artist, "past_shows_count", len(past_shows))

  for upcoming_show in upcoming_shows_query:
    upcomingShowObj = {
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.venue.name,
      "venue_image_link": upcoming_show.venue.image_link,
      "start_time": upcoming_show.start_time.strftime('%d/%m/%Y %H:%M:%S')
    }
    upcoming_shows.append(upcomingShowObj)

  setattr(artist, "upcoming_shows", upcoming_shows)
  setattr(artist, "upcoming_shows_count", len(upcoming_shows))

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # *DONE: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.genres.data = artist.genres
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)
  try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      genres = form.genres.data
      website = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      artist = Artist(name=name, city=city, state=state, phone=phone,
                      image_link=image_link, facebook_link=facebook_link,
                      genres=genres, website=website, seeking_venue=seeking_venue,
                      seeking_description=seeking_description)
  # *DONE: take values from the form submitted, and update existing
  # *artist record with ID <artist_id> using the new attributes
      db.session.add(artist)
      db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print('Caught Exception: ', e)
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
  # *DONE: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be edited.')
  else:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # *DONE: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.genres.data = venue.genres
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # *DONE: take values from the form submitted, and update existing
  # *venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm(request.form)
  try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      genres = form.genres.data
      website = form.website_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
      venue = Venue(name=name, city=city, state=state, address=address,
                    phone=phone, genres=genres, facebook_link=facebook_link, website=website,
                    image_link=image_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
      db.session.add(venue)
      db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print('Caught Exception: ', e)
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
  # *DONE: on unsuccessful db insert, flash an error.
      flash('An error occurred. Venue ' +
            request.form['name'] + ' could not be editted.')
  else:
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully editted!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # *called upon submitting the new artist listing form
  error = False
  form = ArtistForm(request.form)
  try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      genres = form.genres.data
      website = form.website_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
  # *DONE: insert form data as a new Venue record in the db, instead
  # *DONE: modify data to be the data object returned from db insertion
      artist = Artist(name=name, city=city, state=state, phone=phone,
                      image_link=image_link, facebook_link=facebook_link,
                      genres=genres, website=website, seeking_venue=seeking_venue,
                      seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print('Caught Exception: ', e)
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
  # *DONE: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' +
            request.form['name'] + ' could not be listed.')
  else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # *displays list of shows at /shows
  # *DONE: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    formattedShow = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y/%m/%d %H:%M:%S"),
    }
    data.append(formattedShow)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # *called to create new shows in the db, upon submitting new show listing form
  error = False
  form = ShowForm(request.form)
  try:
      start_time = form.start_time.data
      artist_id = form.artist_id.data
      venue_id = form.venue_id.data
      show = Show(artist_id=artist_id, venue_id=venue_id,
                  start_time=start_time)
  # *DONE: insert form data as a new Show record in the db
      db.session.add(show)
      db.session.commit()
  except Exception as e:
      error = True
      db.session.rollback()
      print('Caught Exception: ', e)
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
  # *DONE: on unsuccessful db insert, flash an error.
      flash('An error occurred. Show could not be listed.')
  else:
  # *on successful db insert, flash success
      flash('Show was successfully listed!')
  return render_template('pages/home.html')

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
