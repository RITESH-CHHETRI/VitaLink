from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    websocket_id = db.Column(db.String, unique=True, index=True)
    name = db.Column(db.String(150),unique = True)
    profilepic = db.Column(db.String(100))
    status = db.Column(db.String(20))
    interests = db.Column(db.String(1000),default = None)
    following = db.Column(db.String(1000),default = "")
    followers = db.Column(db.String(1000),default = "")
    logined = db.Column(db.String(10),default = "true")
    otp = db.Column(db.String(10))
    posts = db.relationship('Post')
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    data = db.Column(db.String(10000))
    pic=db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    likes = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    read = db.Column(db.String(10),default='false')
    user_id = db.Column(db.Integer)
    trigid= db.Column(db.Integer)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100))
    message = db.Column(db.String(1000))
    posted = db.Column(db.String(50))
    sender=db.Column(db.String(100))
    read=db.Column(db.String(10),default='false')
