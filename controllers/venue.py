from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms import VenueForm
from services.venue import VenueService
from forms_constants import STATE_CHOICES, GENRE_CHOICES

venue_bp = Blueprint('venues', __name__, url_prefix='/venues')

# GET /venues
@venue_bp.route('/', strict_slashes=False)
def venues():
    """Display all venues grouped by city and state.
    
    Returns a page with venues organized by location.
    """
    data = VenueService.get_venues_grouped_by_location()
    return render_template('pages/venues.html', areas=data, states=STATE_CHOICES, genres=GENRE_CHOICES)

# POST /venues/search
@venue_bp.route('/search', methods=['POST'])
def search_venues():
    """Search venues by name, city, state, and/or genres.
    
    Accepts search_term, city, state, and genres from form data and returns matching venues.
    Returns the search results page with the search criteria and results.
    """
    search_term = request.form.get('search_term', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    genres = request.form.getlist('genres')
    
    # If no search criteria provided, show error
    if not search_term and not city and not state and not genres:
        flash("Please enter a search term, city, state, or select genres", category='error')
        return redirect(request.referrer or url_for('venues.venues'))
    
    # If search term provided, search by name
    if search_term:
        response = VenueService.search_venue_by_name(search_term=search_term)
        search_label = f'"{search_term}"'
    # Otherwise search by city/state/genres
    else:
        response = VenueService.search_venue_by_location(city=city, state=state, genres=genres)
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if genres:
            location_parts.append(f"{len(genres)} genre(s)")
        search_label = ', '.join(location_parts)
    
    return render_template('pages/search_venues.html', 
                         results=response, 
                         search_term=search_term,
                         city=city,
                         state=state,
                         genres=genres,
                         search_label=search_label,
                         states=STATE_CHOICES,
                         genre_choices=GENRE_CHOICES)

# GET /venues/:venue_id
@venue_bp.route('/<int:venue_id>')
def show_venue(venue_id):
    """Display details for a specific venue.
    
    Takes venue_id as URL parameter and returns the venue detail page
    with all information about that venue.
    """
    data = VenueService.show_venue_by_venue_id(venue_id=venue_id)
    return render_template('pages/show_venue.html', venue=data)

# GET /venues/create 
@venue_bp.route('/create', methods=['GET'])
def create_venue_form():
    """Display the form to create a new venue.
    
    Returns a blank form that users can fill out to create a new venue.
    """
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form, data={})


# POST /venues/create
@venue_bp.route('/create', methods=['POST'])
def create_venue_submission():
    """Handle venue creation form submission.
    
    Validates the form data, creates the venue in the database,
    and redirects to the venues list on success or redisplays the form on error.
    """
    form = VenueForm(formdata=request.form)
    validation_errors, venue_data = VenueService.validate_venue_form_data(request.form)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                # WTForms expects errors as a tuple/list
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/new_venue.html', form=form, data=request.form)
    
    venue_create_success, venue_fail_reason = VenueService.create_venue(venue_data)
    
    if venue_create_success:
        flash(f"Venue {venue_data.name} was successfully listed!", category='success')
        return redirect(url_for('venues.venues', _external=False))
    else:
        flash(f"Venue could not be listed: {venue_fail_reason}", category='error')
        return render_template('forms/new_venue.html', form=form, error=venue_fail_reason, data=request.form)

# DELETE /venues/:venue_id
@venue_bp.route('/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """Delete a venue by its ID.
    
    Takes venue_id as URL parameter and deletes that venue from the database.
    Returns a JSON response with success or failure status.
    """
    success, error = VenueService.delete_venue(venue_id=venue_id)

    if success:
        return {'success': True, 'message': 'Venue deleted successfully!'}, 200
    else:
        return {'success': False, 'message': error or 'Unable to delete venue'}, 400

# POST /venues/:venue_id/delete
@venue_bp.route('/<int:venue_id>/delete', methods=['POST'])
def delete_venue_post(venue_id):
    """Delete a venue (POST endpoint for form submissions).
    
    Takes venue_id as URL parameter and deletes that venue from the database.
    Redirects back to /venues on success, or back to venue page with error.
    """
    success, error = VenueService.delete_venue(venue_id=venue_id)

    if success:
        flash('Venue successfully deleted!', 'success')
        return redirect('/venues')
    else:
        flash(f'Unable to delete venue: {error}', 'danger')
        return redirect(f'/venues/{venue_id}')

# GET /venues/:venue_id/edit
@venue_bp.route('/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    """Display the form to edit an existing venue.
    
    Takes venue_id as URL parameter, fetches the venue data from the database,
    and returns a form pre-populated with the current venue information.
    """
    # Loads the Venue Data to edit
    form = VenueForm()
    data = VenueService.show_venue_by_venue_id(venue_id=venue_id)
    
    if not data:
        flash(f"Venue with ID {venue_id} not found", category='error')
        return redirect(request.referrer or url_for('venues.venues'))
    
    # Populate form with venue data
    form.name.data = data.get('name')
    form.city.data = data.get('city')
    form.state.data = data.get('state')
    form.address.data = data.get('address')
    form.phone.data = data.get('phone')
    form.image_link.data = data.get('image_link')
    form.genres.data = data.get('genres', [])
    form.facebook_link.data = data.get('facebook_link')
    form.website_link.data = data.get('website')
    form.seeking_talent.data = data.get('seeking_talent', False)
    form.seeking_description.data = data.get('seeking_description')
    
    return render_template('forms/edit_venue.html', form=form, venue=data)

# POST /venues/:venue_id/edit
@venue_bp.route('/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    """Handle venue edit form submission.
    
    Takes venue_id as URL parameter, validates the submitted form data,
    updates the venue in the database, and redirects on success
    or redisplays the form on error.
    """
    form = VenueForm(formdata=request.form)
    venue = VenueService.show_venue_by_venue_id(venue_id=venue_id)
    
    validation_errors, venue_data = VenueService.validate_venue_form_data(request.form)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                # WTForms expects errors as a tuple/list
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    
    venue_edit_success, venue_fail_reason = VenueService.update_venue(venue_id, venue_data)
    
    if venue_edit_success:
        flash(f"Venue {venue_data.name} was successfully updated!", category='success')
        return redirect(url_for('venues.show_venue', venue_id=venue_id))
    else:
        flash(f"Venue could not be updated: {venue_fail_reason}", category='error')
        return render_template('forms/edit_venue.html', form=form, venue=venue, error=venue_fail_reason)

