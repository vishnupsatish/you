from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from application import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    diary_entries = db.relationship('DiaryEntry', backref='user', lazy=True)
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True)
    photos_entries = db.relationship('PhotosEntry', backref='user', lazy=True)
    main_event_entries = db.relationship('MainEventEntry', backref='user', lazy=True)
    goal_entries = db.relationship('GoalEntry', backref='user', lazy=True)


class Year(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)
    months = db.relationship('Month', backref='year', lazy=True)


class Month(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    days = db.relationship('Day', backref='month', lazy=True)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id'), nullable=False)


class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    month_id = db.Column(db.Integer, db.ForeignKey('month.id'), nullable=False)
    diary_entries = db.relationship('DiaryEntry', backref='day', lazy=True)
    mood_entries = db.relationship('MoodEntry', backref='day', lazy=True)
    photos_entries = db.relationship('PhotosEntry', backref='day', lazy=True)
    main_event_entries = db.relationship('MainEventEntry', backref='day', lazy=True)
    goal_entries = db.relationship('GoalEntry', backref='day', lazy=True)


class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    pos = db.Column(db.Float)
    neg = db.Column(db.Float)
    score = db.Column(db.Integer)
    favourite = db.Column(db.Boolean, default=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return 'DiaryEntry'


class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.Integer, nullable=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return 'MoodEntry'


class PhotosEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String, nullable=False)
    caption = db.Column(db.String, nullable=False)
    favourite = db.Column(db.Boolean, default=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return 'PhotosEntry'

class MainEventEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    favourite = db.Column(db.Boolean, default=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return 'MainEventEntry'


## MARK AS RESOLVED: BOOLEANB
class GoalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, nullable=False)
    steps = db.Column(db.String, nullable=True)
    done = db.Column(db.Boolean, nullable=True)
    favourite = db.Column(db.Boolean, default=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return 'GoalEntry'