# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import logging
import sys
from datetime import datetime
from logging import FileHandler, Formatter

import babel.dates
import dateutil.parser
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from forms import ArtistForm, ShowForm, VenueForm

# ----------------------------------------------------------------------------#
# App Config
# ----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
from models import Artist, Show, Venue, db  # noqa: E0402

db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters
# ----------------------------------------------------------------------------#
def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#
@app.route("/")
def index():
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#
@app.route("/venues")
def venues():
    data = []
    areas = (
        db.session.query(Venue)
        .distinct(Venue.city, Venue.state)
        .order_by(Venue.state, Venue.city)
        .all()
    )
    for area in areas:
        venue_data = []
        venues = (
            db.session.query(Venue)
            .filter_by(city=area.city, state=area.state)
            .order_by(Venue.name)
            .all()
        )
        for venue in venues:
            venue_data.append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": db.session.query(Show)
                    .filter(Show.venue_id == venue.id, Show.start_time > datetime.now())
                    .count(),
                }
            )
        data.append({"city": area.city, "state": area.state, "venues": venue_data})
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    results = db.session.query(Venue).filter(Venue.name.ilike(f"%{search_term}%")).all()
    data = []
    for result in results:
        data.append(
            {
                "id": result.id,
                "name": result.name,
                "num_upcoming_shows": db.session.query(Show)
                .filter(Show.venue_id == result.id, Show.start_time > datetime.now())
                .count(),
            }
        )
    response = {"count": len(results), "data": data}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = db.session.get(Venue, venue_id)
    if not venue:
        return render_template("errors/404.html")
    upcoming_shows_query = (
        db.session.query(Artist, Show)
        .join(Show)
        .filter(Show.venue_id == venue_id, Show.start_time > datetime.now())
        .all()
    )
    upcoming_shows = []
    for artist, show in upcoming_shows_query:
        upcoming_shows.append(
            {
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": format_datetime(str(show.start_time), format="full"),
            }
        )
    past_shows_query = (
        db.session.query(Artist, Show)
        .join(Artist)
        .filter(Show.venue_id == venue_id, Show.start_time < datetime.now())
        .all()
    )
    past_shows = []
    for artist, show in past_shows_query:
        past_shows.append(
            {
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": format_datetime(str(show.start_time), format="full"),
            }
        )
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
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
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_venue.html", venue=data)


# ----------------------------------------------------------------------------#
#  Create Venue
# ----------------------------------------------------------------------------#
@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    error = False
    try:
        name = request.form.get("name", "")
        city = request.form.get("city", "")
        state = request.form.get("state", "")
        address = request.form.get("address", "")
        phone = request.form.get("phone", "")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link", "")
        image_link = request.form.get("image_link", "")
        website = request.form.get("website_link", "")
        seeking_talent = True if "seeking_talent" in request.form else False
        seeking_description = request.form.get("seeking_description", "")
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
        )
        db.session.add(venue)
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # On unsuccessful db insert, flash an error
        flash("An error occurred.  Venue " + request.form.get("name", "") + " could not be listed.")
    else:
        # on successful db insert, flash success
        flash("Venue " + request.form.get("name", "") + " was successfully listed!")
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    try:
        db.session.get(Venue, venue_id).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f"An error occurred.  Venue {venue_id} could not be deleted.")
    if not error:
        flash(f"Venue {venue_id} was successfully deleted.")
    # TODO: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Artists
# ----------------------------------------------------------------------------#
@app.route("/artists")
def artists():
    data = db.session.query(Artist).order_by(Artist.name).all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    results = db.session.query(Artist).filter(Artist.name.ilike(f"%{search_term}%")).all()
    data = []
    for result in results:
        data.append(
            {
                "id": result.id,
                "name": result.name,
                "num_upcoming_shows": db.session.query(Show)
                .filter(Show.venue_id == result.id, Show.start_time > datetime.now())
                .count(),
            }
        )
    response = {"count": len(results), "data": data}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    artist = db.session.get(Artist, artist_id)
    if not artist:
        return render_template("errors/404.html")
    upcoming_shows_query = (
        db.session.query(Venue, Show)
        .join(Show)
        .filter(Show.artist_id == artist_id, Show.start_time > datetime.now())
        .all()
    )
    upcoming_shows = []
    for venue, show in upcoming_shows_query:
        upcoming_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": format_datetime(str(show.start_time), format="full"),
            }
        )
    past_shows_query = (
        db.session.query(Venue, Show)
        .join(Venue)
        .filter(Show.artist_id == artist_id, Show.start_time < datetime.now())
        .all()
    )
    past_shows = []
    for venue, show in past_shows_query:
        past_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": format_datetime(str(show.start_time), format="full"),
            }
        )
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_artist.html", artist=data)


# ----------------------------------------------------------------------------#
#  Update
# ----------------------------------------------------------------------------#
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = db.session.get(Artist, artist_id)
    if artist is not None:
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    error = False
    artist = db.session.get(Artist, artist_id)
    try:
        artist.name = request.form["name"]
        artist.genres = request.form.getlist("genres")
        artist.city = request.form["city"]
        artist.state = request.form["state"]
        artist.phone = request.form["phone"]
        artist.website = request.form["website_link"]
        artist.facebook_link = request.form["facebook_link"]
        artist.seeking_venue = True if "seeking_venue" in request.form else False
        artist.seeking_description = request.form["seeking_description"]
        artist.image_link = request.form["image_link"]
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash("An error occurred.  Artist could not be changed.")
    if not error:
        flash("Artist was successfully updated!")
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.get(Venue, venue_id)
    if venue is not None:
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    error = False
    venue = db.session.get(Venue, venue_id)
    try:
        venue.name = request.form["name"]
        venue.genres = request.form.getlist("genres")
        venue.address = request.form["address"]
        venue.city = request.form["city"]
        venue.state = request.form["state"]
        venue.phone = request.form["phone"]
        venue.website = request.form["website_link"]
        venue.facebook_link = request.form["facebook_link"]
        venue.seeking_talent = True if "seeking_talent" in request.form else False
        venue.seeking_description = request.form["seeking_description"]
        venue.image_link = request.form["image_link"]
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash("An error occurred.  Venue could not be changed.")
    if not error:
        flash("Venue was successfully updated!")
    return redirect(url_for("show_venue", venue_id=venue_id))


# ----------------------------------------------------------------------------#
#  Create Artist
# ----------------------------------------------------------------------------#
@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    error = False
    try:
        name = request.form.get("name", "")
        city = request.form.get("city", "")
        state = request.form.get("state", "")
        phone = request.form.get("phone", "")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link", "")
        image_link = request.form.get("image_link", "")
        website = request.form.get("website_link", "")
        seeking_venue = True if "seeking_venue" in request.form else False
        seeking_description = request.form.get("seeking_description", "")
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(artist)
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # On unsuccessful db insert, flash an error
        flash(
            "An error occurred.  Artist " + request.form.get("name", "") + " could not be listed."
        )
    else:
        # on successful db insert, flash success
        flash("Artist " + request.form.get("name", "") + " was successfully listed!")
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
#  Shows
# ----------------------------------------------------------------------------#
@app.route("/shows")
def shows():
    shows_query = db.session.query(Show, Venue, Artist).join(Venue).join(Artist).all()
    data = []
    for show, venue, artist in shows_query:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    error = False
    try:
        artist_id = request.form.get("artist_id", "")
        venue_id = request.form.get("venue_id", "")
        start_time = request.form.get("start_time", "")
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # On unsuccessful db insert, flash an error
        flash("An error occurred.  Show could not be listed.")
    else:
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
