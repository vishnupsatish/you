import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from application import app, db, bcrypt, admin
from application.forms import *
from application.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Year, db.session))
admin.add_view(ModelView(Month, db.session))
admin.add_view(ModelView(Day, db.session))
admin.add_view(ModelView(DiaryEntry, db.session))
admin.add_view(ModelView(MoodEntry, db.session))
admin.add_view(ModelView(GooglePhotosEntry, db.session))
admin.add_view(ModelView(MainEventEntry, db.session))
admin.add_view(ModelView(GoalEntry, db.session))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect('home')
        else:
            flash('Incorrect password or user not found.', 'danger')
            return redirect('login')
    return render_template('login.html', form=form)


@app.route("/")
@app.route("/home")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    years = Year.query.all().order_by(number)
    return render_template('home.html', title="Home")


@app.route("/<int:year>/months")
def month(year):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('month.html', title="Month")


@app.route("/month_summary")
def month_summary():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('month_summary.html', title="Month Summary")


@app.route("/entry_home")
def entry_home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('entry_home.html', title="Entry Home")


@app.route("/day")
def day():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('day.html', title="Day")


@app.route("/new_diary_entry")
def new_diary_entry():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = NewDiaryEntryForm()
    return render_template('new_diary_entry.html', title="New Diary Entry", form=form)

@app.route("/add_goal_entry")
def add_goal_entry():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = NewGoalForm()
    return render_template('add_goal_entry.html', title="New Goal Entry", form=form)