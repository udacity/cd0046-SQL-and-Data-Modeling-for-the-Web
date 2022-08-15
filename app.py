#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser 
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from models import (app, db, Venue, Shows, Artist)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, FlaskForm, CSRFProtect
from forms import *
from datetime import datetime	
from sqlalchemy import desc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
csrf = CSRFProtect()
csrf.init_app(app)
moment = Moment(app)
db.init_app(app) 
# TODO: connect to a local postgresql database


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

# ---------------------------------------------------------------------------#
#  Search engine function to avoid code repetition
# ---------------------------------------------------------------------------#

def search(entity, search_term):
    if search_term != '':
        try:
            search_results=entity.query.filter (entity.name.ilike('%'+search_term+'%')).order_by('id').all()
            if len(search_results)==0:
                flash(f'Your search: "{search_term}" has no matching records.')
            response={
                "count": len(search_results),
                "data": [{
                     "id":search_result.id,
                     "name":search_result.name,
                    "num_of_upcoming_shows": Shows.query.filter_by(venue_id=search_result.id).count()
                } for search_result in search_results]
                        }
        except Exception as e:
            flash(f'Error: {e}')
    else:
        response ={
            'count':0,
            'data':[{}]
        }
        flash(f'Please enter a valid search term.')
    return response

#--------------------------------#
#gets recently added venue and artist from the db
#---------------------------------#
def get_recents():
    artists_recent = Artist.query.order_by(desc('created_date')).limit(10).all()
    venues_recent = Venue.query.order_by(desc('created_date')).limit(10).all()

    recent_artists = []
    recent_venues = []

    for artist in artists_recent:
        recent_artists.append({
            'id':artist.id,
            'name': artist.name,
            'created_date': artist.created_date
        })

    for venue in venues_recent:
        recent_venues.append({
            'id':venue.id,
            'name': venue.name,
            'created_date': venue.created_date
        })
    return recent_artists, recent_venues

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    recent_artists, recent_venues = get_recents()
    return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    db_data = []
    venueData = Venue.query.all()
    for venue in venueData:
        data = {}
        cities = []
        for city in db_data:
            cities.append(city['city'])
        if venue.city not in cities:
            data['city'] = venue.city
            data['state'] = venue.state
            data['venues'] = [{'id': venue.id, 'name': venue.name}]
            db_data.append(data)
        else:
            cityIndex = cities.index(venue.city)
            venueItem = {'id': venue.id, 'name': venue.name}
            db_data[cityIndex]['venues'].append(venueItem)
    db.session.close()
  
    return render_template('pages/venues.html', areas=db_data)
  
  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  real_response = search(Venue, search_term)
  return render_template('pages/search_venues.html', results=real_response, search_term=search_term)
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  no_show = False
  venue_details=Venue.query.filter_by(id=venue_id).\
  join(Shows, Shows.venue_id==Venue.id).\
  join(Artist, Artist.id==Shows.artist_id).\
  add_columns(Artist.id, Artist.name, Artist.image_link, Shows.start_time)\
  .all()	
       	
  past_shows =[]	
  upcoming_shows=[]	      	
  if venue_details:	
    for detail in venue_details:	
        if detail.start_time < datetime.today():	
            past_shows.append({	
                "artist_id": detail.id,	
                "artist_name": detail.name,	
                "artist_image_link": detail.image_link,	
                "start_time": f'{detail.start_time}'	
            })
        else:	
            upcoming_shows.append({	
                "artist_id": detail.id,	
                "artist_name": detail.name,	
                "artist_image_link": detail.image_link,	
                "start_time": f'{detail.start_time}'	
            })	
  else:	
    venue_details = Venue.query.filter_by(id=venue_id).all()	
    no_show = True	
      
  for detail in venue_details:	
    venue_info={	
        'id': detail.Venue.id if not no_show else detail.id,	
        'name':detail.Venue.name if not no_show else detail.name,	
        'genres':detail.Venue.genres.replace('{', '').replace('}', '').split(',')\
                if not no_show else \
                detail.genres.replace('{', '').replace('}', '').split(','),	
        'address':detail.Venue.address if not no_show else detail.address,	
        'city': detail.Venue.city if not no_show else detail.city,	
        'state': detail.Venue.state if not no_show else detail.state,	
        'phone': detail.Venue.phone if not no_show else detail.phone,	
        'website': detail.Venue.website if not no_show else detail.website,	
        'facebook_link': detail.Venue.facebook_link if not no_show else detail.facebook_link,	
        'seeking_talent': detail.Venue.seeking_talent == 'y' if not no_show else detail.seeking_talent == 'y',	
        'seeking_description': detail.Venue.seeking_description if not no_show else detail.seeking_description,	
        'image_link': detail.Venue.image_link if not no_show else detail.image_link,	
        'past_shows': past_shows,	
        'upcoming_shows':upcoming_shows,	
        'past_shows_count':len(past_shows),	
        'upcoming_shows_count':len(upcoming_shows)	
    }	

  return render_template('pages/show_venue.html', venue=venue_info)       

 
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
def create_venue_submission():
  form = VenueForm()
  if form.validate_on_submit():
      try:
          name= request.form['name']
          city=request.form['city']
          state=request.form['state']
          address = request.form['address']
          phone=request.form['phone']
          image_link=request.form['image_link']
          facebook_link=request.form['facebook_link']
          website_link =request.form['website_link']
          genres=request.form.getlist('genres')

  #         html checkboxes sends no response when unchecked
          try:
              seeking_talent=request.form['seeking_talent']
          except:
              seeking_talent = 'n'

          seeking_description = request.form['seeking_description']

          new_venue = Venue(
              name=name,
              city=city,
              state=state,
              address = address,
              phone=phone,
              image_link=image_link,
              facebook_link=facebook_link,
              website =website_link,
              genres=genres,
              seeking_talent=seeking_talent,
              seeking_description = seeking_description
          )
          db.session.add(new_venue)
          db.session.commit()
          # on successful db insert, flash success
          flash(f'Venue {request.form["phone"]} was successfully listed!')
      except Exception as e:
          db.session.rollback()                       
          flash(f'<Error: {e}>  Venue {request.form["name"]} could not be listed!')
      finally:
          db.session.close()
      recent_artists, recent_venues = get_recents()
      return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)
  return render_template('forms/new_venue.html', form=form)
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
        shows=Shows.query.filter_by(venue_id=venue_id).all()
        venue=Venue.query.get(venue_id)
        if shows:
            for show in shows:
                db.session.delete(show)
        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue {venue.name} with id {venue.id} and shows count {len(shows)} deleted successfully.')
  except Exception as e:
      db.session.rollback()
      flash(f'<Error: {e}> Venue {venue.name} with id {venue_id} and shows count {len(shows)} could not be deleted.')
  finally:
      db.session.close()
      
  return redirect(url_for('index'))
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  real_data =[]
  artists = Artist.query.order_by('name').all()
  for artist in artists:
      real_data.append(
          {
      "id": artist.id,
      "name": artist.name,
          }
      )
  return render_template('pages/artists.html', artists=real_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  real_response = search(Artist, search_term)
  return render_template('pages/search_artists.html', results=real_response, search_term=search_term)
    
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    no_show = False    
    artist_details=Artist.query.filter_by(id=artist_id).\
    join(Shows, Shows.artist_id==Artist.id).\
    join(Venue, Venue.id==Shows.venue_id).\
    add_columns(Venue.id, Venue.name, Venue.image_link, Shows.start_time)\
    .all()
    
    past_shows =[]
    upcoming_shows=[]
    
    if artist_details:
        for detail in artist_details:
            if detail.start_time < datetime.today():
                past_shows.append({
                    "artist_id": detail.id,
                    "artist_name": detail.name,
                    "artist_image_link": detail.image_link,
                    "start_time": f'{detail.start_time}'
                })
            else:
                upcoming_shows.append({
                    "artist_id": detail.id,
                    "artist_name": detail.name,
                    "artist_image_link": detail.image_link,
                    "start_time": f'{detail.start_time}'
                })
    else:
        artist_details = Artist.query.filter_by(id=artist_id).all()
        no_show = True
        
    for detail in artist_details:
        artist_info={
            'id': detail.Artist.id if not no_show else detail.id,
            'name':detail.Artist.name if not no_show else detail.name,
            'genres':detail.Artist.genres.replace('{', '').replace('}', '').split(',')\
                    if not no_show else \
                    detail.genres.replace('{', '').replace('}', '').split(','),
            'city': detail.Artist.city if not no_show else detail.city,
            'state': detail.Artist.state if not no_show else detail.state,
            'phone': detail.Artist.phone if not no_show else detail.phone,
            'website': detail.Artist.website if not no_show else detail.website,
            'facebook_link': detail.Artist.facebook_link if not no_show else detail.facebook_link,
            'seeking_venue': detail.Artist.seeking_venue == 'y' if not no_show else detail.seeking_venue == 'y',
            'seeking_description': detail.Artist.seeking_description if not no_show else detail.seeking_description,
            'image_link': detail.Artist.image_link if not no_show else detail.image_link,
            'past_shows': past_shows,
            'upcoming_shows':upcoming_shows,
            'past_shows_count':len(past_shows),
            'upcoming_shows_count':len(upcoming_shows)

        }

    return render_template('pages/show_artist.html', artist=artist_info)


  

#----------------------------------------------------#
# Book an artist from the artist page
#----------------------------------------------------#
@app.route('/artists/<int:artist_id>/book_artist', methods=['GET'])
def book_artist(artist_id):
    form = ShowForm()
    form.artist_id.data = artist_id
    return render_template('forms/new_show.html', form=form)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  artist=Artist.query.get(artist_id)
  for field, value in vars(artist).items():
      if field not in ['_sa_instance_state', 'id', 'created_date']:
          field='website_link' if field == 'website' else field
          if field == 'seeking_venue':
              form[field].data = value=='y'
              continue
          form[field].data = value
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
# TODO: take values from the form submitted, and update existing
# artist record with ID <artist_id> using the new attributes
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if form.validate_on_submit():
        try:
            artist.city=form.city.data
            artist.name= form.name.data
            artist.phone= request.form['phone']
            artist.image_link= form.image_link.data
            artist.website= form.website_link.data
            artist.seeking_description= form.seeking_description.data
            artist.state= form.state.data
            artist.genres= form.genres.data
            artist.facebook_link= form.facebook_link.data            
            artist.seeking_venue= 'y' if form.seeking_venue.data else 'n'

            db.session.commit()
            flash(f'<Success! {artist.name} updated successfully.')
        except Exception as e:
            db.session.rollback()
            flash(f'<Error: {e}> {artist.name} could not be updated.')
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)  
  for field, value in vars(venue).items():
      if field not in ['_sa_instance_state', 'id', 'created_date']:
          field='website_link' if field == 'website' else field
          if field == 'seeking_talent':
              form[field].data = value=='y'
              continue
          form[field].data = value
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if form.validate_on_submit():
      try:
          venue.city=form.city.data
          venue.name= form.name.data
          venue.phone= request.form['phone']
          venue.image_link= form.image_link.data
          venue.website= form.website_link.data
          venue.seeking_description= form.seeking_description.data
          venue.state= form.state.data
          venue.genres= form.genres.data
          venue.facebook_link= form.facebook_link.data            
          venue.seeking_talent= 'y' if form.seeking_talent.data else 'n'

          db.session.commit()
          flash(f'<Success! {venue.name} updated successfully.')
      except Exception as e:
          db.session.rollback()
          flash(f'<Error: {e}> {request.form["phone"]} could not be updated.')
      finally:
          db.session.close()
      return redirect(url_for('show_venue', venue_id=venue_id))
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form=ArtistForm()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if form.validate_on_submit():
        try:
            name= request.form['name']
            city=request.form['city']
            state=request.form['state']
            phone=request.form['phone']
            image_link=request.form['image_link']
            facebook_link=request.form['facebook_link']
            website_link =request.form['website_link']
            genres=request.form.getlist('genres')
            try:
                seeking_venue=request.form['seeking_venue']
            except:
                seeking_venue='n'
            seeking_description = request.form['seeking_description']

            new_artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                image_link=image_link,
                facebook_link=facebook_link,
                website =website_link,
                genres=genres,
                seeking_venue=seeking_venue,
                seeking_description = seeking_description
            )
            db.session.add(new_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(f'Artist {request.form["name"]} was successfully listed!')
        except Exception as e:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash(f'<Error: {e}> Artist {request.form["name"]} could not be listed!')
        finally:
            db.session.close()
        recent_artists, recent_venues = get_recents()
        return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)
  return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  real_data = []
  all_shows = Shows.query.all()
  for show in all_shows:
      show_venue = Venue.query.get_or_404(show.venue_id)
      show_artist = Artist.query.get_or_404(show.artist_id)
      
#         populating shows with real data from the database
      real_data.append(
          {
      "venue_id": show_venue.id,
      "venue_name": show_venue.name,
      "artist_id": show_artist.id,
      "artist_name": show_artist.name,
      "artist_image_link": show_artist.image_link,
      "start_time": f'{show.start_time}'
  }
      )
  
  return render_template('pages/shows.html', shows=real_data)

  
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
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        show_time = request.form['start_time']
        new_show = Shows(
            artist_id=artist_id,
            venue_id=venue_id,
            start_time=show_time
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
  except Exception as e:
      db.session.rollback()
      flash(f'<Error: {e}> Show could not be listed!')
  finally: 
      db.session.close()
  recent_artists, recent_venues = get_recents()
  return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)

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
