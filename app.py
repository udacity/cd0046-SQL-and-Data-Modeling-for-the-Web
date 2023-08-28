#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from datetime import datetime
from flask import (
    abort,
    Flask, render_template,
    request, 
    flash, redirect,
    url_for,
)
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import ArtistForm, ShowForm, VenueForm
from model import Artist, db, Show, Venue
from util import format_datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters
#----------------------------------------------------------------------------#

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

@app.route('/', methods=['GET'])
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():    
    try:
        venue_groups = db.session.query(Venue.city, Venue.state)\
                                .group_by(Venue.city, Venue.state)\
                                .order_by(Venue.state).all()
        if not venue_groups: 
            flash('No venue(s) yet. Please create one.') 
            return redirect(url_for('create_venue_form'))
        
        resp = []    
        for group in venue_groups:
            venues_in_group = []
            
            city = group[0]
            state = group[1]
            venues = db.session.query(Venue).filter(Venue.city == city, Venue.state == state).all()
            
            for venue in venues:
                venues_in_group.append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': len(db.session.query(Show)
                                            .filter(Show.venue_id == venue.id)
                                            .filter(Show.start_time > datetime.now())
                                            .all()
                                            )
                })
                
            sorted_num_shows_desc = sorted(venues_in_group, 
                                                key=lambda x: x['num_upcoming_shows'], 
                                                reverse=True)
            resp.append({
                'city': city,
                'state': state,
                'venues': sorted_num_shows_desc,
            })
        return render_template('pages/venues.html', areas=resp)
            
    except:
        abort(500)
        
    finally:
        db.session.close()


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    try:
        results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
        data = []
        for result in results:
            data.append({
                'id': result.id,
                'name': result.name,
                'num_upcoming_shows': len(db.session.query(Show)
                                                    .filter(Show.venue_id == result.id)
                                                    .filter(Show.start_time > datetime.now())
                                                    .all()),  
            })
        return render_template(
            'pages/search_venues.html', 
            results={'count': len(results), 'data': data}, 
            search_term=search_term,
        )
        
    except:
        abort(500)
        
    finally:
        db.session.close()


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        venue = db.session.query(Venue).filter(Venue.id == venue_id)
        if not venue:
            abort(404)
            
        return render_template('pages/show_venue.html', venue=venue.to_dict())
    
    except:
        abort(500)
        
    finally:
        db.session.close()    


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    venue_name = form.name.data.strip()
    venue_city = form.city.data.strip()
    try:
        exists = db.session.query(Venue).filter(Venue.name == venue_name, Venue.city == venue_city).one_or_none()
        if exists: 
            flash(f'"{venue_name}" already exists in {venue_city}.')
            return redirect(url_for('create_venue_form'))
        
        new_venue = Venue()
        form.populate_obj(new_venue)
        db.session.add(new_venue) 
        db.session.commit()
        flash(f'Venue {venue_name} successfully listed!')
        return render_template('pages/home.html')
    
    except:
        flash(f'An error occurred. Venue {venue_name} could not be listed.')
        db.session.rollback()
        return redirect(url_for('create_venue_form'))
  
    finally:
        db.session.close()
        

