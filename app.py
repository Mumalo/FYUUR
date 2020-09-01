
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from models import set_up_db, Venue, Artist, Show, db
from flask_wtf.csrf import CSRFProtect

crf = CSRFProtect()

app = Flask(__name__)
# crf.init_app(app)
moment = Moment(app)
set_up_db(app)
csrf_token = app.config["SECRET_KEY"]


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    return render_template('pages/home.html')


@app.route('/venues')
def venues():
    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    data = []
    venue_state_and_city = ''

    for venue in venues:
        upcoming_shows = venue.shows.filter(Show.start_time > now).all()
        if venue_state_and_city == venue.city + venue.state:
            data[len(data) - 1]["venues"].append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows)  # a count of the number of shows
            })
        else:
            venue_state_and_city = venue.city + venue.state
            data.append({
              "city": venue.city,
              "state": venue.state,
              "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
              }]
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form["search_term"]
    found_venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()
    print(found_venues)
    data_list = []
    for venue in found_venues:
        current_venue = {}
        current_venue["id"] = venue.id
        current_venue["name"] = venue.name
        current_venue["num_upcoming_shows"] = len(Show.query.options(db.joinedload(Show.Venue)).\
            filter(Show.venue_id == venue.id).all())
        data_list.append(current_venue)
    response = {
      "count": len(found_venues),
      "data": data_list
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    print(venue)
    data = {}
    if venue:
        past_shows = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id)\
            .filter(Show.start_time <= now).all()
        upcoming_shows = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id)\
            .filter(Show.start_time > now).all()
        data = venue.show_details()
        data["past_shows"] = list(map(Show.show_artist, past_shows))
        data["upcoming_shows"] = list(map(Show.show_artist, upcoming_shows))
        data["past_shows_count"] = len(past_shows)
        data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET', 'POST'])
def create_venues():
    form = VenueForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data_dict = request.form
            venue = Venue(data_dict)
            result = venue.save(new=True)
            if not result["success"]:
                flash('An error occured while creating venue {}'.format(data_dict['name']))
            else:
                flash('venue created successfully')
                return render_template('pages/home.html')
        else:
            flash('invalid data submitted')
            return render_template('forms/new_venue.html', form=form)
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.get(venue_id)
    if venue:
        result = Venue.delete(venue)
        if not result['success']:
            flash('error deleting venue with id {}'.format(venue_id))
        else:
            flash('successfully removed venue {}'.format(venue_id))
    return None


@app.route('/artists')
def artists():
    data = list(map(Artist.show_details, Artist.query.all()))
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    found_artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    response = {
      "count": len(found_artists),
      "data": [{
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist.id).filter(
          Show.start_time > now).all()),
      }
        for artist in found_artists
      ]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = {}
    if artist:
        upcoming_shows = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(
          Show.start_time > now).all()
        past_shows = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(
          Show.start_time < now).all()
        data = artist.show_details()
        data['past_shows'] = [show.show_venue() for show in past_shows]
        data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['GET, POST'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist:
        form = ArtistForm(formdata=request.form, obj=artist)
        if request.method == 'GET':
            return render_template('forms/edit_artist.html', form=form, artist=artist)
        elif request.method == 'POST' and form.validate():
            form.populate_obj(artist)
            artist.save(new=False)
            return redirect(url_for('show_artist', artist_id=artist_id))
    return render_template('errors/404.html'), 404


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        form = VenueForm(formdata=request.form, obj=venue)
        if request.method == 'POST':
            form.populate_obj(venue)
            venue.save(new=False)
            return redirect(url_for('show_venue', venue_id=venue_id))
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    return render_template('errors/404.html'), 404


@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist():
    form = ArtistForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            print(request.form)
            artist = Artist(request.form)
            result = artist.save(new=True)
            print(result)
            if not result['success']:
                flash('error saving artist {}'.format(request.form['name']))
                return render_template('forms/new_artist.html', form=form)
            else:
                flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        flash('some values submitted were incorrect')
        return render_template('forms/new_artist.html', form=form)
    return render_template('forms/new_artist.html', form=form)


@app.route('/shows')
def shows():
    shows_list = Show.query.all()
    data = [show.show_details() for show in shows_list]
    print(data)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET', 'POST'])
def create_shows():
    form = ShowForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            show = Show(request.form)
            result = show.save(new=True)
            if not result['success']:
                flash('error creating new show')
                return render_template('forms/new_show.html', form=form)
            else:
                flash('Show was successfully listed!')
                return render_template('pages/home.html')
        flash('some values submitted were incorrect')
        return render_template('forms/new_show.html', form=form)
    return render_template('forms/new_show.html', form=form)


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
