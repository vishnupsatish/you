import os
import secrets
from flask import url_for
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

def sentiment_analyze(sentiment_text):
    clean_text = sentiment_text.lower().translate(str.maketrans('', '', string.punctuation))
    score = SentimentIntensityAnalyzer().polarity_scores(clean_text)
    negative = score['neg']
    positive = score['pos']
    return positive, negative


