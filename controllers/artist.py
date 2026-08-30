from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms import ArtistForm, ArtistAvailabilityForm, ArtistAvailabilityExceptionForm
from services.artist import ArtistService
from forms_constants import STATE_CHOICES, GENRE_CHOICES
from dal import db
from dal.availability import ArtistAvailability, ArtistAvailabilityException
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

artist_bp = Blueprint('artists', __name__, url_prefix='/artists')

# GET /artists
@artist_bp.route('/', strict_slashes=False)
def artists():
    """Display all artists.
    
    Returns a page with all artists in the database.
    """
    data = ArtistService.get_all_artists()
    return render_template('pages/artists.html', artists=data, states=STATE_CHOICES, genres=GENRE_CHOICES)

# POST /artists/search
@artist_bp.route('/search', methods=['POST'])
def search_artists():
    """Search artists by name, city, state, and/or genres.
    
    Accepts search_term, city, state, and genres from form data and returns matching artists.
    Returns the search results page with the search criteria and results.
    """
    search_term = request.form.get('search_term', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    genres = request.form.getlist('genres')
    
    # If no search criteria provided, show error
    if not search_term and not city and not state and not genres:
        flash("Please enter a search term, city, state, or select genres", category='error')
        return redirect(request.referrer or url_for('artists.artists'))
    
    # If search term provided, search by name
    if search_term:
        response = ArtistService.search_artist_by_name(search_term=search_term)
        search_label = f'"{search_term}"'
    # Otherwise search by city/state/genres
    else:
        response = ArtistService.search_artist_by_location(city=city, state=state, genres=genres)
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if genres:
            location_parts.append(f"{len(genres)} genre(s)")
        search_label = ', '.join(location_parts)
    
    return render_template('pages/search_artists.html', 
                         results=response, 
                         search_term=search_term,
                         city=city,
                         state=state,
                         genres=genres,
                         search_label=search_label,
                         states=STATE_CHOICES,
                         genre_choices=GENRE_CHOICES)

# GET /artists/:artist_id
@artist_bp.route('/<int:artist_id>')
def show_artist(artist_id):
    """Display details for a specific artist.
    
    Takes artist_id as URL parameter and returns the artist detail page
    with all information about that artist. Redirects back if artist not found.
    """
    data = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    
    if not data:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(request.referrer or url_for('artists.artists'))
    
    return render_template('pages/show_artist.html', artist=data)

# GET /artists/create
@artist_bp.route('/create', methods=['GET'])
def create_artist_form():
    """Display the form to create a new artist.
    
    Returns the artist creation form for user to fill out.
    """
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form, data={})

# POST /artists/create
@artist_bp.route('/create', methods=['POST'])
def create_artist_submission():
    """Handle artist creation form submission.
    
    Validates the form data, creates the artist in the database,
    and redirects to the artists list on success or redisplays the form on error.
    """
    form = ArtistForm(formdata=request.form)
    validation_errors, artist_data = ArtistService.validate_artist_form_data(request.form)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                # WTForms expects errors as a tuple/list
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/new_artist.html', form=form, data=request.form)
    
    artist_create_success, artist_fail_reason = ArtistService.create_artist(artist_data)
    
    if artist_create_success:
        flash(f"Artist {artist_data.name} was successfully listed!", category='success')
        return redirect(url_for('artists.artists', _external=False))
    else:
        flash(f"Artist could not be listed: {artist_fail_reason}", category='error')
        return render_template('forms/new_artist.html', form=form, error=artist_fail_reason, data=request.form)

