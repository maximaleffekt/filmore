from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import current_user

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    roles = db.relationship('Role', backref='owner', lazy=True)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Neu: Metadaten
    film_manufacturer = db.Column(db.String(50))
    film_type = db.Column(db.String(50))
    iso = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images = db.relationship('Image', backref='role', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    shutter_speed = db.Column(db.String(50))
    aperture = db.Column(db.String(50))
    image_file = db.Column(db.String(200))   # optionales Upload
    frame_number = db.Column(db.Integer)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'))
    lens_id = db.Column(db.Integer, db.ForeignKey('lens.id'))
    filter_id = db.Column(db.Integer, db.ForeignKey('filter.id'))
    camera = db.relationship('Camera')
    lens = db.relationship('Lens')
    filter = db.relationship('Filter')

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    brand = db.Column(db.String(120))
    min_shutter_speed = db.Column(db.String(50))
    max_shutter_speed = db.Column(db.String(50))
    seriennummer = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Lens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    focal_length = db.Column(db.String(50))
    aperture = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
