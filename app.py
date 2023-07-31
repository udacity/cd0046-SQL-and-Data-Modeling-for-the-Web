#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Migrate, Venue, Artist, Show


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
moment = Moment(app)
migrate = Migrate(app, db)

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
  # Done : replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    performance_venues = Venue.query.distinct(Venue.city, Venue.state).all()
    data = []

    for venue in performance_venues:    
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
                "id": venue_data.id,
                "name": venue_data.name,
                "num_upcoming_shows": len(Show.query.filter(Show.venue_id==venue_data.id, Show.start_time > datetime.now()).all())
            } for venue_data in Venue.query.filter_by(city=venue.city, state=venue.state).all()]
        })
    print(data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()
    searched_venues = []
    for venue in venues:
        searched_venues.append({
            "id": venue.id,
            "name": venue.name,
        })

    response = {
        "count": len(venues),
        "data": searched_venues
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
    error = False
    try:
        venue = Venue.query.get(venue_id)
        upcoming_shows = []
        past_shows = []

        for show in venue.shows:
            if show.start_time > datetime.now():
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres.split(','),
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()),
            "past_shows_count": len(Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()),
        }
    except:
        error = True
        print(sys.exc_info())
    if error == True:
        abort(500)
    else:
        return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Done: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion

    create_venue_form = VenueForm(request.form)
    error = False

    try:
        create_venue = Venue(
            name=create_venue_form.name.data,
            city=create_venue_form.city.data,
            state=create_venue_form.state.data,
            address=create_venue_form.address.data,
            phone=create_venue_form.phone.data,
            genres=create_venue_form.genres.data,
            facebook_link=create_venue_form.facebook_link.data,
            image_link=create_venue_form.image_link.data,
            website=create_venue_form.website.data,
            seeking_talent=create_venue_form.seeking_talent.data,
            seeking_description=create_venue_form.seeking_description.data
        )
        db.session.add(create_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash("Venue {0} has been deleted successfully".format(
            venue[0]['name']))
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash("An error occurred. Venue {0} could not be deleted.".format(
            venue[0]['name']))
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template(url_for('/venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.order_by('id').all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()
    searched_artists = []
    for artist in artists:
        searched_artists.append({
            "id": artist.id,
            "name": artist.name,
        })
    response = {
        "count": len(artists),
        "data": searched_artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        upcoming_shows = []
        past_shows = []

        for show in artist.shows:
            if show.start_time > datetime.now():
                upcoming_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                past_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres.split(','),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()),
            "past_shows_count": len(Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()),
        }

    except:
        error = True
        print(sys.exc_info())
    if error == True:
        abort(500)
    else:
        return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist_form = ArtistForm(request.form)
    error = False

    try:
        artist = Artist.query.get(artist_id)

        artist.name = artist_form.name.data
        artist.city = artist_form.city.data
        artist.state = artist_form.state.data
        artist.phone = artist_form.phone.data
        artist.genres = artist_form.genres.data
        artist.image_link = artist_form.image_link.data
        artist.facebook_link = artist_form.facebook_link.data
        artist.website_link = artist_form.website_link.data
        artist.seeking_venue = artist_form.seeking_venue.data
        artist.seeking_description = artist_form.seeking_description.data

        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' information was succesfully updated!')

    except:
        error = True
        db.session.rollback()
        flash('Artist ' + request.form['name'] +
              ' information was not updated!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    get_venue = Venue.query.get(venue_id)

    venue = {
        "id": get_venue.id,
        "name": get_venue.name,
        "genres": get_venue.genres,
        "address": get_venue.address,
        "city": get_venue.city,
        "state": get_venue.state,
        "phone": get_venue.phone,
        "website": get_venue.website,
        "facebook_link": get_venue.facebook_link,
        "seeking_talent": get_venue.seeking_talent,
        "seeking_description": get_venue.seeking_description,
        "image_link": get_venue.image_link
    }
    form = VenueForm(data=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_form = VenueForm(request.form)
    error = False
    try:
        venue = Artist.query.get(venue_id)
        venue.name = venue_form.name.data
        venue.genres = venue_form.genres.data
        venue.address = venue_form.address.data
        venue.city = venue_form.city.data
        venue.state = venue_form.state.data
        venue.phone = venue_form.phone.data
        venue.website = venue_form.website_link.data
        venue.facebook_link = venue_form.facebook_link.data
        venue.seeking_talent = venue_form.seeking_talent.data
        venue.seeking_description = venue_form.seeking_description.data,
        venue.image_link = venue_form.image_link

        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' information was succesfully updated!')

    except:
        error = True
        db.session.rollback()
        flash('Venue ' + request.form['name'] +
              ' information was not updated!')
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    create_artist_form = ArtistForm(request.form)
    error = False
    try:
        create_artist = Artist(
            name=create_artist_form.name.data,
            city=create_artist_form.city.data,
            state=create_artist_form.state.data,
            phone=create_artist_form.phone.data,
            genres=create_artist_form.genres.data,
            image_link=create_artist_form.image_link.data,
            facebook_link=create_artist_form.facebook_link.data
        )

        db.session.add(create_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' could not be listed!')

    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []

    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "artist_id": show.artist_id,
            "start_time": show.start_time,
            "artist_name": Artist.query.get(show.artist_id).name,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,
            "venue_name": Venue.query.get(show.venue_id).name,
        })

    return render_template('pages/shows.html', shows=data)
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_form = ShowForm(request.form)
    error = False

    try:
        create_show = Show(
            artist_id=show_form.artist_id.data,
            venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )

        db.session.add(create_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
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
