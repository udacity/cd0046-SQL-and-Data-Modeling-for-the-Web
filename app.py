#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from asyncio.windows_events import NULL
from contextlib import redirect_stderr
from doctest import FAIL_FAST
import sys
from email.policy import default
import json
from os import abort
from tracemalloc import start
from types import CoroutineType
from datetime import datetime
from wsgiref.handlers import format_date_time
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:442@localhost:5432/fyyur'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.String)

  @hybrid_property
  def artist_image_link(self):
    artist = Artist.query.get(self.artist_id)
    return artist.image_link
    
  @hybrid_property
  def venue_image_link(self):
    venue = Venue.query.get(self.artist_id)
    return venue.image_link

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.PickleType())
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', cascade="all, delete")
  
    @hybrid_property
    def upcoming_shows(self):
      list_of_shows = []

      for show in self.shows:
        now = datetime.now()

        if datetime.strptime(show.start_time, '%d/%m/%y %H:%M:%S') > now:
          list_of_shows.append(show)

      return list_of_shows

    @hybrid_property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)
      
    @hybrid_property
    def past_shows(self):
      list_of_shows = []

      for show in self.shows:
        now = datetime.now()

        if datetime.strptime(show.start_time, '%d/%m/%y %H:%M:%S') < now:
          list_of_shows.append(show)

      return list_of_shows

    @hybrid_property
    def past_shows_count(self):
      return len(self.past_shows)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    genres = db.Column(db.PickleType())
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', collection_class=list)

    @hybrid_property
    def upcoming_shows(self):
      list_of_shows = []

      for show in self.shows:
        now = datetime.now()

        if datetime.strptime(show.start_time, '%d/%m/%y %H:%M:%S') > now:
          list_of_shows.append(show)

      return list_of_shows

    @hybrid_property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    @hybrid_property
    def past_shows(self):
      list_of_shows = []

      for show in self.shows:
        now = datetime.now()

        if datetime.strptime(show.start_time, '%d/%m/%y %H:%M:%S') < now:
          list_of_shows.append(show)

      return list_of_shows
    
    @hybrid_property
    def past_shows_count(self):
      return len(self.past_shows)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  db_venues = Venue.query.all()
  areas = []
  
  for venue in db_venues:
    if len(areas) == 0:
      area = {
        'city': venue.city,
        'state': venue.state,
        'venues' : [venue]
      }
      areas.append(area)

    else:
      new_area={}
      for area in areas:
        if area['city'] == venue.city and area['state'] == venue.state:
          area['venues'].append(venue)
        
        else:
          new_area['city'] = venue.city
          new_area['state'] = venue.state

      if new_area:
        new_area['venues']= [venue]
        areas.append(new_area)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = search_term=request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try : 
    talent = request.form['seeking_talent']
    seeking_talent= False
    if talent == 'y':
      seeking_talent = True

    new_venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = [request.form['genres']],
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      website = request.form['website_link'],
      seeking_talent = seeking_talent,
      seeking_description = request.form['seeking_description']
    )

    # on successful db insert, flash success
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  error= False
  print('method called')
  try:
    print('deleting')
    print(venue_id)
    venue = Venue.query.get(int(venue_id))
    print(venue)
    db.session.delete(venue)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be deleted.')
  else:
    return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = search_term=request.form.get('search_term', '')
  result = Venue.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    talent = request.form['seeking_venue']
    seeking_venue= False
    
    if talent == 'y':
      seeking_venue = True
     
    seeking_description = request.form['seeking_description']

    if seeking_description is NULL:
      seeking_description = ''

    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = [request.form['genres']] 
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.seeking_talent = seeking_venue
    artist.seeking_description = seeking_description
    
    db.session.add(artist)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
    
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    talent = request.form['seeking_talent']
    seeking_talent= False
    seeking_description= ''
    if talent == 'y':
      seeking_talent = True
      seeking_description = request.form['seeking_description'] or ''

    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = [request.form['genres']] 
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.image_link = request.form['image_link']
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    
    db.session.add(venue)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
    
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue could not be updated.')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  print('creating artist')
  error = False
  try: 
    talent = request.form['seeking_venue']
    seeking_venue= False
    if talent == 'y':
      seeking_venue = True
    print(talent)
    new_artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = [request.form['genres']],
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      website = request.form['website_link'],
      seeking_venue = seeking_venue,
      seeking_description = request.form['seeking_description']
    )
    print(new_artist)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info)
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be listed.')
  else:
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    start_time = request.form['start_time']
    new_start_time = ''
    print(start_time)

    for character in start_time:
      if character == '-':
        new_start_time += '/'
      else:
        new_start_time += character

    new_start_time = new_start_time[2:]
    day = new_start_time[6:8]
    year = new_start_time[0:2]
    new_start_time = day + new_start_time[2:6] + year + new_start_time[8:]

    new_show = Show(
      artist_id = request.form['artist_id'],
      venue_id= request.form['venue_id'],
      start_time = new_start_time[2:]
    )
    db.session.add(new_show)
    db.session.commit()
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  else:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
