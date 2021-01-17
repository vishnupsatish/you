import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView
import cloudinary

app = Flask(__name__)
app.config['SECRET_KEY'] = '4387cr6bi23bxy4rd3erft34yuxt23ju7tr'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
admin = Admin(app=app, url="/flask-admin")

cloudinary.config(
    cloud_name = "dnwczwamg", 
    api_key = "778543234586879", 
    api_secret = "S1OSxuJqxBkpDSkwbxBoTLVgiw0" )


from application import routes
