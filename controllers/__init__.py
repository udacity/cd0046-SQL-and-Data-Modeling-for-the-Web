from flask import Blueprint
from controllers.main import main_bp
from controllers.venue import venue_bp
from controllers.artist import artist_bp
from controllers.show import show_bp

__all__ = ['main_bp', 'venue_bp', 'artist_bp', 'show_bp']
