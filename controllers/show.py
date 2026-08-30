from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms import ShowForm
from services.show import ShowService
from services.availability import AvailabilityService
from dal import Venue, Artist
from datetime import datetime, timedelta

show_bp = Blueprint('shows', __name__, url_prefix='/shows')

# GET /shows
@show_bp.route('/', strict_slashes=False)
def shows():
    """Display all shows.
    
    Returns a page with all shows in the database.
    """
    data = ShowService.get_all_shows()
    return render_template('pages/shows.html', shows=data)

# POST /shows/search
@show_bp.route('/search', methods=['POST'])
def search_shows():
    """Search shows by artist and/or venue.
    
    Accepts search parameters from form data and returns matching shows.
    Returns the search results page with the results.
    """
    artist_id = request.form.get('artist_id', '').strip()
    venue_id = request.form.get('venue_id', '').strip()
    
    if not artist_id and not venue_id:
        flash("Please enter a valid search term", category='error')
        return redirect(request.referrer or url_for('shows.shows'))
    
    response_data = ShowService.search_show_by_artist_and_venue(
        artist_id=int(artist_id) if artist_id else None,
        venue_id=int(venue_id) if venue_id else None
    )
    return render_template('pages/search_shows.html', results={"data": response_data, "count": len(response_data)})

# GET /shows/:show_id
@show_bp.route('/<int:show_id>')
def show_show(show_id):
    """Display details for a specific show.
    
    Takes show_id as URL parameter and returns the show detail page
    with all information about that show. Redirects back if show not found.
    """
    data = ShowService.show_show_by_show_id(show_id=show_id)
    
    if not data:
        flash(f"Show with ID {show_id} not found", category='error')
        return redirect(request.referrer or url_for('shows.shows'))
    
    return render_template('pages/show.html', show=data)

# GET /shows/create
@show_bp.route('/create', methods=['GET'])
def create_show_form():
    """Display the form to create a new show.
    
    Accepts optional artist_id query parameter to prefill the artist field.
    Returns the show creation form for user to fill out.
    """
    form = ShowForm()
    # Populate dropdowns with available venues and artists
    venues = Venue.query.all()
    artists = Artist.query.all()
    
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city}, {v.state})") for v in venues]
    form.artist_id.choices = [(a.id, f"{a.name}") for a in artists]
    
    # Check if artist_id is provided as query parameter to prefill
    artist_id = request.args.get('artist_id', type=int)
    artist_availability = None
    
    if artist_id:
        form.artist_id.data = artist_id
        # Fetch and format artist availability
        availability_data = AvailabilityService.get_artist_availability_summary(artist_id)
        if availability_data:
            artist_availability = {
                'recurring_slots': availability_data.get('recurring_slots', []),
                'exceptions': availability_data.get('exceptions', [])
            }
    
    # Set min_time for start_time input to current time (UTC)
    # Use utcnow() to avoid timezone offset issues with datetime-local HTML input
    min_time = datetime.utcnow()
    
    return render_template('forms/new_show.html', form=form, data={}, now=min_time, artist_availability=artist_availability)

# POST /shows/create
@show_bp.route('/create', methods=['POST'])
def create_show_submission():
    """Handle show creation form submission.
    
    Validates the form data, creates the show in the database,
    and redirects to the shows list on success or redisplays the form on error.
    """
    form = ShowForm()
    # Populate dropdowns for re-rendering if validation fails
    venues = Venue.query.all()
    artists = Artist.query.all()
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city}, {v.state})") for v in venues]
    form.artist_id.choices = [(a.id, f"{a.name}") for a in artists]
    
    validation_error, show_data = ShowService.validate_show_form_data(request.form)
    
    if validation_error:
        flash(f"Form validation failed: {validation_error}", category='error')
        # Fetch artist availability if artist is selected
        artist_availability = None
        artist_id = request.form.get('artist_id', type=int)
        if artist_id:
            availability_data = AvailabilityService.get_artist_availability_summary(artist_id)
            if availability_data:
                artist_availability = {
                    'recurring_slots': availability_data.get('recurring_slots', []),
                    'exceptions': availability_data.get('exceptions', [])
                }
        return render_template('forms/new_show.html', form=form, error=validation_error, data=request.form, now=datetime.utcnow(), artist_availability=artist_availability)
    
    show_create_success, show_fail_reason = ShowService.create_show(show_data)
    
    if show_create_success:
        flash(f"Show was successfully listed!", category='success')
        return redirect(url_for('shows.shows', _external=False))
    else:
        flash(f"Show could not be listed: {show_fail_reason}", category='error')
        # Fetch artist availability if artist is selected
        artist_availability = None
        artist_id = request.form.get('artist_id', type=int)
        if artist_id:
            availability_data = AvailabilityService.get_artist_availability_summary(artist_id)
            if availability_data:
                artist_availability = {
                    'recurring_slots': availability_data.get('recurring_slots', []),
                    'exceptions': availability_data.get('exceptions', [])
                }
        return render_template('forms/new_show.html', form=form, error=show_fail_reason, data=request.form, now=datetime.utcnow(), artist_availability=artist_availability)

