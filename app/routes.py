from flask import render_template,request
from app import app, db, whooshee
from app.forms import LoginForm, CreateNewCellLine, RegisterForm, SearchForm, BasicInfo, GeneticInfo, CultureInfo, AdditionalInfo, StocksForm
from flask import render_template, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from app.models import User, CellLines, Stocks, Genotype, CellCulture, CellLineGeneration
from flask_login import current_user, login_user, logout_user, login_required
import pandas as pd
from io import BytesIO
import base64
# from app.captcha import Captcha
import os
from app.filename import random_filename
from app.resize import resize_image
import re
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, FormField, IntegerField
from wtforms.validators import DataRequired, NoneOf, AnyOf, ValidationError, EqualTo, Email, Length

@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    form = SearchForm()
    return render_template('index.html', title='Home', posts=posts, form = form)


@app.route('/search', methods=['GET','POST'])
@login_required
def search():
    kw = request.form.get('kw','').strip()
    type = request.form.get('kw_type','All').strip()
    page = request.args.get('page', 1, type=int)
    per_page = app.config['CELLLINES_PER_PAGE']
    if type == 'All':
        cell_lines = CellLines.query.whooshee_search(kw).paginate(page,per_page)
    elif type == 'Name':
        cell_lines = CellLines.query.filter(CellLines.name.like('%'+kw+'%')).paginate(page,per_page)
    elif type == 'ID':
        cell_lines = CellLines.query.filter(CellLines.running_number.like('%'+kw+'%')).paginate(page,per_page)
    elif type == 'Cell type':
        cell_lines = CellLines.query.filter(CellLines.celltype.like('%'+kw+'%')).paginate(page,per_page)
    elif type == 'Tissue':
        cell_lines = CellLines.query.filter(CellLines.tissue.like('%'+kw+'%')).paginate(page,per_page)
    else:
        cell_lines = CellLines.query.filter(CellLines.species.like('%'+kw+'%')).paginatee(page,per_page)
    next_url = url_for('cell_lines', page=cell_lines.next_num) \
        if cell_lines.has_next else None
    prev_url = url_for('cell_lines', page=cell_lines.prev_num) \
        if cell_lines.has_prev else None
    return render_template('cell_lines.html', title='Cell Lines', cell_lines=cell_lines.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/create',methods=['GET','POST'])
@login_required
def create():
    form = CreateNewCellLine()
    if form.validate_on_submit():
        NewCellLine = CellLines(
            name=form.basic_information.data["name"],
            celltype=form.basic_information.data["celltype"],
            species=form.basic_information.data["species"],
            tissue=form.basic_information.data["tissue"],
            running_number = form.basic_information.data["running_number"],
            user_id = current_user.id
        )
        db.session.add(NewCellLine)
        db.session.commit()
        NewStocks = Stocks(
            cell_line_id = NewCellLine.id,
            date = form.stocks.data["date"],
            freezer = form.stocks.data["freezer"],
            rack = form.stocks.data["rack"],
            box = form.stocks.data["box"],
            position = form.stocks.data["position"],
            medium = form.stocks.data["medium"],
            passage = form.stocks.data["passage"]
        )
        NewGenotype = Genotype(
            cell_line_id = NewCellLine.id,
            modmethod = form.genetic_information.data["modmethod"],
            locus = form.genetic_information.data["locus"],
            tag = form.genetic_information.data["tag"],
            modtype = form.genetic_information.data["modtype"],
            mutation = form.genetic_information.data["mutation"],
            transgene = form.genetic_information.data["transgene"],
            resistance = form.genetic_information.data["resistance"],
            inducible = form.genetic_information.data["inducible"]
        )
        NewCulture = CellCulture(
            cell_line_id = NewCellLine.id,
            bsl = form.culture_information.data["bsl"],
            mycoplasma = form.culture_information.data["mycoplasma"],
            pcrdate = form.culture_information.data["pcrdate"],
            culturetype = form.culture_information.data["culturetype"],
            medium = form.culture_information.data["medium"],
            notes = form.culture_information.data["notes"]
        )
        NewAdditionalInfo = CellLineGeneration(
            cell_line_id = NewCellLine.id,
            protocol = form.additional_information.data["protocol"],
            description = form.additional_information.data["description"],
            comments = form.additional_information.data["comments"],
            publication = form.additional_information.data["publication"]
        )
        if form.additional_information.data["wb"] is not None:
            wb_file = form.additional_information.data["wb"]
            wb_name = random_filename(wb_file.filename)
            wb_file.save(os.path.join(app.config['UPLOAD_FOLDER'],wb_name))
            wb_s = resize_image(wb_file, wb_name, 800)
            NewAdditionalInfo.wb = wb_name
            NewAdditionalInfo.wb_s = wb_s
        if form.additional_information.data["pcr"] is not None:
            pcr_file = form.additional_information.data["pcr"]
            pcr_name = random_filename(pcr_file.filename)
            pcr_file.save(os.path.join(app.config['UPLOAD_FOLDER'],pcr_name))
            pcr_s = resize_image(pcr_file, pcr_name, 800)
            NewAdditionalInfo.pcr = pcr_name
            NewAdditionalInfo.pcr_s = pcr_s
        if form.additional_information.data["sequencing_info"] is not None:
            sequencing_info_file = form.additional_information.data["sequencing_info"]
            sequencing_info_name = random_filename(sequencing_info_file.filename)
            sequencing_info_file.save(os.path.join(app.config['UPLOAD_FOLDER'],sequencing_info_name))
            sequencing_info_s = resize_image(sequencing_info_file, sequencing_info_name, 800)
            NewAdditionalInfo.sequencing_info = sequencing_info_name
            NewAdditionalInfo.sequencing_info_s = sequencing_info_s
        if form.additional_information.data["facs"] is not None:
            facs_file = form.additional_information.data["facs"]
            facs_name = random_filename(facs_file.filename)
            facs_file.save(os.path.join(app.config['UPLOAD_FOLDER'],facs_name))
            facs_s = resize_image(facs_file, facs_name, 800)
            NewAdditionalInfo.facs = facs_name
            NewAdditionalInfo.facs_s = facs_s
        db.session.add(NewGenotype)
        db.session.add(NewCulture)
        db.session.add(NewGenotype)
        db.session.add(NewAdditionalInfo)
        db.session.add(NewStocks)
        db.session.commit()
        flash("New entry created!")
        return redirect(url_for('index'))
    print(form.errors)
    return render_template('create.html', title='New entry', form=form)

@app.route('/delete/<int:cell_id>')
@login_required
def delete(cell_id):
    if current_user.is_admin:
        cl = CellLines.query.get(cell_id)
        add = cl.additional_info.all()
        if add:
            for i in add:
                if i.wb is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.wb))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.wb_s))
                if i.pcr is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.pcr))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.pcr_s))
                if i.sequencing_info is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.sequencing_info))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.sequencing_info_s))
                if i.facs is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.facs))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.facs_s))
            db.session.delete(i)
        db.session.delete(cl)
        db.session.commit()
        flash("Item was deleted successfully")
        return redirect(url_for("cell_lines"))
    else:
        flash("Only administrators can delete entries!")
        return redirect(url_for("cell_lines"))

