import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from application import app, db, bcrypt
from application.forms import *
from application.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

