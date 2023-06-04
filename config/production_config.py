import os

class ProductionConfig():
    DEBUG = True
    TESTING = True
    DBHOST= os.environ.get('DBHOST')
    DATABASE = os.environ.get('DATABASE')
    DBUSER = os.environ.get('DBUSER')
    DBPASS = os.environ.get('DBPASS')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEFAULT_SESSION_LENGTH = os.environ.get('DEFAULT_SESSION_LENGTH')

