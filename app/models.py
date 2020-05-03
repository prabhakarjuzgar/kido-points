from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import jwt
from app import db, login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    children = relationship('Child', backref='parent', lazy=True)

    def __repr__(self):
        return '<User {} Email {}>'.format(self.username, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,
                                                                            size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='H256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithm=['H256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    childname = db.Column(db.String(64), index=True)
    parentid = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    activity = relationship('Activity', backref='child')
    target = relationship('Target', backref='child')


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity = db.Column(db.String(128), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False)
#    current = db.Column(db.Integer)
    childid = db.Column(db.Integer, db.ForeignKey(Child.id), nullable=False)


class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.Integer, nullable=False)
    childid = db.Column(db.Integer, db.ForeignKey(Child.id), nullable=False)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