@app.route('/edit/<int:cell_id>',methods=['GET','POST'])
@login_required
def edit(cell_id):
    cl = CellLines.query.get(cell_id)
    if current_user.is_admin or cl.user_id == current_user.id:
        genotype = cl.genetic_info.all()[0]
        culture = cl.culture_info.all()[0]
        addinfo = cl.additional_info.all()[0]
        stocks = cl.stocks.all()[0]
        BasicInfo.name = StringField('Name', validators=[DataRequired()], default = cl.name)
        BasicInfo.celltype = StringField('Cell type', validators=[DataRequired()], default = cl.celltype)
        BasicInfo.species = SelectField('Species', validators=[NoneOf(values=["Choose"])],
                                         choices=[('Choose', 'Choose'),('Mouse', 'Mouse'), ('Human', 'Human'), ('Hamster', 'Hamster'), ('Drosophila', 'Drosophila')], default = cl.species)
        BasicInfo.tissue = StringField('Tissue', validators=[DataRequired()], default = cl.tissue)
        BasicInfo.running_number = StringField("Running number", validators=[DataRequired()], default = cl.running_number)
        GeneticInfo.modmethod = StringField('Modification method', validators=[DataRequired()], default = genotype.modmethod)
        GeneticInfo.locus = StringField('Locus/Gene', validators=[DataRequired()], default = genotype.locus)
        GeneticInfo.tag = StringField('Epitope tag', validators=[DataRequired()], default = genotype.tag)
        GeneticInfo.modtype = SelectField('Modification type', choices=[('Choose', 'Choose'),('Knockout', 'Knockout'), ('Knockin', 'Knockin'), ('Mutation', 'Mutation'), ('Transgene', 'Transgene')],
                                validators=[NoneOf(['Choose'])], default = genotype.modtype)
        GeneticInfo.mutation = StringField('Mutation', validators=[DataRequired()], default = genotype.mutation)
        GeneticInfo.transgene = StringField('Transgene', validators=[DataRequired()], default = genotype.transgene)
        GeneticInfo.resistance = StringField('Resistance', validators=[DataRequired()], default = genotype.resistance)
        GeneticInfo.inducible = SelectField('Dox inducible', choices=[('yes', 'yes'), ('no', 'no')],validators=[DataRequired()], default = genotype.inducible)
        CultureInfo.bsl = SelectField('Biosafety level', choices=[(1, '1'), (2, '2'),(3, '3')],validators=[DataRequired()], default = culture.bsl, coerce=int)
        CultureInfo.mycoplasma = SelectField('Mycoplasma status', choices=[('negative', 'negative'), ('positive', 'positive')],validators=[DataRequired()], default = culture.mycoplasma)
        CultureInfo.pcrdate = DateField("Mycoplama PCR date", format='%Y-%m-%d', default = culture.pcrdate)
        CultureInfo.culturetype = SelectField('Culture type', choices=[('adherent', 'adherent'), ('suspension', 'suspension')],validators=[DataRequired()], default = culture.culturetype)
        CultureInfo.medium = StringField('Culture medium', validators=[DataRequired()], default = culture.medium)
        CultureInfo.notes = TextAreaField('Notes', default = culture.notes)
        StocksForm.freezer = StringField('Freezer', default = stocks.freezer)
        StocksForm.rack = StringField('Rack', default = stocks.rack)
        StocksForm.box = StringField('Box', default = stocks.box)
        StocksForm.position = StringField('Position', default = stocks.position)
        StocksForm.medium = StringField('Medium', default = stocks.medium)
        StocksForm.passage = IntegerField('Passage', default = stocks.passage)
        StocksForm.date = DateField('Date', format='%Y-%m-%d', default = stocks.date)
        AdditionalInfo.protocol = TextAreaField('Protocol', default = addinfo.protocol)
        AdditionalInfo.description = TextAreaField('Description', default = addinfo.description)
        AdditionalInfo.comments = TextAreaField('Comments', default = addinfo.comments)
        AdditionalInfo.publication = StringField('Published in', validators=[DataRequired()], default = addinfo.publication)
        CreateNewCellLine.basic_information = FormField(BasicInfo)
        CreateNewCellLine.genetic_information = FormField(GeneticInfo)
        CreateNewCellLine.culture_information = FormField(CultureInfo)
        CreateNewCellLine.stocks = FormField(StocksForm)
        CreateNewCellLine.additional_information = FormField(AdditionalInfo)
        form = CreateNewCellLine()
        if form.validate_on_submit():
            cl.name = form.basic_information.data["name"]
            cl.celltype = form.basic_information.data["celltype"]
            cl.species = form.basic_information.data["species"]
            cl.tissue = form.basic_information.data["tissue"]
            cl.running_number =  form.basic_information.data["running_number"]
            stocks.date = form.stocks.data["date"]
            stocks.freezer = form.stocks.data["freezer"]
            stocks.rack = form.stocks.data["rack"]
            stocks.box = form.stocks.data["box"]
            stocks.position = form.stocks.data["position"]
            stocks.medium = form.stocks.data["medium"]
            stocks.passage = form.stocks.data["passage"]
            genotype.modmethod = form.genetic_information.data["modmethod"]
            genotype.locus = form.genetic_information.data["locus"]
            genotype.tag = form.genetic_information.data["tag"]
            genotype.modtype = form.genetic_information.data["modtype"]
            genotype.mutation = form.genetic_information.data["mutation"]
            genotype.transgene = form.genetic_information.data["transgene"]
            genotype.resistance = form.genetic_information.data["resistance"]
            genotype.inducible = form.genetic_information.data["inducible"]
            culture.bsl = form.culture_information.data["bsl"]
            culture.mycoplasma = form.culture_information.data["mycoplasma"]
            culture.pcrdate = form.culture_information.data["pcrdate"]
            culture.culturetype = form.culture_information.data["culturetype"]
            culture.medium = form.culture_information.data["medium"]
            culture.notes = form.culture_information.data["notes"]
            addinfo.protocol = form.additional_information.data["protocol"]
            addinfo.description = form.additional_information.data["description"]
            addinfo.comments = form.additional_information.data["comments"]
            addinfo.publication = form.additional_information.data["publication"]
            if form.additional_information.data["wb"] is not None:
                if addinfo.wb is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.wb))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.wb_s))
                wb_file = form.additional_information.data["wb"]
                wb_name = random_filename(wb_file.filename)
                wb_file.save(os.path.join(app.config['UPLOAD_FOLDER'],wb_name))
                wb_s = resize_image(wb_file, wb_name, 800)
                addinfo.wb = wb_name
                addinfo.wb_s = wb_s
            if form.additional_information.data["pcr"] is not None:
                if addinfo.pcr is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.pcr))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.pcr_s))
                pcr_file = form.additional_information.data["pcr"]
                pcr_name = random_filename(pcr_file.filename)
                pcr_file.save(os.path.join(app.config['UPLOAD_FOLDER'],pcr_name))
                pcr_s = resize_image(pcr_file, pcr_name, 800)
                addinfo.pcr = pcr_name
                addinfo.pcr_s = pcr_s
            if form.additional_information.data["sequencing_info"] is not None:
                if addinfo.sequencing_info is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.sequencing_info))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.sequencing_info_s))
                sequencing_info_file = form.additional_information.data["sequencing_info"]
                sequencing_info_name = random_filename(sequencing_info_file.filename)
                sequencing_info_file.save(os.path.join(app.config['UPLOAD_FOLDER'],sequencing_info_name))
                sequencing_info_s = resize_image(sequencing_info_file, sequencing_info_name, 800)
                addinfo.sequencing_info = sequencing_info_name
                addinfo.sequencing_info_s = sequencing_info_s
            if form.additional_information.data["facs"] is not None:
                if addinfo.facs is not None:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.facs))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], addinfo.facs_s))
                facs_file = form.additional_information.data["facs"]
                facs_name = random_filename(facs_file.filename)
                facs_file.save(os.path.join(app.config['UPLOAD_FOLDER'],facs_name))
                facs_s = resize_image(facs_file, facs_name, 800)
                addinfo.facs = facs_name
                addinfo.facs_s = facs_s
            db.session.commit()
            flash("Item was edited successfully")
            return redirect(url_for('cell_lines'))
        return render_template('create.html',form=form, title = 'Edit')
    else:
        flash('You do not have the permission to edit this entry!')
        return redirect(url_for('cell_lines'))

