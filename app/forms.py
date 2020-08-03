from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField,\
                     FileField,DateField, FormField
from wtforms.validators import DataRequired, NoneOf, AnyOf
from app import db

def pick_option(form, field):
    print(field.data)
    if field.data == "Choose":
        raise ValidationError('Please choose an option')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class BasicInfo(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    celltype = StringField('Cell type', validators=[DataRequired()])
    species = SelectField('Species', validators=[NoneOf(values=["Choose", "Mouse"])],
                            choices=['Choose','Mouse', 'Human', 'Hamster', 'Drosophila'])
    tissue = StringField('Name', validators=[DataRequired()])
    

class GeneticInfo(FlaskForm):
    modmethod = StringField('Modification method', validators=[DataRequired()])
    locus = StringField('Locus/Gene', validators=[DataRequired()])
    tag = StringField('Epitope tag', validators=[DataRequired()])
    modtype = SelectField('Modification type', choices=['Choose','Knockout', 'Knockin', 'Mutation', 'Transgene'],
                            validators=[NoneOf(['Choose'])])
    mutation = StringField('Mutation', validators=[DataRequired()])
    transgene = StringField('Transgene', validators=[DataRequired()])
    resistance = StringField('Resistance', validators=[DataRequired()])
    inducible = SelectField('Dox inducible', choices=['yes', 'no'],validators=[DataRequired()])

class CultureInfo(FlaskForm):
    bsl = SelectField('Biosafety level', choices=['1', '2','3'],validators=[DataRequired()], default='1')
    mycoplasma = SelectField('Mycoplasma status', choices=['negative', 'positive'],validators=[DataRequired()])
    pcrdate = DateField("Mycoplama PCR date")
    culturetype = SelectField('Culture type', choices=['adherent', 'suspension'],validators=[DataRequired()], default='adherent')
    medium = StringField('Culture medium', validators=[DataRequired()])
    notes = TextAreaField('Notes')

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
    additional_information = FormField(AdditionalInfo)
    submit = SubmitField('Create')