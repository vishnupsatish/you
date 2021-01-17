import os
import secrets
from flask import url_for
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string
import datetime
from flask_login import current_user

def generate_file_name(form_picture):
    file_name = str()
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-").replace(' ', "-") + str(current_user.id) + str(secrets.token_hex(8)) +"-img"
    return file_name
    
def sentiment_analyze(sentiment_text):
    clean_text = sentiment_text.lower().translate(str.maketrans('', '', string.punctuation))
    score = SentimentIntensityAnalyzer().polarity_scores(clean_text)
    negative = score['neg']
    positive = score['pos']
    return positive, negative


