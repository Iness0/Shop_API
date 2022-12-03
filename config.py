import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    PROPAGATE_EXCEPTIONS = True
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    UPLOADED_IMAGES_DEST = os.path.join("static", "images")


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