# GET /artists/:artist_id/edit
@artist_bp.route('/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """Display the form to edit an existing artist.
    
    Takes artist_id as URL parameter, fetches the artist data from the database,
    and returns a form pre-populated with the current artist information.
    """
    form = ArtistForm()
    data = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    
    if not data:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(request.referrer or url_for('artists.artists'))
    
    # Populate form with artist data
    form.name.data = data.get('name')
    form.city.data = data.get('city')
    form.state.data = data.get('state')
    form.phone.data = data.get('phone')
    form.image_link.data = data.get('image_link')
    form.genres.data = data.get('genres', [])
    form.facebook_link.data = data.get('facebook_link')
    form.website_link.data = data.get('website')
    form.seeking_venue.data = data.get('seeking_venue', False)
    form.seeking_description.data = data.get('seeking_description')
    
    return render_template('forms/edit_artist.html', form=form, artist=data)

# DELETE /artists/:artist_id
@artist_bp.route('/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    """Delete an artist by its ID.
    
    Takes artist_id as URL parameter and deletes that artist from the database.
    Returns a JSON response with success or failure status.
    """
    success, error = ArtistService.delete_artist(artist_id=artist_id)

    if success:
        return {'success': True, 'message': 'Artist deleted successfully!'}, 200
    else:
        return {'success': False, 'message': error or 'Unable to delete artist'}, 400

# POST /artists/:artist_id/delete
@artist_bp.route('/<int:artist_id>/delete', methods=['POST'])
def delete_artist_post(artist_id):
    """Delete an artist (POST endpoint for form submissions).
    
    Takes artist_id as URL parameter and deletes that artist from the database.
    Redirects back to /artists on success, or back to artist page with error.
    """
    success, error = ArtistService.delete_artist(artist_id=artist_id)

    if success:
        flash('Artist successfully deleted!', 'success')
        return redirect('/artists')
    else:
        flash(f'Unable to delete artist: {error}', 'danger')
        return redirect(f'/artists/{artist_id}')

# POST /artists/:artist_id/edit
@artist_bp.route('/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    """Handle artist edit form submission.
    
    Takes artist_id as URL parameter, validates the submitted form data,
    updates the artist in the database, and redirects on success
    or redisplays the form on error.
    """
    form = ArtistForm(formdata=request.form)
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(request.referrer or url_for('artists.artists'))
    
    validation_errors, artist_data = ArtistService.validate_artist_form_data(request.form)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                # WTForms expects errors as a tuple/list
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    
    artist_edit_success, artist_fail_reason = ArtistService.update_artist(artist_id, artist_data)
    
    if artist_edit_success:
        flash(f"Artist {artist_data.name} was successfully updated!", category='success')
        return redirect(url_for('artists.show_artist', artist_id=artist_id))
    else:
        flash(f"Artist could not be updated: {artist_fail_reason}", category='error')
        return render_template('forms/edit_artist.html', form=form, artist=artist, error=artist_fail_reason)


# GET /artists/<id>/availability
@artist_bp.route('/<int:artist_id>/availability', strict_slashes=False)
def show_artist_availability(artist_id):
    """Display artist's availability schedule.
    
    Shows recurring weekly availability slots and date-specific exceptions.
    """
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    weekly_availability = ArtistAvailability.query.filter_by(artist_id=artist_id).order_by(
        ArtistAvailability.day_of_week,
        ArtistAvailability.start_time
    ).all()
    
    exceptions = ArtistAvailabilityException.query.filter_by(artist_id=artist_id).order_by(
        ArtistAvailabilityException.exception_date.desc()
    ).all()
    
    return render_template('pages/artist_availability.html',
                         artist=artist,
                         weekly_availability=weekly_availability,
                         exceptions=exceptions)


# GET /artists/<id>/availability/new
@artist_bp.route('/<int:artist_id>/availability/new', methods=['GET'])
def new_artist_availability(artist_id):
    """Show form for creating new artist availability slot."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    form = ArtistAvailabilityForm()
    return render_template('forms/new_availability.html', form=form, artist=artist)


# POST /artists/<id>/availability/new
@artist_bp.route('/<int:artist_id>/availability/new', methods=['POST'])
def create_artist_availability(artist_id):
    """Handle artist availability form submission."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    form = ArtistAvailabilityForm()
    logger.info(f"Form data received for artist {artist_id}: {request.form}")
    
    if not form.validate():
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msg = f"{field}: {error}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        logger.error(f"Form validation failed for artist {artist_id}. Errors: {error_messages}")
        flash("Form validation failed: " + "; ".join(error_messages), category='error')
        return render_template('forms/new_availability.html', form=form, artist=artist)
    
    try:
        logger.info(f"Creating availability for artist {artist_id}: day={form.day_of_week.data}, start={form.start_time.data}, end={form.end_time.data}")
        availability = ArtistAvailability(
            artist_id=artist_id,
            day_of_week=int(form.day_of_week.data),
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_available=form.is_available.data
        )
        db.session.add(availability)
        db.session.commit()
        logger.info(f"Successfully created availability slot for artist {artist_id}")
        flash("Availability slot created successfully!", category='success')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    except IntegrityError as e:
        db.session.rollback()
        if 'uq_artist_availability_slot' in str(e):
            logger.warning(f"Duplicate availability slot attempted for artist {artist_id}: day={form.day_of_week.data}, start={form.start_time.data}, end={form.end_time.data}")
            flash("You already have an availability slot for this day and time. Please delete it first or create a different time slot.", category='error')
        else:
            logger.exception(f"Integrity error creating availability for artist {artist_id}: {str(e)}")
            flash(f"Error creating availability: Database constraint violation", category='error')
        return render_template('forms/new_availability.html', form=form, artist=artist)
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error creating availability for artist {artist_id}: {str(e)}")
        flash(f"Error creating availability: {str(e)}", category='error')
        return render_template('forms/new_availability.html', form=form, artist=artist)


# GET /artists/<id>/availability/<slot_id>/edit
@artist_bp.route('/<int:artist_id>/availability/<int:slot_id>/edit', methods=['GET'])
def edit_artist_availability(artist_id, slot_id):
    """Show form for editing artist availability slot."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    slot = ArtistAvailability.query.get(slot_id)
    if not slot or slot.artist_id != artist_id:
        flash("Availability slot not found", category='error')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    
    form = ArtistAvailabilityForm()
    if request.method == 'GET':
        form.day_of_week.data = slot.day_of_week
        form.start_time.data = datetime.combine(datetime.today(), slot.start_time)
        form.end_time.data = datetime.combine(datetime.today(), slot.end_time)
        form.is_available.data = slot.is_available
    
    return render_template('forms/new_availability.html', form=form, artist=artist)


# POST /artists/<id>/availability/<slot_id>/edit
@artist_bp.route('/<int:artist_id>/availability/<int:slot_id>/edit', methods=['POST'])
def update_artist_availability(artist_id, slot_id):
    """Handle artist availability form submission for updates."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    slot = ArtistAvailability.query.get(slot_id)
    if not slot or slot.artist_id != artist_id:
        flash("Availability slot not found", category='error')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    
    form = ArtistAvailabilityForm()
    logger.info(f"Update form data received for artist {artist_id}, slot {slot_id}: {request.form}")
    
    if not form.validate():
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msg = f"{field}: {error}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        logger.error(f"Update form validation failed for artist {artist_id}. Errors: {error_messages}")
        flash("Form validation failed: " + "; ".join(error_messages), category='error')
        return render_template('forms/new_availability.html', form=form, artist=artist)
    
    try:
        logger.info(f"Updating availability for artist {artist_id}, slot {slot_id}: day={form.day_of_week.data}")
        slot.day_of_week = int(form.day_of_week.data)
        slot.start_time = form.start_time.data
        slot.end_time = form.end_time.data
        slot.is_available = form.is_available.data
        db.session.commit()
        logger.info(f"Successfully updated availability slot for artist {artist_id}")
        flash("Availability slot updated successfully!", category='success')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    except IntegrityError as e:
        db.session.rollback()
        if 'uq_artist_availability_slot' in str(e):
            logger.warning(f"Duplicate availability slot attempted during update for artist {artist_id}: day={form.day_of_week.data}, start={form.start_time.data}, end={form.end_time.data}")
            flash("Another availability slot already exists for this day and time.", category='error')
        else:
            logger.exception(f"Integrity error updating availability for artist {artist_id}: {str(e)}")
            flash(f"Error updating availability: Database constraint violation", category='error')
        return render_template('forms/new_availability.html', form=form, artist=artist)
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating availability for artist {artist_id}: {str(e)}")
        flash(f"Error updating availability: {str(e)}", category='error')
        return render_template('forms/new_availability.html', form=form, artist=artist)


# POST /artists/<id>/availability/<slot_id>/delete
@artist_bp.route('/<int:artist_id>/availability/<int:slot_id>/delete', methods=['POST'])
def delete_artist_availability(artist_id, slot_id):
    """Delete an artist availability slot."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    slot = ArtistAvailability.query.get(slot_id)
    if not slot or slot.artist_id != artist_id:
        flash("Availability slot not found", category='error')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    
    try:
        db.session.delete(slot)
        db.session.commit()
        flash("Availability slot deleted successfully!", category='success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting availability: {str(e)}", category='error')
    
    return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))


