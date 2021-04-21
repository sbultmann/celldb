from flask import render_template,request
from app import app, db
from app.forms import LoginForm, CreateNewCellLine
from flask import render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from app.models import User, CellLines
from flask_login import current_user, login_user, logout_user, login_required
import pandas as pd

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

""" needs work """
@app.route('/create')
@login_required
def create():
    form = CreateNewCellLine()
    return render_template('create.html', title='New entry', form=form)

@app.route('/cell_lines', methods=['GET', 'POST'])
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

@app.route('/details/<int:cell_id>')
def details(cell_id):   
    cl = CellLines.query.get(cell_id)
    genotype = cl.genetic_info.all()[0]
    culture = cl.culture_info.all()[0]
    addinfo = cl.additional_info.all()[0]
    stocks = cl.stocks.all()
    return render_template('details.html', title='Details', cell_line = cl, genotype = genotype,
                            culture = culture, addinfo = addinfo, stocks = stocks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))