# GET /shows/:show_id/edit
@show_bp.route('/<int:show_id>/edit', methods=['GET'])
def edit_show(show_id):
    """Display the form to edit an existing show.
    
    Takes show_id as URL parameter, fetches the show data from the database,
    and returns a form pre-populated with the current show information.
    """
    form = ShowForm()
    data = ShowService.show_show_by_show_id(show_id=show_id)
    
    if not data:
        flash(f"Show with ID {show_id} not found", category='error')
        return redirect(request.referrer or url_for('shows.shows'))
    
    # Populate dropdowns
    venues = Venue.query.all()
    artists = Artist.query.all()
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city}, {v.state})") for v in venues]
    form.artist_id.choices = [(a.id, f"{a.name}") for a in artists]
    
    # Populate form with show data
    form.venue_id.data = data.get('venue_id')
    form.artist_id.data = data.get('artist_id')
    # Convert ISO format string to datetime object
    start_time_str = data.get('start_time')
    if start_time_str:
        form.start_time.data = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    
    end_time_str = data.get('end_time')
    if end_time_str:
        form.end_time.data = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
    
    return render_template('forms/edit_show.html', form=form, show=data)

# POST /shows/:show_id/edit
@show_bp.route('/<int:show_id>/edit', methods=['POST'])
def edit_show_submission(show_id):
    """Handle show edit form submission.
    
    Takes show_id as URL parameter, validates the submitted form data,
    updates the show in the database, and redirects on success
    or redisplays the form on error.
    """
    form = ShowForm()
    show = ShowService.show_show_by_show_id(show_id=show_id)
    
    if not show:
        flash(f"Show with ID {show_id} not found", category='error')
        return redirect(request.referrer or url_for('shows.shows'))
    
    # Populate dropdowns for re-rendering if validation fails
    venues = Venue.query.all()
    artists = Artist.query.all()
    form.venue_id.choices = [(v.id, f"{v.name} ({v.city}, {v.state})") for v in venues]
    form.artist_id.choices = [(a.id, f"{a.name}") for a in artists]
    
    validation_error, show_data = ShowService.validate_show_form_data(request.form)
    
    if validation_error:
        flash(f"Form validation failed: {validation_error}", category='error')
        return render_template('forms/edit_show.html', form=form, show=show, error=validation_error)
    
    show_edit_success, show_fail_reason = ShowService.update_show(show_id, show_data)
    
    if show_edit_success:
        flash(f"Show was successfully updated!", category='success')
        return redirect(url_for('shows.show_show', show_id=show_id))
    else:
        flash(f"Show could not be updated: {show_fail_reason}", category='error')
        return render_template('forms/edit_show.html', form=form, show=show, error=show_fail_reason)

# DELETE /shows/:show_id
@show_bp.route('/<int:show_id>', methods=['DELETE'])
def delete_show(show_id):
    """Delete a show by its ID.
    
    Takes show_id as URL parameter and deletes that show from the database.
    Returns a JSON response with success or failure status.
    """
    success, error = ShowService.delete_show(show_id=show_id)

    if success:
        return {'success': True, 'message': 'Show deleted successfully!'}, 200
    else:
        return {'success': False, 'message': error or 'Unable to delete show'}, 400

# POST /shows/:show_id/delete
@show_bp.route('/<int:show_id>/delete', methods=['POST'])
def delete_show_post(show_id):
    """Delete a show (POST endpoint for form submissions).
    
    Takes show_id as URL parameter and deletes that show from the database.
    Redirects back to /shows on success, or back to show page with error.
    """
    success, error = ShowService.delete_show(show_id=show_id)

    if success:
        flash('Show successfully deleted!', 'success')
        return redirect('/shows')
    else:
        flash(f'Unable to delete show: {error}', 'danger')
        return redirect(f'/shows/{show_id}')
