import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'I-want-to-graduate-on-time'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # This is the directory that flask-file-upload saves files to. Make sure the UPLOAD_FOLDER is the same as Flasks's static_folder or a child. For example:
    UPLOAD_FOLDER = os.path.join(basedir, "static/uploads")

    # Other FLASK config varaibles ...
    ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb
    CELLLINES_PER_PAGE = 10
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
