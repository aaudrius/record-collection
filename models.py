from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    collections = db.relationship('UserCollection', backref='user', lazy=True)

class UserCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    release_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    cover_image = db.Column(db.String(200))
    year = db.Column(db.String(20))
    country = db.Column(db.String(20))
    selected_label = db.Column(db.String(200))
    format = db.Column(db.String(200))
    spotify_album_id = db.Column(db.String(200), nullable=True)

followees = db.Table('followees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followee_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

User.followees = db.relationship('User',
                               secondary=followees,
                               primaryjoin=(User.id == followees.c.user_id),
                               secondaryjoin=(User.id == followees.c.followee_id),
                               lazy='dynamic')
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