@app.route('/venues/<venue_id>/delete', methods=['POST'])	
def delete_venue(venue_id):
    try:
        exists = db.session.query(Venue).filter(Venue.id == venue_id).one_or_none()
        db.session.delete(exists)
        db.session.commit()
        flash(f'Venue "{exists.name}" has been successfully removed.')
        return redirect(url_for('show_venue'))
        
    except:
        db.session.rollback()
        flash('An error has occured.')
        return redirect(url_for('show_venue'))
        
    finally:
        db.session.close()
        

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        venue = db.session.query(Venue).filter(Venue.id == venue_id).one_or_none()
        if not venue:
            abort(404)
            
        form = VenueForm(obj=venue)
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    
    except:
        abort(500)
        
    finally:
        db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try: 
        venue = db.session.query(Venue).filter(Venue.id == venue_id)
        venue = form.populate_obj(venue)
        db.session.commit()
        flash('Venue updated successfuly!')
        return redirect(url_for('show_venue', venue_id=venue_id))
    
    except: 
        flash('Unsuccessful update.')  
        db.session.rollback()
        return redirect(url_for('edit_venue', venue_id=venue_id))
        
    finally: 
        db.session.close()


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    try:
        artists = db.session.query(Artist).all()
        if not artists: 
            flash('No artist(s) yet. Please create one.') 
            return redirect(url_for('create_artist_form'))
        
        data = []
        for artist in artists:
            data.append({
                'id': artist.id,
                'name': artist.name,
            })
        return render_template('pages/artists.html', artists=data)
    
    except:
        abort(500)
        
    finally:
        db.session.close()
        

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    try:
        results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
        data = []
        for result in results:
            data.append({
                'id': result.id,
                'name': result.name,
                'num_upcoming_shows': len(db.session.query(Show)
                                                    .filter(Show.artist_id == result.id)
                                                    .filter(Show.start_time > datetime.now())
                                                    .all()),  
            })
        return render_template(
            'pages/search_artists.html', 
            results={'count': len(results), 'data': data}, 
            search_term=search_term,
        )
        
    except:
        abort(500)
        
    finally:
        db.session.close()


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        artist = db.session.query(Artist).filter(Artist.id == artist_id)
        if not artist:
            abort(404)
            
        return render_template('pages/show_artist.html', artist=artist.to_dict())
    
    except:
        abort(500)
        
    finally:
        db.session.close()    


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        artist = db.session.query(Artist).filter(Artist.id == artist_id).one_or_none()
        if not artist:
            abort(404)
            
        form = ArtistForm(obj=artist)
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    
    except:
        abort(500)
        
    finally:
        db.session.close()


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    try: 
        artist = db.session.query(Artist).filter(Artist.id == artist_id)
        artist = form.populate_obj(artist)
        db.session.commit()
        flash('Artist successfully updated!')
        return redirect(url_for('show_artist', artist_id=artist_id))
    
    except: 
        flash('Unsuccessful update.')
        db.session.rollback()
        return redirect(url_for('edit_artist', artist_id=artist_id))
        
    finally: 
        db.session.close()
    
    
@app.route('/artists/create', methods=['GET']) 
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    artist_name = form.name.data.strip()
    try:
        exists = db.session.query(Artist).filter(Artist.name == artist_name).one_or_none()
        if exists: 
            flash('This name is already in use.')
            return redirect(url_for('create_artist_form'))
        
        new_artist = Artist()
        form.populate_obj(new_artist)
        db.session.add(new_artist) 
        db.session.commit()
        flash(f'Artist {artist_name} was successfully listed!')
        return redirect(url_for('show_artist', artist_id=new_artist.id))
            
    except:
        flash(f'An error occurred. Artist {artist_name} could not be listed.')
        db.session.rollback()
        return redirect(url_for('create_artist_form'))
        
    finally:
        db.session.close()


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows', methods=['GET'])
def shows():
    try:
        shows = db.session.query(Show).all()
        if not shows:
            flash('No show(s) yet. Please create one.')
            return redirect(url_for('create_show_form'))
        
        resp = []
        for show in shows:
            resp.append({   
                    'venue_id': show.venue_id,
                    'venue_name': show.venue.name,
                    'artist_id': show.artist_id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': str(show.start_time)
            })       
        return render_template('pages/shows.html', shows=resp)
            
    except:
        abort(500)
        
    finally:
        db.session.close()
        
  
@app.route('/shows/create', methods=['GET']) 
def create_show_form():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    artist_id = form.artist_id.data.strip()
    venue_id = form.venue_id.data.strip()
    
    try:
        artist = db.session.query(Artist).filter(Artist.id == artist_id).one_or_none()
        venue = db.session.query(Venue).filter(Venue.id == venue_id).one_or_none()
    
        if not artist:
            flash('Cannot create new show with an unknown artist. Create the new artist first.')
            return redirect(url_for('create_artist_form'))
            
        elif not venue:
            flash('Cannot create new show with an unknown venue. Create the new venue first.')
            return redirect(url_for('create_venue_form'))
        
    except:
        abort(500)
        
    finally:
        db.session.close()

    try:
        new_show = Show()
        form.populate_obj(new_show)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('create_show_form'))
        
    finally:
        db.session.close() 


#  Error handlers
#  ----------------------------------------------------------------

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
