from PIL import Image
import os
from app import app


def resize_image(image, filename, target_width):
    img = Image.open(image)
    filename, extension = os.path.splitext(filename)
    if img.size[0] <= target_width:
        img.save(os.path.join(app.config['UPLOAD_FOLDER'],(filename+'_s'+extension)))
        return filename+'_s'+extension
    w_percent = (target_width/float(img.size[0]))
    height = int(float(img.size[1])*w_percent)
    img = img.resize((target_width, height), Image.ANTIALIAS)
    img.save(os.path.join(app.config['UPLOAD_FOLDER'],(filename+'_s'+extension)))
    return filename+'_s'+extension
