from datetime import datetime, date
from app import db, login, whooshee
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String, default = 'USER')
    cell_line = db.relationship('CellLines',backref = 'user', lazy= 'dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

@whooshee.register_model('name','running_number','celltype','species','tissue')
class CellLines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    running_number = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(128), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timeedited = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    celltype = db.Column(db.String(128), index=True, unique=False)
    species = db.Column(db.String(128), index=True, unique=False)
    tissue = db.Column(db.String(128), index=True, unique=False)
    genetic_info = db.relationship('Genotype', backref='cell_line', lazy='dynamic', cascade = 'save-update, merge, delete')
    culture_info = db.relationship('CellCulture', backref='cell_line', lazy='dynamic', cascade = 'save-update, merge, delete')
    additional_info = db.relationship('CellLineGeneration', backref='cell_line', lazy='dynamic', cascade = 'save-update, merge, delete')
    stocks = db.relationship('Stocks', backref='cell_line', lazy='dynamic', cascade = 'save-update, merge, delete')

    def __repr__(self):
        return '<CellLine {}>'.format(self.name)


class Stocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cell_line_id = db.Column(db.Integer, db.ForeignKey('cell_lines.id'))
    date = db.Column(db.Date, index=True)
    freezer = db.Column(db.String(128), index=True, unique=False)
    rack = db.Column(db.String(128), index=True, unique=False)
    box = db.Column(db.String(128), index=True, unique=False)
    position = db.Column(db.String(128), index=True, unique=False)
    medium = db.Column(db.String(128), index=True, unique=False)
    passage = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<Stock in freezer {}, rack {}, box {}, position {}>'.format(self.freezer,
        self.rack, self.box, self.position)


class Genotype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cell_line_id = db.Column(db.Integer, db.ForeignKey('cell_lines.id'))
    modmethod = db.Column(db.String(128), index=True, unique=False)
    locus = db.Column(db.String(128), index=True, unique=False)
    tag = db.Column(db.String(128), index=True, unique=False)
    modtype = db.Column(db.String(128), index=True, unique=False)
    mutation = db.Column(db.String(128), index=True, unique=False)
    transgene = db.Column(db.String(128), index=True, unique=False)
    resistance = db.Column(db.String(128), index=True, unique=False)
    inducible = db.Column(db.String(128), index=True, unique=False)

    def __repr__(self):
        return '<Genotype: modification method {}, locus {}>'.format(self.modmethod,
                                                                     self.locus)


class CellCulture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cell_line_id = db.Column(db.Integer, db.ForeignKey('cell_lines.id'))
    bsl = db.Column(db.Integer, index=True)
    mycoplasma = db.Column(db.String(128), index=True, unique=False)
    pcrdate = db.Column(db.Date, index=True)
    culturetype = db.Column(db.String(128), index=True, unique=False)
    medium = db.Column(db.String(128), index=True, unique=False)
    notes = db.Column(db.Text(), index=True, unique=False)

    def __repr__(self):
        return '<Cell cuture condition: BSL {}, Medium {}, Mycoplasma status {}>'.format(self.bsl,
        self.medium, self.mycoplasma)


class CellLineGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cell_line_id = db.Column(db.Integer, db.ForeignKey('cell_lines.id'))
    protocol = db.Column(db.Text(), index=True, unique=False)
    wb = db.Column(db.String(128), index=True, unique=True)
    wb_s = db.Column(db.String(128), index=True, unique=True)
    pcr = db.Column(db.String(128), index=True, unique=True)
    pcr_s = db.Column(db.String(128), index=True, unique=True)
    sequencing_info = db.Column(db.String(128), index=True, unique=True)
    sequencing_info_s = db.Column(db.String(128), index=True, unique=True)
    facs = db.Column(db.String(128), index=True, unique=True)
    facs_s = db.Column(db.String(128), index=True, unique=True)
    description = db.Column(db.Text(), index=True, unique=False)
    comments = db.Column(db.Text(), index=True, unique=False)
    publication = db.Column(db.String(128), index=True, unique=False)

    def __repr__(self):
        return '<Additional information: Protocol {}, Description {}>'.format(
        self.protocol, self.description)
