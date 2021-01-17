import os
import secrets
from random import shuffle
import datetime
import cv2
import numpy as np
import pytesseract
from flask import render_template, url_for, flash, redirect, request, abort, session
from application import app, db, bcrypt, admin
import cloudinary.api
import cloudinary.uploader
from application.forms import *
from application.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView
from application.utils import *

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Year, db.session))
admin.add_view(ModelView(Month, db.session))
admin.add_view(ModelView(Day, db.session))
admin.add_view(ModelView(DiaryEntry, db.session))
admin.add_view(ModelView(MoodEntry, db.session))
admin.add_view(ModelView(PhotosEntry, db.session))
admin.add_view(ModelView(MainEventEntry, db.session))
admin.add_view(ModelView(GoalEntry, db.session))


@app.context_processor
def inject_date():
    date = datetime.datetime.today()
    return dict(every_all_year=date.year, every_all_month=date.strftime("%B"), every_all_day=date.strftime('%d'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data,
                    password=hashed_password)
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

    months = list(Month.query.order_by(
        Month.number).filter((Month.year.has(name=year))))

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

    month_object = Month.query.order_by(Month.number).filter(
        (Month.year.has(name=year)), Month.name == month).first()
    print(month_object)
    days = list(Day.query.order_by(Day.date).filter_by(month=month_object))

    print(days)
    ordinals = []

    for d in days:
        ordinals.append(ordinal(d.date))

    return render_template('day.html', title="Days", days=days, ordinals=ordinals)


@app.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    diary_entries = list(DiaryEntry.query.filter_by(
        user=current_user, favourite=True).all())
    photo_entries = list(PhotosEntry.query.filter_by(
        user=current_user, favourite=True).all())
    goal_entries = list(GoalEntry.query.filter_by(
        user=current_user, favourite=True).all())
    main_event_entries = list(MainEventEntry.query.filter_by(
        user=current_user, favourite=True).all())

    all_entries = main_event_entries + \
        photo_entries + diary_entries

    left_side = []

    right_side = []
    for i, entry in enumerate(all_entries):
        c = entry
        if i % 2 == 0:
            if i % 4 == 0:
                left_side.append((entry, 'background-1', c))
            elif i % 4 == 2:
                left_side.append((entry, 'background-3', c))
        else:
            if i % 4 == 1:
                right_side.append((entry, 'background-3', c))
            elif i % 4 == 3:
                right_side.append((entry, 'background-4', c))

    date = datetime.datetime.today()

    month = Month.query.order_by(Month.number).filter((Month.year.has(name=date.year))).first()

    month_diary_entries = list(DiaryEntry.query.filter(
        DiaryEntry.user==current_user, DiaryEntry.favourite==True, DiaryEntry.day.has(month_id=month.id)))


    neg = [d.neg for d in month_diary_entries]
    pos = [d.pos for d in month_diary_entries]
    negative = sum(neg) / len(neg)
    positive = sum(pos) / len(pos)

    score = 3

    pos_or_neg = 'Positive' if positive > negative else 'Negative'
    if positive == negative:
        pos_or_neg = 'Neutral'

    difference = abs(positive - negative)

    if positive > negative:
        if difference > 0.5:
            score = 5
        elif difference > 0.2:
            score = 4
    elif negative > positive:
        if difference > 0.5:
            score = 1
        elif difference > 0.2:
            score = 2

    return render_template('month_summary.html', title="Month Summary", left_side=left_side, right_side=right_side, score=score, goal_entries=goal_entries)


@app.route("/entry_home", methods=["GET", "POST"])
def entry_home():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('entry_home.html', title="Entry Home")


@app.route("/new_diary_entry", methods=['GET', 'POST'])
def new_diary_entry():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    date = request.args.get('date')
    if not date:
        today = datetime.datetime.today()
        date = today.strftime('%B/%d/%Y')

    text = request.args.get('text')
    if not text:
        text = ''

    session['diary_entry_date'] = date

    form = NewDiaryEntryForm()
    if form.validate_on_submit():
        mood_eval = sentiment_analyze(form.text.data)
        positive = mood_eval[0]
        negative = mood_eval[1]

        month, day, year = session['diary_entry_date'].split('/')

        month_object = Month.query.order_by(Month.number).filter(
            (Month.year.has(name=year)), Month.name == month).first()
        day = Day.query.filter_by(month=month_object, date=day).first()

        score = 3

        pos_or_neg = 'Positive' if positive > negative else 'Negative'
        if positive == negative:
            pos_or_neg = 'Neutral'

        difference = abs(positive - negative)

        if positive > negative:
            if difference > 0.5:
                score = 5
            elif difference > 0.2:
                score = 4
        elif negative > positive:
            if difference > 0.5:
                score = 1
            elif difference > 0.2:
                score = 2

        print(positive, negative, score, difference, pos_or_neg)

        diary_entry = DiaryEntry(title=form.title.data, content=form.text.data, pos=positive,
                                 neg=negative, day=day, score=score, user=current_user, favourite=form.favourite.data)
        db.session.add(diary_entry)
        db.session.commit()
        flash("Diary entry created successfully.", "success")
        return redirect(url_for("specific_day", year=year, month=month, day=day.date))
    form.text.data = text

    return render_template('new_diary_entry.html', title="New Diary Entry", form=form)


@app.route('/new_diary_entry_ocr', methods=['GET', 'POST'])
def new_diary_entry_ocr():
    date = request.args.get('date')
    form = NewDiaryEntryOCRForm()
    if not date:
        today = datetime.datetime.today()
        date = today.strftime('%B/%d/%Y')
    session['new_diary_entry_ocr'] = date
    if form.validate_on_submit():
        image = form.image.data.read()

        nparr = np.fromstring(image, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        invert = 255 - opening
        data = pytesseract.image_to_string(invert, lang='eng', config='--psm 6')
        return redirect(url_for('new_diary_entry', text=data))


    return render_template('new_diary_entry_ocr.html', title="OCR Diary Entry", form=form)



@app.route("/add_goal_entry", methods=["GET", "POST"])
def add_goal_entry():
    date = request.args.get('date')
    if not date:
        today = datetime.datetime.today()
        date = today.strftime('%B/%d/%Y')
    session['goal_entry_date'] = date
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = NewGoalForm()
    if form.validate_on_submit():
        month, day, year = session['goal_entry_date'].split('/')

        month_object = Month.query.order_by(Month.number).filter(
            (Month.year.has(name=year)), Month.name == month).first()
        day = Day.query.filter_by(month=month_object, date=day).first()

        goal = GoalEntry(goal=form.goal.data, steps=form.steps.data,
                         user_id=current_user.id, day_id=day.id, favourite=form.favourite.data)
        db.session.add(goal)
        db.session.commit()
        flash("Goal entry created successfully.", "success")
        return redirect(url_for("specific_day", year=year, month=month, day=day.date))
    return render_template('add_goal_entry.html', title="New Goal Entry", form=form)


@app.route("/<int:year>/month/<string:month>/day/<int:day>", methods=["GET", "POST"])
def specific_day(year, month, day):

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    month_object = Month.query.order_by(Month.number).filter(
        (Month.year.has(name=year)), Month.name == month).first()
    day = Day.query.filter_by(month=month_object, date=day).first()

    if request.method == "POST":
        mood_rating = 0
        if request.form.get("1"):
            mood_rating = 1
        elif request.form.get("2"):
            mood_rating = 2
        elif request.form.get("3"):
            mood_rating = 3
        elif request.form.get("4"):
            mood_rating = 4
        elif request.form.get("5"):
            mood_rating = 5

        try:
            mood_entry = MoodEntry.query.filter_by(
                user=current_user, day=day).all()[0]
        except:
            mood_entry = MoodEntry(user=current_user, day=day)
            db.session.add(mood_entry)

        mood_entry.mood = mood_rating
        db.session.commit()

        flash('Your mood has been tracked!', 'success')
        return redirect(url_for('specific_day', year=year, month=month, day=day.date))

    diary_entries = list(DiaryEntry.query.filter_by(
        user=current_user, day=day).all())
    mood_entries = list(MoodEntry.query.filter_by(
        user=current_user, day=day).all())
    photo_entries = list(PhotosEntry.query.filter_by(
        user=current_user, day=day).all())
    goal_entries = list(GoalEntry.query.filter_by(
        user=current_user, day=day).all())
    main_event_entries = list(MainEventEntry.query.filter_by(
        user=current_user, day=day).all())

    all_entries = main_event_entries + mood_entries + \
        photo_entries + goal_entries + diary_entries

    left_side = []

    right_side = []
    for i, entry in enumerate(all_entries):
        c = entry
        if i % 2 == 0:
            if i % 6 == 0:
                left_side.append((entry, 'background-1', c))
            elif i % 6 == 2:
                left_side.append((entry, 'background-3', c))
            elif i % 6 == 4:
                left_side.append((entry, 'background-5', c))
        else:
            if i % 6 == 1:
                right_side.append((entry, 'background-3', c))
            elif i % 6 == 3:
                right_side.append((entry, 'background-4', c))
            elif i % 6 == 5:
                right_side.append((entry, 'background-6', c))

    return render_template('specific_day.html', title="Day", day=day, left_side=left_side, right_side=right_side)


@app.route('/add_photo_entry', methods=["GET", "POST"])
def add_photo_entry():
    date = request.args.get('date')
    if not date:
        today = datetime.datetime.today()
        date = today.strftime('%B/%d/%Y')
    session['photo_entry_date'] = date
    form = NewPictureEntryForm()
    if form.validate_on_submit():
        month, day, year = session['photo_entry_date'].split('/')

        month_object = Month.query.order_by(Month.number).filter(
            (Month.year.has(name=year)), Month.name == month).first()
        day = Day.query.filter_by(month=month_object, date=day).first()

        picture_fn = generate_file_name(form.image.data)
        picture_path = f"you/user-photos/{picture_fn}"
        cloudinary.uploader.upload(form.image.data, public_id=picture_path)

        photo_entry = PhotosEntry(
            photo=picture_path, caption=form.caption.data, day_id=day.id, user_id=current_user.id, favourite=form.favourite.data)
        db.session.add(photo_entry)
        db.session.commit()
        flash('Image uploaded successfully.', "success")
        return redirect(url_for('specific_day', year=year, month=month, day=day.date))
    return render_template("add_photo_entry.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/main_event', methods=['GET', 'POST'])
def main_event():
    form = MainEventsForm()

    date = request.args.get('date')
    if not date:
        today = datetime.datetime.today()
        date = today.strftime('%B/%d/%Y')
    session['main_event_entry_date'] = date

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if form.validate_on_submit():
        month, day, year = session['main_event_entry_date'].split('/')

        month_object = Month.query.order_by(Month.number).filter(
            (Month.year.has(name=year)), Month.name == month).first()
        day_object = Day.query.filter_by(month=month_object, date=day).first()

        entry = MainEventEntry(
            content=form.event.data, description=form.description.data, day=day_object, user=current_user, favourite=form.favourite.data)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('specific_day', year=year, month=month, day=day))
    return render_template('main_event.html', title="Month Event", form=form)