@app.route('/cell_lines', methods=['GET', 'POST'])
@login_required
def cell_lines():
    page = request.args.get('page', 1, type=int)
    cell_lines = db.session.query(CellLines).paginate(
        page, app.config['CELLLINES_PER_PAGE'], False)
    next_url = url_for('cell_lines', page=cell_lines.next_num) \
        if cell_lines.has_next else None
    prev_url = url_for('cell_lines', page=cell_lines.prev_num) \
        if cell_lines.has_prev else None
    return render_template('cell_lines.html', title='Cell Lines', cell_lines=cell_lines.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/image/<path:filename>')
@login_required
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/full_size_image/<path:filename>')
@login_required
def full_size_image(filename):
    filename, ext = os.path.splitext(filename)
    filename = filename[:-2]
    filename += ext
    return render_template('full_size_image.html', f = filename, title = "Full-size image")

@app.route('/details/<int:cell_id>')
@login_required
def details(cell_id):
    cl = CellLines.query.get(cell_id)
    genotype = cl.genetic_info.all()[0]
    culture = cl.culture_info.all()[0]
    addinfo = cl.additional_info.all()[0]
    stocks = cl.stocks.all()[0]
    return render_template('details.html', title='Details', cell_line = cl, genotype = genotype,
                                    culture = culture, addinfo = addinfo, stocks = stocks, wb = addinfo.wb_s, pcr = addinfo.pcr_s, seq = addinfo.sequencing_info_s, facs = addinfo.facs_s)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    #c = Captcha()
    #image, code = c.CaptchaGenerator()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        NewUser = User(username = form.username.data, email = form.email.data, role = 'USER')
        NewUser.set_password(form.password.data)
        db.session.add(NewUser)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
