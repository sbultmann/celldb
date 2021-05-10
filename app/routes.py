from flask import render_template,request
from app import app, db
from app.forms import LoginForm, CreateNewCellLine, RegisterForm
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


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
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
    return render_template('index.html', title='Home', posts=posts)


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
            running_number = form.basic_information.data["running_number"]
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
        wb_file = form.additional_information.data["wb"]
        pcr_file = form.additional_information.data["pcr"]
        seq_file = form.additional_information.data["sequencing_info"]
        facs_file = form.additional_information.data["facs"]
        wb_name = random_filename(wb_file.filename)
        pcr_name = random_filename(pcr_file.filename)
        seq_name = random_filename(seq_file.filename)
        facs_name = random_filename(facs_file.filename)
        wb_file.save(os.path.join(app.config['UPLOAD_FOLDER'],wb_name))
        pcr_file.save(os.path.join(app.config['UPLOAD_FOLDER'],pcr_name))
        seq_file.save(os.path.join(app.config['UPLOAD_FOLDER'],seq_name))
        facs_file.save(os.path.join(app.config['UPLOAD_FOLDER'],facs_name))
        wb_s = resize_image(wb_file, wb_name, 800)
        pcr_s = resize_image(pcr_file, pcr_name, 800)
        seq_s = resize_image(seq_file, seq_name, 800)
        facs_s = resize_image(facs_file, facs_name, 800)
        NewAdditionalInfo = CellLineGeneration(
            cell_line_id = NewCellLine.id,
            protocol = form.additional_information.data["protocol"],
            wb = wb_name,
            wb_s = wb_s,
            pcr = pcr_name,
            pcr_s = pcr_s,
            sequencing_info = seq_name,
            sequencing_info_s = seq_s,
            facs = facs_name,
            facs_s = facs_s,
            description = form.additional_information.data["description"],
            comments = form.additional_information.data["comments"],
            publication = form.additional_information.data["publication"]
        )
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
        flash("Only administrators can delete entrys!")
        return redirect(url_for("index"))

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
    return render_template('full_size_image.html', f = filename)

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
        NewUser = User(username = form.username.data, email = form.email.data)
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
