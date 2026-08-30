#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template
from flask_moment import Moment
from forms import *
from services.common import CommonService
from controllers import main_bp, venue_bp, artist_bp, show_bp
from controllers.album import album_bp
from controllers.song import song_bp
from logging_config import configure_logging

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
CommonService.init_db(app)
migrate = CommonService.migrate_db(app)

# Configure logging
logger = configure_logging(app)

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
# Register Blueprints
#----------------------------------------------------------------------------#

app.register_blueprint(main_bp)
app.register_blueprint(venue_bp)
app.register_blueprint(artist_bp)
app.register_blueprint(show_bp)
app.register_blueprint(album_bp)
app.register_blueprint(song_bp)

#----------------------------------------------------------------------------#
# Error Handlers & CLI
#----------------------------------------------------------------------------#

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.cli.command()
def seed_db():
    """Seed database with test data (development/testing only)."""
    from test_helpers.seed import seed_database
    success, message = seed_database()
    print(message)


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
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
