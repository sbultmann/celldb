from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, FormField, IntegerField
from wtforms.validators import DataRequired, NoneOf, AnyOf, ValidationError, EqualTo, Email
from app import db
from app.models import User, CellLines

def pick_option(form, field):
    print(field.data)
    if field.data == "Choose":
        raise ValidationError('Please choose an option')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class BasicInfo(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    celltype = StringField('Cell type', validators=[DataRequired()])
    species = SelectField('Species', validators=[NoneOf(values=["Choose"])],
                            choices=[('Choose', 'Choose'),('Mouse', 'Mouse'), ('Human', 'Human'), ('Hamster', 'Hamster'), ('Drosophila', 'Drosophila')])
    tissue = StringField('Tissue', validators=[DataRequired()])
    running_number = StringField("Running number", validators=[DataRequired()])

    def validate_name(self, name):
        name = CellLines.query.filter_by(name=name.data).first()
        if name is not None:
            raise ValidationError('The name is already exsited.')

    def validate_running_number(self, running_number):
        name = CellLines.query.filter_by(running_number=running_number.data).first()
        if name is not None:
            raise ValidationError('The running_number is already exsited.')

class GeneticInfo(FlaskForm):
    modmethod = StringField('Modification method', validators=[DataRequired()])
    locus = StringField('Locus/Gene', validators=[DataRequired()])
    tag = StringField('Epitope tag', validators=[DataRequired()])
    modtype = SelectField('Modification type', choices=[('Choose', 'Choose'),('Knockout', 'Knockout'), ('Knockin', 'Knockin'), ('Mutation', 'Mutation'), ('Transgene', 'Transgene')],
                            validators=[NoneOf(['Choose'])])
    mutation = StringField('Mutation', validators=[DataRequired()])
    transgene = StringField('Transgene', validators=[DataRequired()])
    resistance = StringField('Resistance', validators=[DataRequired()])
    inducible = SelectField('Dox inducible', choices=[('yes', 'yes'), ('no', 'no')],validators=[DataRequired()])

class CultureInfo(FlaskForm):
    bsl = SelectField('Biosafety level', choices=[(1, '1'), (2, '2'),(3, '3')],validators=[DataRequired()], default='1', coerce=int)
    mycoplasma = SelectField('Mycoplasma status', choices=[('negative', 'negative'), ('positive', 'positive')],validators=[DataRequired()])
    pcrdate = DateField("Mycoplama PCR date", format='%Y-%m-%d')
    culturetype = SelectField('Culture type', choices=[('adherent', 'adherent'), ('suspension', 'suspension')],validators=[DataRequired()], default='adherent')
    medium = StringField('Culture medium', validators=[DataRequired()])
    notes = TextAreaField('Notes')

class Stocks(FlaskForm):
    freezer = StringField('Freezer')
    rack = StringField('Rack')
    box = StringField('Box')
    position = StringField('Position')
    medium = StringField('Medium')
    passage = IntegerField('Passage')
    date = DateField('Date', format='%Y-%m-%d')

class AdditionalInfo(FlaskForm):
    protocol = TextAreaField('Protocol')
    wb = FileField('Western Blot')
    pcr = FileField('PCR gel')
    sequencing_info = FileField('Sequencing data')
    facs = FileField('FACS data')
    description = TextAreaField('Description')
    comments = TextAreaField('Comments')
    publication = StringField('Published in', validators=[DataRequired()])

class CreateNewCellLine(FlaskForm):
    basic_information = FormField(BasicInfo)
    genetic_information = FormField(GeneticInfo)
    culture_information = FormField(CultureInfo)
    stocks = FormField(Stocks)
    additional_information = FormField(AdditionalInfo)
    submit = SubmitField('Create')
