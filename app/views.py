from flask import render_template, flash, jsonify, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from werkzeug import secure_filename
from app import app, db, lm, models
from .forms import LoginForm
from .models import User
from operator import itemgetter
import __builtin__, collections, json, re, os, xmltodict

class_directory = '/home/kitka/src/dwcharbuilder/app/static/data/classes'

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.before_request
def before_request():
    g.user = current_user
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.get_id() is not None:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            flash ('Username or password is invalid' , 'error')
            return redirect(url_for('login'))
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)
        flash('Logged in successfully.')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/')
@app.route('/index')
@login_required
def index():
    return "Hello, World!"
    
@app.template_filter()
def makelist(list, *args):
    if not list:
        return []
    elif type(list) != type([]):
        return [list]
    else:
        return list
    
@app.route('/<userid>/new')
@login_required
def new(userid):
    user = g.user
    classes = {}
    for filename in os.listdir(class_directory):
        with open(os.path.join(class_directory, filename), 'r') as fd:
            rawdata = xmltodict.parse(fd.read())
            classname = rawdata['class']['@name']
            classes[classname] = filename
    classes = collections.OrderedDict(sorted(classes.items()))
        
    return render_template('new.html', user=user, classes=classes)
    
@app.route('/class/new', methods=['GET', 'POST'])
@login_required
def class_new():
    user = g.user
    file = os.path.join(class_directory, request.form.get('charclass'))
    with open(file, 'r') as fd:
        rawdata = xmltodict.parse(fd.read())
        charclass = rawdata['class']
        
    return render_template('new_character.html', user=user, charclass=charclass)