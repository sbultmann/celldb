import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WHOOSHEE_MIN_STRING_LEN = 2
    # This is the directory that flask-file-upload saves files to. Make sure the UPLOAD_FOLDER is the same as Flasks's static_folder or a child. For example:
    UPLOAD_FOLDER = os.path.join(basedir, "static/uploads")
    CSV_FOLDER = os.path.join(basedir, "static/csv")
    # Other FLASK config varaibles ...
    ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb
    CELLLINES_PER_PAGE = 10
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    '''
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='cellDB'
    MAIL_PASSWORD= os.getenv('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER=('CellDB','noreply@celldb.com')
    '''