# GET /artists/<id>/availability/exception/new
@artist_bp.route('/<int:artist_id>/availability/exception/new', methods=['GET'])
def new_artist_availability_exception(artist_id):
    """Show form for creating new availability exception."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    form = ArtistAvailabilityExceptionForm()
    return render_template('forms/new_availability_exception.html', form=form, artist=artist)


# POST /artists/<id>/availability/exception/new
@artist_bp.route('/<int:artist_id>/availability/exception/new', methods=['POST'])
def create_artist_availability_exception(artist_id):
    """Handle artist availability exception form submission."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    form = ArtistAvailabilityExceptionForm()
    logger.info(f"Exception form data received for artist {artist_id}: {request.form}")
    
    if not form.validate():
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msg = f"{field}: {error}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        logger.error(f"Exception form validation failed for artist {artist_id}. Errors: {error_messages}")
        flash("Form validation failed: " + "; ".join(error_messages), category='error')
        return render_template('forms/new_availability_exception.html', form=form, artist=artist)
    
    try:
        logger.info(f"Creating availability exception for artist {artist_id}: date={form.exception_date.data}")
        exception = ArtistAvailabilityException(
            artist_id=artist_id,
            exception_date=form.exception_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_available=form.is_available.data,
            reason=form.reason.data
        )
        db.session.add(exception)
        db.session.commit()
        logger.info(f"Successfully created availability exception for artist {artist_id}")
        flash("Availability exception created successfully!", category='success')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    except IntegrityError as e:
        db.session.rollback()
        if 'uq_artist_availability_exception' in str(e):
            logger.warning(f"Duplicate availability exception attempted for artist {artist_id}: date={form.exception_date.data}")
            flash("You already have an exception for this date. Please delete it first or choose a different date.", category='error')
        else:
            logger.exception(f"Integrity error creating exception for artist {artist_id}: {str(e)}")
            flash(f"Error creating exception: Database constraint violation", category='error')
        return render_template('forms/new_availability_exception.html', form=form, artist=artist)
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error creating exception for artist {artist_id}: {str(e)}")
        flash(f"Error creating exception: {str(e)}", category='error')
        return render_template('forms/new_availability_exception.html', form=form, artist=artist)


