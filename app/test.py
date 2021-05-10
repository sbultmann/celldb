import random
class person:
    def __init__(self):
        self.name = 'bbb'
        self.age = 23

    def year_of_birth(self):
        return 2021-self.age

    def show(self):
        return (self.name, self.age, self.year_of_birth())


p1 = person()
r = p1.show()
print(r)


class Color:
    def __init__(self):
        self.lib = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
        self.width = 130
        self.height = 50

    def Col(self):
        #random.seed()
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


c = Color()
print(c.Col())
