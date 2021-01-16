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

    years = list(Year.query.order_by(Year.name.desc()).all())
    return render_template('home.html', title="Home", years=years)


@app.route("/<int:year>/months")
def months(year):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    months = list(Month.query.order_by(Month.number).filter((Month.year.has(name=year))))

    return render_template('month.html', title="Months", months=months)


SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix


@app.route("/<int:year>/month/<string:month>/days")
def day(year, month):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    month_object = Month.query.order_by(Month.number).filter((Month.year.has(name=year)), Month.name==month).first()
    print(month_object)
    days = list(Day.query.order_by(Day.date).filter_by(month=month_object))

    print(days)
    ordinals = []

    for d in days:
        ordinals.append(ordinal(d.date))


    return render_template('day.html', title="Days", days=days, ordinals=ordinals)


@app.route("/month_summary")
def month_summary():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('month_summary.html', title="Month Summary")


@app.route("/entry_home", methods=["GET", "POST"])
def entry_home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('entry_home.html', title="Entry Home")





@app.route("/new_diary_entry", methods=['GET', 'POST'])
def new_diary_entry():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # date = request.args.get('date')
    # if not date:
    #     date = 

    form = NewDiaryEntryForm()
    if form.validate_on_submit():
        diary_entry = DiaryEntry(title=form.title.data, content=form.text.data)
        db.session.add(diary_entry)
        db.session.commit()
        flash("Diary entry created successfully.", "is-success")
        return redirect(url_for("home"))
    return render_template('new_diary_entry.html', title="New Diary Entry", form=form)

@app.route("/add_goal_entry")
def add_goal_entry():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = NewGoalForm()
    return render_template('add_goal_entry.html', title="New Goal Entry", form=form)


@app.route("/<int:year>/month/<string:month>/day/<int:day>")
def specfic_day(year, month, day):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    month_object = Month.query.order_by(Month.number).filter((Month.year.has(name=year)), Month.name==month).first()
    print(month_object)
    day = Day.query.filter_by(month=month_object, date=day).first()

    print(day)


    return render_template('specific_day.html', title="Day", day=day)