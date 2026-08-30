from flask import Blueprint, render_template
from services.artist import ArtistService
from services.venue import VenueService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Display the homepage with recent artists and venues."""
    recent_artists = ArtistService.get_recent_artists(limit=10)
    recent_venues = VenueService.get_recent_venues(limit=10)
    
    return render_template('pages/home.html', 
                         recent_artists=recent_artists, 
                         recent_venues=recent_venues)
