from flask import render_template, flash, jsonify, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from werkzeug import secure_filename
from app import app, db, lm, models
# from .forms import LoginForm, CharacterForm, AdjustmentForm
# from .models import Character, User
from operator import itemgetter
import __builtin__, collections, json, re, os, xmltodict

@lm.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.before_request
def before_request():
    g.user = current_user
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.get_id() is not None:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)
        flask.flash('Logged in successfully.')
        return redirect(next or flask.url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"