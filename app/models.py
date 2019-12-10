from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.sqlite import BLOB

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # memes = db.relationship('Meme', back_populates="user_id")
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    caption = db.Column(db.String(164), index=True)
    location_id = db.Column(db.String(64), db.ForeignKey('location.id'))
    location = db.relationship("Location", back_populates="memes")
    categories = db.relationship("MemeToCategory", back_populates="meme")
    image_name = db.Column(db.String(164), index=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', back_populates="meme")

    def __repr__(self):
        return '<Meme {}>'.format(self.body)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    memes = db.relationship("Meme", back_populates="location")

    def __repr__(self):
        return '<Location {}>'.format(self.body)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    memes = db.relationship("MemeToCategory", back_populates="category")

    # def __repr__(self):
    #     return '<Category {}>'.format(self.body)


class MemeToCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meme_id = db.Column(db.Integer, db.ForeignKey('meme.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    meme = db.relationship("Meme", back_populates="categories")
    category = db.relationship("Category", back_populates="memes")

    def __repr__(self):
        return '<MemeToCategory {} {}>'.format(self.meme_id, self.category_id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(164), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meme_id = db.Column(db.Integer, db.ForeignKey('meme.id'))
    meme = db.relationship("Meme", back_populates="comments")
    user = db.relationship("User", back_populates="comments")

    def __repr__(self):
        return '<Comment {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))