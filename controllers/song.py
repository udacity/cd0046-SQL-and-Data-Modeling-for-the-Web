"""Routes for song management."""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from forms import SongForm
from services.song import SongService
from services.album import AlbumService
from dal import db, Album
import logging

logger = logging.getLogger(__name__)

song_bp = Blueprint('songs', __name__, url_prefix='/songs')


# GET /albums/<album_id>/songs/create
@song_bp.route('/create', methods=['GET'])
def create_song_form():
    """Display the form to create a new song.
    
    Accepts album_id query parameter (required) to specify which album the song belongs to.
    Returns the song creation form for user to fill out.
    """
    album_id = request.args.get('album_id', type=int)
    
    if not album_id:
        flash("Album ID is required to create a song", category='error')
        return redirect(url_for('albums.albums'))
    
    album = AlbumService.get_album_by_id(album_id)
    
    if not album:
        flash(f"Album with ID {album_id} not found", category='error')
        return redirect(url_for('albums.albums'))
    
    form = SongForm()
    return render_template('forms/new_song.html', form=form, album=album, data={})


# POST /albums/<album_id>/songs/create
@song_bp.route('/create', methods=['POST'])
def create_song_submission():
    """Handle song creation form submission.
    
    Validates the form data, creates the song in the database,
    and redirects to the album detail page on success or redisplays the form on error.
    """
    album_id = request.form.get('album_id', type=int)
    
    if not album_id:
        flash("Album ID is required to create a song", category='error')
        return redirect(url_for('albums.albums'))
    
    album = AlbumService.get_album_by_id(album_id)
    
    if not album:
        flash(f"Album with ID {album_id} not found", category='error')
        return redirect(url_for('albums.albums'))
    
    form = SongForm(formdata=request.form)
    
    validation_errors, song_data = SongService.validate_song_form_data(request.form, album_id)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/new_song.html', form=form, album=album, data=request.form)
    
    song_create_success, song_fail_reason = SongService.create_song(song_data)
    
    if song_create_success:
        flash(f"Song '{song_data.title}' was successfully added to the album!", category='success')
        return redirect(url_for('albums.show_album', album_id=album_id))
    else:
        flash(f"Song could not be created: {song_fail_reason}", category='error')
        return render_template('forms/new_song.html', form=form, album=album, error=song_fail_reason, data=request.form)


# GET /songs/<song_id>/edit
@song_bp.route('/<int:song_id>/edit', methods=['GET'])
def edit_song(song_id):
    """Display the form to edit an existing song.
    
    Takes song_id as URL parameter, fetches the song data from the database,
    and returns a form pre-populated with the current song information.
    """
    form = SongForm()
    song = SongService.get_song_by_id(song_id)
    
    if not song:
        flash(f"Song with ID {song_id} not found", category='error')
        return redirect(request.referrer or url_for('albums.albums'))
    
    album = AlbumService.get_album_by_id(song.album_id)
    
    if not album:
        flash(f"Album with ID {song.album_id} not found", category='error')
        return redirect(url_for('albums.albums'))
    
    # Populate form with song data
    form.title.data = song.title
    form.track_number.data = song.track_number
    form.duration.data = song.duration
    form.genre.data = song.genre
    form.spotify_link.data = song.spotify_link
    
    return render_template('forms/edit_song.html', form=form, song=song, album=album)


# POST /songs/<song_id>/edit
@song_bp.route('/<int:song_id>/edit', methods=['POST'])
def edit_song_submission(song_id):
    """Handle song edit form submission.
    
    Takes song_id as URL parameter, validates the submitted form data,
    updates the song in the database, and redirects on success
    or redisplays the form on error.
    """
    form = SongForm(formdata=request.form)
    song = SongService.get_song_by_id(song_id)
    
    if not song:
        flash(f"Song with ID {song_id} not found", category='error')
        return redirect(request.referrer or url_for('albums.albums'))
    
    album = AlbumService.get_album_by_id(song.album_id)
    
    if not album:
        flash(f"Album with ID {song.album_id} not found", category='error')
        return redirect(url_for('albums.albums'))
    
    validation_errors, song_data = SongService.validate_song_form_data(request.form, song.album_id)
    
    if validation_errors:
        # Populate form field errors from validation errors dict
        for field_name, error_message in validation_errors.items():
            if field_name != 'general' and hasattr(form, field_name):
                form[field_name].errors = (error_message,)
            elif field_name == 'general':
                flash(error_message, category='error')
        
        return render_template('forms/edit_song.html', form=form, song=song, album=album)
    
    # Set the ID before updating
    song_data.id = song_id
    
    song_edit_success, song_fail_reason = SongService.update_song(song_id, song_data)
    
    if song_edit_success:
        flash(f"Song '{song_data.title}' was successfully updated!", category='success')
        return redirect(url_for('albums.show_album', album_id=song.album_id))
    else:
        flash(f"Song could not be updated: {song_fail_reason}", category='error')
        return render_template('forms/edit_song.html', form=form, song=song, album=album, error=song_fail_reason)


# POST /songs/<song_id>/delete
@song_bp.route('/<int:song_id>/delete', methods=['POST'])
def delete_song(song_id):
    """Delete a song (POST endpoint for form submissions).
    
    Takes song_id as URL parameter and deletes that song from the database.
    Redirects back to album page on success or back to album page with error.
    """
    song = SongService.get_song_by_id(song_id)
    
    if not song:
        flash(f"Song with ID {song_id} not found", category='error')
        return redirect(url_for('albums.albums'))
    
    album_id = song.album_id
    success, error = SongService.delete_song(song_id)
    
    if success:
        flash('Song successfully deleted!', 'success')
        return redirect(url_for('albums.show_album', album_id=album_id))
    else:
        flash(f'Unable to delete song: {error}', 'danger')
        return redirect(url_for('albums.show_album', album_id=album_id))


# DELETE /songs/<song_id> (JSON endpoint for async deletes)
@song_bp.route('/<int:song_id>', methods=['DELETE'])
def delete_song_json(song_id):
    """Delete a song by its ID (JSON endpoint).
    
    Takes song_id as URL parameter and deletes that song from the database.
    Returns a JSON response with success or failure status.
    """
    success, error = SongService.delete_song(song_id)
    
    if success:
        return {'success': True, 'message': 'Song deleted successfully!'}, 200
    else:
        return {'success': False, 'message': error or 'Unable to delete song'}, 400
