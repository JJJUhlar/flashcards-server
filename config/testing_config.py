import os

class TestingConfig():
    DEBUG = True
    TESTING = True
    DBHOST= os.environ.get('DBHOST')
    DATABASE = os.environ.get('DATABASE')
    DBUSER = os.environ.get('DBUSER')
    DBPASS = os.environ.get('DBPASS')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    DEFAULT_SESSION_LENGTH = os.environ.get('DEFAULT_SESSION_LENGTH')