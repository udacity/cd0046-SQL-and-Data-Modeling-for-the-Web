#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging,sys
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
migrate= Migrate(app, db)

venue_genre= db.Table ('venue_genre',
db.Column('genre_id',db.Integer,db.ForeignKey ('Genre.id'), primary_key=True),
db.Column('venue_id',db.Integer,db.ForeignKey ('Venue.id'), primary_key=True)
)

artist_genre= db.Table ('artist_genre',
db.Column('genre_id',db.Integer,db.ForeignKey ('Genre.id'), primary_key=True),
db.Column('artist_id',db.Integer,db.ForeignKey ('Artist.id'), primary_key=True)
)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres= db.relationship ('Genre',secondary= venue_genre, backref= 'venue',lazy=True)
    website_link=db.Column(db.String(500))
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column( db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Genre(db.Model):
  __tablename__ ='Genre'
  id = db.Column(db.Integer, primary_key= True)
  name = db.Column(db.String,nullable= False)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link=db.Column(db.String(500))
    genres= db.relationship ('Genre',secondary= artist_genre, backref= 'artist',lazy=True)  
    facebook_link = db.Column(db.String(120))
    website_link=db.Column(db.String(500))
    seeking_venue=db.Column(db.Boolean())
    seeking_description=db.Column(db.String(500))
    image_link = db.Column(db.String(500))

class Show(db.Model):
    __tablename__ ='Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, nullable=False)
    venue_id =  db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
  data = []

  fetched_city_and_states = db.session.query(Venue.city, Venue.state).distinct().all()

  for city_and_state_row in fetched_city_and_states:
    data_item = {
      "city": city_and_state_row.city,
      "state": city_and_state_row. state,
      "venues": []
    }

    fetched_venues = db.session \
      .query(Venue.id, Venue.name) \
      .filter(Venue.city == city_and_state_row.city and Venue.state == city_and_state_row.state) \
      .all()

    for venue_row in fetched_venues:
      fetched_num_upcoming_shows = db.session \
        .query(db.func.count(Show.id)) \
        .filter(Show.venue_id == venue_row.id) \
        .filter(Show.start_time >= datetime.now()) \
        .one()[0]
      
      data_item["venues"].append({
        "id": venue_row.id,
        "name": venue_row.name,
        "num_upcoming_shows": fetched_num_upcoming_shows
      })
    
    data.append(data_item)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_venue=request.form.get('search_term', '')
  venues= Venue.query.filter(Venue.name.ilike('%{}%'.format(search_venue)))
  response = {
    "count":venues.count(),
    "data":[]
  }
  for venue in venues:
    num_upcoming_shows= Show.query.filter(Show.venue_id==venue.id, Show.start_time > datetime.now()).count() 
    row_data ={
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows":num_upcoming_shows
    }
    response["data"].append(row_data)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue= Venue.query.get(venue_id)
  genres=[]
  for genre in venue.genres :
    genres.append (genre.name)

  past_shows_count= db.session.query(db.func.count()) \
    .filter(Show.venue_id==venue_id) \
    .filter(Show.start_time < datetime.now()).one()[0]
  upcoming_shows_count= db.session.query(db.func.count()) \
    .filter(Show.venue_id==venue_id) \
    .filter(Show.start_time > datetime.now()).one()[0]

  data={"id":venue.id,
        "name":venue.name,
        "genres":genres,
        "address":venue.address,
        "city":venue.city,
        "state":venue.state,
        "phone":venue.phone,
        "website_link":venue.website_link,
        "facebook_link":venue.facebook_link,
        "seeking_talent":venue.seeking_talent,
        "seeking_description":venue.seeking_description,
        "image_link":venue.image_link,
        "past_shows_count" :past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
        "past_shows" :[],
        "upcoming_shows":[]
        } 

  fetched_past_shows=Show.query.filter(Show.venue_id == venue_id,Show.start_time < datetime.now())
  for show in fetched_past_shows :
    artist= Artist.query.get(show.artist_id)
    data_item_past_show = {
      "artist_id":show.artist_id,
      "artist_name": artist.name,
      "artist_image_link" :artist.image_link,
      "start_time":str(show.start_time)
    }
    data["past_shows"].append(data_item_past_show)

  fetched_upcoming_shows=Show.query.filter(Show.venue_id == venue_id,Show.start_time > datetime.now())
  for show in fetched_upcoming_shows :
    artist= Artist.query.get(show.artist_id)
    data_item_past_show = {
      "artist_id":show.artist_id,
      "artist_name": artist.name,
      "artist_image_link" :artist.image_link,
      "start_time":str(show.start_time)
    }
    data["upcoming_shows"].append(data_item_past_show)

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
  try:
    venue= Venue(name=request.form['name'],
                  city= request.form['city'] ,
                  state= request.form['state'],
                  address=request.form['address'],
                  phone=request.form['phone'],
                  image_link=request.form['image_link'],
                  facebook_link= request.form['facebook_link'],
                  genres=[],
                  website_link= request.form['website_link'],
                  seeking_talent= request.form.get('seeking_talent') == 'y',
                  seeking_description= request.form['seeking_description']
                  )
    for genre in request.form.getlist('genres'):
      fetched_genre = Genre.query.filter_by(name=genre).one()
      venue.genres.append(fetched_genre)

 
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!','info')
  except Exception as e:
    print(e)
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Venue ' + request.form['name'] +' could not be listed.', 'error')
  finally:
    db.session.close()

  # TODO: modify data to be the data object returned from db insertion

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venue_name=Venue.query.get(venue_id).name
  try:
    db.session.query(venue_genre).filter(venue_genre.c.venue_id==venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    Show.query.filter_by(venue_id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_name+ ' was successfully deleted!','info')
  except Exception as e :
    print(e)
    db.session.rollback()
    flash('Venue ' + venue_name +' could not be deleted.','error')
    return jsonify({ 'success': False })
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({ 'success': True })
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_artist=request.form.get('search_term', '')
  artists= Artist.query.filter(Artist.name.ilike('%{}%'.format(search_artist)))
  response = {
    "count":artists.count(),
    "data":[]
  }
  for artist in artists:
    num_upcoming_shows= Show.query.filter(Show.artist_id==artist.id, Show.start_time > datetime.now()).count() 
    row_data ={
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows":num_upcoming_shows
    }
    response["data"].append(row_data)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 
  artist=Artist.query.get(artist_id)
  genres = []
  for genre in artist.genres :
    genres.append (genre.name)

  past_shows=[]
  pshows = Show.query.filter(Show.artist_id == artist_id , Show.start_time <= datetime.now())
  for show in pshows:
    venue=Venue.query.get(show.venue_id)
    past_shows.append ({"venue_id": show.venue_id,
                      "venue_name": venue.name,
                      "venue_image_link": venue.image_link,
                      "start_time": str(show.start_time) })
  
  upcoming_shows=[]
  ushows = Show.query.filter(Show.artist_id == artist_id , Show.start_time > datetime.now())
  for show in ushows:
    venue=Venue.query.get(show.venue_id)
    upcoming_shows.append ({"venue_id": show.venue_id,
                            "venue_name": venue.name,
                            "venue_image_link": venue.image_link,
                            "start_time": str(show.start_time) })
   
  data= {
     "id":artist.id,
     "name":artist.name,
     "genres":genres, 
     "city":artist.city,
     "state":artist.state,
     "phone":artist.phone,
     "seeking_venue":artist.seeking_venue,
     "seeking_description": artist.seeking_description,
     "image_link":artist.image_link,
     "past_shows":past_shows,
     "upcoming_shows":upcoming_shows,
     "past_shows_count":pshows.count(),
     "upcoming_shows_count":ushows.count()
  }

  print (data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist=Artist.query.get(artist_id)
  genre_list=[]
  for genre in artist.genres:
    genre_list.append(genre.name)

  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    phone=artist.phone,
    image_link=artist.image_link,
    genres=genre_list,
    facebook_link=artist.facebook_link,
    website_link=artist.website_link,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist=Artist.query.get(artist_id)
    genre_list=[]
    for genre in request.form.getlist('genres'):
      genre_list.append(Genre.query.filter_by(name=genre).one())

    artist.name = request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    artist.image_link=request.form['image_link']
    artist.genres=genre_list
    artist.facebook_link=request.form['facebook_link']
    artist.website_link=request.form['website_link']
    artist.seeking_venue=request.form.get('seeking_venue')=='y'
    artist.seeking_description=request.form['seeking_description']

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(e)
    flash('Artist ' + request.form['name'] + ' was could not be listed!','error')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)

  genre_list = []
  for genre in venue.genres:
    genre_list.append(genre.name)

  form = VenueForm(
    name=venue.name,
    city = venue.city,
    state= venue.state,
    address=venue.address,
    phone=venue.phone,
    image_link=venue.image_link,
    facebook_link=venue.facebook_link,
    genres=genre_list,
    website_link=venue.website_link,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
    )
 
   # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
#   # TODO: take values from the form submitted, and update existing
#   # venue record with ID <venue_id> using the new attributes
  venue=Venue.query.get(venue_id)
  
  try:
    venue.name=request.form['name']
    venue.city= request.form['city'] 
    venue.state= request.form['state']
    venue.address=request.form['address']
    venue.phone=request.form['phone']
    venue.image_link=request.form['image_link']
    venue.facebook_link= request.form['facebook_link']
    venue.genres=[]
    venue.website_link= request.form['website_link']
    venue.seeking_talent= request.form.get('seeking_talent') == 'y'
    venue.seeking_description= request.form['seeking_description']

    genre_list = []
    genre_list= request.form.getlist('genres')
    for genre in genre_list:
      venue.genres.append(Genre.query.filter_by(name = genre).one()) 

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(e)
    flash('Venue ' + request.form['name'] + ' was could not be listed!','error')
  finally:
    db.session.close()

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

  try:
    artist=Artist(
    name=request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    image_link=request.form['image_link'],
    genres= [],
    facebook_link = request.form['facebook_link'],
    website_link=request.form['website_link'],
    seeking_venue=request.form.get('seeking_venue')=='y',
    seeking_description=request.form['seeking_description'])

    genre_list=request.form.getlist('genres')
    for genre in genre_list :
      artist.genres.append(Genre.query.filter_by (name=genre).one())
      
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(e)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data= []
  shows =Show.query.all() 
  for show in shows :
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id":show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link":Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time) })

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
  try:

    show=Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time'])
    
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!','info')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Show could not be listed.','error')
  finally:
    db.session.close()
  # on successful db insert, flash success
  
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
