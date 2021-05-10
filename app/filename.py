from uuid import uuid4
import os

def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid4().hex + ext
    return new_filename