# GET /artists/<id>/availability/exception/<exc_id>/edit
@artist_bp.route('/<int:artist_id>/availability/exception/<int:exc_id>/edit', methods=['GET'])
def edit_artist_availability_exception(artist_id, exc_id):
    """Show form for editing availability exception."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    exception = ArtistAvailabilityException.query.get(exc_id)
    if not exception or exception.artist_id != artist_id:
        flash("Availability exception not found", category='error')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    
    form = ArtistAvailabilityExceptionForm()
    if request.method == 'GET':
        form.exception_date.data = exception.exception_date
        form.start_time.data = datetime.combine(datetime.today(), exception.start_time)
        form.end_time.data = datetime.combine(datetime.today(), exception.end_time)
        form.is_available.data = exception.is_available
        form.reason.data = exception.reason
    
    return render_template('forms/new_availability_exception.html', form=form, artist=artist)


# POST /artists/<id>/availability/exception/<exc_id>/edit
@artist_bp.route('/<int:artist_id>/availability/exception/<int:exc_id>/edit', methods=['POST'])
def update_artist_availability_exception(artist_id, exc_id):
    """Handle artist availability exception form submission for updates."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    exception = ArtistAvailabilityException.query.get(exc_id)
    if not exception or exception.artist_id != artist_id:
        flash("Availability exception not found", category='error')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    
    form = ArtistAvailabilityExceptionForm()
    logger.info(f"Exception update form data received for artist {artist_id}, exception {exc_id}: {request.form}")
    
    if not form.validate():
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msg = f"{field}: {error}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        logger.error(f"Exception update form validation failed for artist {artist_id}. Errors: {error_messages}")
        flash("Form validation failed: " + "; ".join(error_messages), category='error')
        return render_template('forms/new_availability_exception.html', form=form, artist=artist)
    
    try:
        logger.info(f"Updating availability exception for artist {artist_id}, exception {exc_id}: date={form.exception_date.data}")
        exception.exception_date = form.exception_date.data
        exception.start_time = form.start_time.data
        exception.end_time = form.end_time.data
        exception.is_available = form.is_available.data
        exception.reason = form.reason.data
        db.session.commit()
        logger.info(f"Successfully updated availability exception for artist {artist_id}")
        flash("Availability exception updated successfully!", category='success')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    except IntegrityError as e:
        db.session.rollback()
        if 'uq_artist_availability_exception' in str(e):
            logger.warning(f"Duplicate availability exception attempted during update for artist {artist_id}: date={form.exception_date.data}")
            flash("Another exception already exists for this date.", category='error')
        else:
            logger.exception(f"Integrity error updating exception for artist {artist_id}: {str(e)}")
            flash(f"Error updating exception: Database constraint violation", category='error')
        return render_template('forms/new_availability_exception.html', form=form, artist=artist)
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating exception for artist {artist_id}: {str(e)}")
        flash(f"Error updating exception: {str(e)}", category='error')
        return render_template('forms/new_availability_exception.html', form=form, artist=artist)


# POST /artists/<id>/availability/exception/<exc_id>/delete
@artist_bp.route('/<int:artist_id>/availability/exception/<int:exc_id>/delete', methods=['POST'])
def delete_artist_availability_exception(artist_id, exc_id):
    """Delete an artist availability exception."""
    artist = ArtistService.show_artist_by_artist_id(artist_id=artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} not found", category='error')
        return redirect(url_for('artists.artists'))
    
    exception = ArtistAvailabilityException.query.get(exc_id)
    if not exception or exception.artist_id != artist_id:
        flash("Availability exception not found", category='error')
        return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
    
    try:
        db.session.delete(exception)
        db.session.commit()
        flash("Availability exception deleted successfully!", category='success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting exception: {str(e)}", category='error')
    
    return redirect(url_for('artists.show_artist_availability', artist_id=artist_id))
