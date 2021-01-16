from application import db
from datetime import datetime, timedelta
from application.models import *



numdays = 18644
base = datetime.today()
date_list = [base - timedelta(days=x) for x in range(numdays)]

for d in date_list:
    year = d.year
    month = d.month
    month_name = d.strftime('%B')
    day = d.day
    day_name = d.strftime("%A")
    
    current_year = Year.query.filter_by(name=year).first()
    if not bool(current_year):
        current_year = Year(name=year)
        db.session.add(current_year)

    current_month = Month.query.filter_by(number=month, year=current_year).first()
    if not bool(current_month):
        current_month = Month(number=month, name=month_name, year=current_year)
        db.session.add(current_month)

    current_day = Day.query.filter_by(date=day, month=current_month).first()
    if not bool(current_day):
        current_day = Day(date=day, name=day_name, month=current_month)
        db.session.add(current_day)


user = User(email='a@a.a', name='Aa Aa', password='$2y$12$fHlljwgC0PwI2yn8BStzkOnDDAfGIeeg5Y9bubqIa1ENTc9S0ywE2')
db.session.add(user)

db.session.commit()





