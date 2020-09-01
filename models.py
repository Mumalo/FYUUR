from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()
import sys

def set_up_db(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    return db


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def __init__(self, obj_dict):
        self.name = obj_dict['name']
        self.city = obj_dict['city']
        self.state = obj_dict['state']
        self.address = obj_dict['address']
        self.phone = obj_dict['phone']
        self.facebook_link = obj_dict['facebook_link']
        self.genres = obj_dict.getlist('genres')
        self.description = obj_dict['seeking_description']
        self.image_link = obj_dict['image_link']
        self.website = obj_dict['website']
        self.seeking_talent = obj_dict['seeking_talent'] == 'y'

    def show_details(self):
        return {
            'id': self.id,
            'name': self.city,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'webiste': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.description,
            'image_link': self.image_link,
        }

    def save(self, new=True):
        success = True
        try:
            if new:
                db.session.add(self)
            db.session.commit()
        except:
            print(sys.exc_info())
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        return {'success':  success}

    def delete(self):
        success = True
        try:
            db.session.delete(self)
        except:
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        return {'success': success}


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(140), default=' ')
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __init__(self, object_dict):
        self.name = object_dict['name']
        self.city = object_dict['city']
        self.phone = object_dict['phone']
        self.genres = object_dict.getlist('genres')
        self.facebook_link = object_dict['facebook_link']
        self.state = object_dict['state']
        self.image_link = object_dict['image_link']
        self.seeking_venue = object_dict['seeking_venue'] == 'y'
        self.seeking_description = object_dict['seeking_description']
        self.website = object_dict['website']
        self.image_link = object_dict['image_link']


    def show_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        }

    def save(self, new=True):
        success = True
        try:
            if new:
                db.session.add(self)
            db.session.commit()
        except:
            print(sys.exc_info())
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        return {'success': success}



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.String(), nullable=False)

    def __init__(self, object_dict):
        self.venue_id = object_dict['venue_id']
        self.artist_id = object_dict['artist_id']
        self.start_time = object_dict['start_time']

    def show_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def show_artist(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def show_venue(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image': self.Venue.image_link,
            'start_time': self.start_time
        }

    def save(self, new=True):
        success = True
        try:
            if new:
                db.session.add(self)
            db.session.commit()
        except:
            print(sys.exc_info())
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        return {'success':  success}





#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#