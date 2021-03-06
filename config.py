import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    ADMINS = ['tohnic1999@gmail.com']
    LANGUAGES = ['en']
    MAIL_SERVER = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DAYS_PER_WEEK = 6
    TASK_SCHEDULE_LIMIT = 1 #One Day