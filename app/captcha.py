from PIL import Image, ImageDraw, ImageFont
import random


class Captcha:
    def __init__(self):
        self.lib = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
        self.width = 130
        self.height = 50

    def ColorGenerator(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def TextGenerator(self):
        return ''.join(random.sample(self.lib, 4))

    def CaptchaGenerator(self):
        im = Image.new('RGBA', (self.width, self.height), self.ColorGenerator())
        text = self.TextGenerator()
        font = ImageFont.truetype("MicrosoftYaqiHeiLight-2.ttf", 30)
        draw = ImageDraw.Draw(im)
        font_width, font_height = font.getsize(text)
        draw.text(((self.width-font_width)/2, (self.height-font_height)/2), text, font=font, fill = self.ColorGenerator())
        for i in range(3):
            start = (random.randint(0, self.width), random.randint(0, self.height))
            end = (random.randint(0, self.width), random.randint(0, self.height))
            draw.line([start, end], fill = self.ColorGenerator(), width = 2)
        for w in range(self.width):
            for h in range(self.height):
                tmp = random.randint(0, 100)
                if tmp > 90:
                    draw.point((w, h), fill=self.ColorGenerator())
        return (im, text)
