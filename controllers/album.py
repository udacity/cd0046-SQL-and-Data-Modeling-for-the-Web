"""Routes for album management."""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms import AlbumForm
from services.album import AlbumService
from dal import db, Artist
import logging

logger = logging.getLogger(__name__)

album_bp = Blueprint('albums', __name__, url_prefix='/albums')


# GET /albums
@album_bp.route('/', strict_slashes=False)
def albums():
    """Display all albums.
    
    Returns a page with all albums in the database, sorted by release date.
    """
    albums_list = AlbumService.get_all_albums()
    return render_template('pages/albums.html', albums=albums_list)


# GET /albums/<album_id>
@album_bp.route('/<int:album_id>')
def show_album(album_id):
    """Display details for a specific album with all songs.
    
    Takes album_id as URL parameter and returns the album detail page
    with album information and tracklist.
    """
    album = AlbumService.get_album_by_id(album_id)
    
    if not album:
        flash(f"Album with ID {album_id} not found", category='error')
        return redirect(request.referrer or url_for('albums.albums'))
    
    return render_template('pages/album.html', album=album)


# GET /albums/create
@album_bp.route('/create', methods=['GET'])
def create_album_form():
    """Display the form to create a new album.
    
    Accepts optional artist_id query parameter to prefill the artist field.
    Returns the album creation form for user to fill out.
    """
    form = AlbumForm()
    
    # Populate artist dropdown
    artists = Artist.query.all()
    form.artist_id.choices = [(a.id, a.name) for a in artists]
    
    # Check if artist_id is provided as query parameter to prefill
    artist_id = request.args.get('artist_id', type=int)
    artist_name = None
    if artist_id:
        form.artist_id.data = artist_id
        artist = Artist.query.get(artist_id)
        if artist:
            artist_name = artist.name
    
    return render_template('forms/new_album.html', form=form, data={}, artist_id=artist_id, artist_name=artist_name)


# POST /albums/create
@album_bp.route('/create', methods=['POST'])
def create_album_submission():
    """Handle album creation form submission.
    
    Validates the form data, creates the album in the database,
    and redirects to the album detail page on success or redisplays the form on error.
    """
    form = AlbumForm(formdata=request.form)
    
    # Populate choices before validation
    artists = Artist.query.all()
    form.artist_id.choices = [(a.id, a.name) for a in artists]
    
    validation_errors, album_data = AlbumService.validate_album_form_data(request.form)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        # Check if artist_id was submitted (comes from hidden field when created from artist page)
        artist_id = None
        artist_name = None
        if 'artist_id' in request.form:
            try:
                artist_id = int(request.form.get('artist_id'))
                artist = Artist.query.get(artist_id)
                if artist:
                    artist_name = artist.name
            except (ValueError, TypeError):
                pass
        
        return render_template('forms/new_album.html', form=form, data=request.form, artist_id=artist_id, artist_name=artist_name)
    
    album_create_success, album_fail_reason = AlbumService.create_album(album_data)
    
    if album_create_success:
        flash(f"Album '{album_data.title}' was successfully created!", category='success')
        # Redirect to album list for the artist
        return redirect(url_for('artists.show_artist', artist_id=album_data.artist_id))
    else:
        flash(f"Album could not be created: {album_fail_reason}", category='error')
        return render_template('forms/new_album.html', form=form, error=album_fail_reason, data=request.form)


# GET /albums/<album_id>/edit
@album_bp.route('/<int:album_id>/edit', methods=['GET'])
def edit_album(album_id):
    """Display the form to edit an existing album.
    
    Takes album_id as URL parameter, fetches the album data from the database,
    and returns a form pre-populated with the current album information.
    """
    form = AlbumForm()
    album = AlbumService.get_album_by_id(album_id)
    
    if not album:
        flash(f"Album with ID {album_id} not found", category='error')
        return redirect(request.referrer or url_for('albums.albums'))
    
    # Populate artist dropdown
    artists = Artist.query.all()
    form.artist_id.choices = [(a.id, a.name) for a in artists]
    
    # Populate form with album data
    form.title.data = album.title
    form.release_date.data = album.release_date
    form.description.data = album.description
    form.image_link.data = album.image_link
    form.spotify_link.data = album.spotify_link
    form.artist_id.data = album.artist_id
    
    return render_template('forms/edit_album.html', form=form, album=album)


# POST /albums/<album_id>/edit
@album_bp.route('/<int:album_id>/edit', methods=['POST'])
def edit_album_submission(album_id):
    """Handle album edit form submission.
    
    Takes album_id as URL parameter, validates the submitted form data,
    updates the album in the database, and redirects on success
    or redisplays the form on error.
    """
    form = AlbumForm(formdata=request.form)
    album = AlbumService.get_album_by_id(album_id)
    
    if not album:
        flash(f"Album with ID {album_id} not found", category='error')
        return redirect(request.referrer or url_for('albums.albums'))
    
    # Populate artist dropdown
    artists = Artist.query.all()
    form.artist_id.choices = [(a.id, a.name) for a in artists]
    
    validation_errors, album_data = AlbumService.validate_album_form_data(request.form)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/edit_album.html', form=form, album=album)
    
    # Set the ID before updating
    album_data.id = album_id
    
    album_edit_success, album_fail_reason = AlbumService.update_album(album_id, album_data)
    
    if album_edit_success:
        flash(f"Album '{album_data.title}' was successfully updated!", category='success')
        return redirect(url_for('albums.show_album', album_id=album_id))
    else:
        flash(f"Album could not be updated: {album_fail_reason}", category='error')
        return render_template('forms/edit_album.html', form=form, album=album, error=album_fail_reason)


# POST /albums/<album_id>/delete
@album_bp.route('/<int:album_id>/delete', methods=['POST'])
def delete_album(album_id):
    """Delete an album (POST endpoint for form submissions).
    
    Takes album_id as URL parameter and deletes that album from the database.
    Redirects back to albums list on success or back to album page with error.
    """
    album = AlbumService.get_album_by_id(album_id)
    
    if not album:
        flash(f"Album with ID {album_id} not found", category='error')
        return redirect(url_for('albums.albums'))
    
    artist_id = album.artist_id
    success, error = AlbumService.delete_album(album_id)
    
    if success:
        flash('Album successfully deleted!', 'success')
        return redirect(url_for('artists.show_artist', artist_id=artist_id))
    else:
        flash(f'Unable to delete album: {error}', 'danger')
        return redirect(url_for('albums.show_album', album_id=album_id))


# DELETE /albums/<album_id> (JSON endpoint for async deletes)
@album_bp.route('/<int:album_id>', methods=['DELETE'])
def delete_album_json(album_id):
    """Delete an album by its ID (JSON endpoint).
    
    Takes album_id as URL parameter and deletes that album from the database.
    Returns a JSON response with success or failure status.
    """
    success, error = AlbumService.delete_album(album_id)
    
    if success:
        return {'success': True, 'message': 'Album deleted successfully!'}, 200
    else:
        return {'success': False, 'message': error or 'Unable to delete album'}, 400
