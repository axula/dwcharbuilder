from flask import render_template, flash, jsonify, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from werkzeug import secure_filename
from app import app, db, lm, models
from .forms import LoginForm
from .models import Character, Gear, User
from operator import itemgetter
import __builtin__, collections, json, re, os, xmltodict

class_directory = '/home/kitka/src/dwcharbuilder/app/static/data/classes'
item_directory = '/home/kitka/src/dwcharbuilder/app/static/data/equipment'

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
    
@app.template_filter()
def option_list(list):
    temp = []
    for item in makelist(list):
        temp.append(item['#text'])
    return ', '.join(temp)
    
@app.route('/<userid>')
@login_required
def user(userid):
    user = g.user

    if user == None:
        flash('User %s not found.' % userid)
        return redirect(url_for('index'))

    return render_template('user.html', title='Characters', user=user)
    
@app.route('/<userid>/new')
@login_required
def new(userid):
    user = g.user
    classes = {}
    for filename in os.listdir(class_directory):
        with open(os.path.join(class_directory, filename), 'r') as fd:
            rawdata = xmltodict.parse(fd.read())
            classname = rawdata['class']['@name']
            classes[filename] = classname
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

@app.route('/character/new', methods=['GET', 'POST'])
@login_required
def new_character():
    user = g.user
    with open(os.path.join(class_directory, request.form['class']), 'r') as fd:
        rawdata = xmltodict.parse(fd.read())
        charclass = rawdata['class']
    look = {}
    bonds = {}
    for key, value in request.form.iteritems():
        if 'look-' in key and 'custom' not in key:
            if value:
                look[key] = value
            else:
                look[key] = request.form[look[key] + '-custom']
        elif 'bond' in key:
            bonds[key] = value
    moves = {}
    for move in [ m for m in charclass['moves']['move'] if m['@minLevel'] == "1" ]:
        if 'options' in move:
            for options in makelist(move['options']):
                moves[move['@name']] = dict([(options['@name'], request.form[options['@name']])])
        else:
            moves[move['@name']] = ""
    character = Character(name=request.form['name'], 
                    class_name=charclass['@name'], 
                    level=1, xp=0, look=json.dumps(look), 
                    strength=request.form['strength'], 
                    dexterity=request.form['dexterity'], 
                    constitution=request.form['constitution'], 
                    intelligence=request.form['intelligence'], 
                    wisdom=request.form['wisdom'], 
                    charisma=request.form['charisma'], 
                    hp_bonus=int(charclass['stats']['hp']), 
                    alignment=request.form['alignment'], 
                    race=request.form['race'], 
                    bonds=json.dumps(bonds), moves=json.dumps(moves), race_choice="", 
                    weapons="", armor="", gear="", magic_items="", 
                    spellbook="", spells_prepared="")
    db.session.add(character)
    db.session.commit()
    return redirect(url_for('character', userid=user.username, characterid=character.id))
    
@app.template_filter()
def tags(list):
    temp = []
    for i in list:
        if '#text' in i:
            temp.append(i['#text'])
        else:
            temp.append(i)
    return ', '.join(temp)
    
@app.route('/<userid>/<characterid>/character')
@login_required
def character(userid, characterid):
    user = g.user
    character = Character.query.filter_by(id=characterid, userid=user.id).first()
    file = os.path.join(class_directory, character.class_file)
    with open(file, 'r') as fd:
        rawdata = xmltodict.parse(fd.read())
        charclass = rawdata['class']
    data = {}
    data['damage'] = charclass['stats']['damage']
    data['moves'] = []
    moves = charclass['moves']['move']
    for name, choices in json.loads(character.moves).iteritems():
        move = ( m for m in moves if m['@name'] == name ).next()
        if move['@minLevel'] == '1':
            type = "Starting Move"
        else:
            type = "Advanced Move"
        choice_text = []
        if choices:
            for k, v in choices.iteritems():
                choice_text.append(k.title() + ': ' + ', '.join(makelist(v)))
        data['moves'].append( { 'title' : name, 'type' : type, 
                                'url' : name.replace(' ', '-').lower(), 
                                'choices' : '; '.join(choice_text), 
                                'text' : move['description'] } )
    data['moves'] = sorted(data['moves'], key=itemgetter('title'))
    data['look'] = json.loads(character.look)
    data['alignment_text'] = ( a['#text'] for a in charclass['alignment']['choice'] if a['@name'] == character.alignment ).next()
    data['bonds'] = []
    for key, player in json.loads(character.bonds).iteritems():
        if player:
            index = int(key.replace('bond', '')) - 1
            text = charclass['bonds']['bond'][index]
            data['bonds'].append( character.bond_text(player, text) )
    data['race_text'] = ( r['description'] for r in charclass['race']['choice'] if r['@name'] == character.race ).next()
    data['max_load'] = int(charclass['gear']['@load']) + character.modifier(character.strength)
    
    # Inventory Items
    data['weapons'] = character.gear.filter_by(type="weapon")
    data['armors'] = character.gear.filter_by(type="armor")
    data['gear'] = character.gear.filter_by(type="gear")
    data['poisons'] = character.gear.filter_by(type="poison")
    
    # Items list
    data['weapon_choices'] = []
    data['armor_choices'] = []
    data['gear_choices'] = []
    data['poison_choices'] = []
    for filename in os.listdir(item_directory):
        with open(os.path.join(item_directory, filename), 'r') as fd:
            rawdata = xmltodict.parse(fd.read())
            for w in rawdata['items']['weapons']['weapon']:
                taglist = '(' + tags(w['tag']) + ')'
                data['weapon_choices'].append( { 'name' : w['@name'], 'tags' : taglist, 'source' : filename, 'price' : w['@price'] } )
            for a in rawdata['items']['armors']['armor']:
                taglist = '(' + tags(a['tag']) + ')'
                data['armor_choices'].append( { 'name' : a['@name'], 'tags' : taglist, 'source' : filename, 'price' : a['@price'] } )
            for i in rawdata['items']['gears']['gear']:
                taglist = '(' + tags(i['tag']) + ')'
                data['gear_choices'].append( { 'name' : i['@name'], 'tags' : taglist, 'source' : filename, 'price' : i['@price'], 'description' : i['description'] } )
            for p in rawdata['items']['poisons']['poison']:
                taglist = '(' + tags(p['tag']) + ')'
                data['poison_choices'].append( { 'name' : p['@name'], 'tags' : taglist, 'source' : filename, 'price' : p['@price'], 'description' : p['description'] } )
    
    return render_template('character.html', user=user, character=character, data=data)
    
@app.route('/equipment/add', methods=['POST'])
@login_required
def add_equipment():
    user = g.user
    if request.json['source']:
        file = os.path.join(item_directory, request.json['source'])
        with open(file, 'r') as fd:
            rawdata = xmltodict.parse(fd.read())
            items = rawdata['items'][request.json['type'] + 's'][request.json['type']]
            item = ( i for i in items if i['@name'] == request.json['name'] )
        tags = ''
        if '@uses' in item:
            max_uses = int( item['@uses'] )
        else:
            max_uses = None
    gear = Gear( name=request.json['name'], characterid=request.json['id'], 
                 type=request.json['type'], source=request.json['source'], 
                 tags=tags, remaining_uses=max_uses )
    character = Character.query.filter_by(id=request.json['id']).first()
    if request.json['is_buying']:
        character.money -= item['@price']
    db.session.add(gear)
    db.session.add(character)
    db.session.commit()
    return jsonify( { 'name' : gear.name, 'type' : gear.type, 'id' : gear.id, 
                      'source' : gear.source, 'tags' : gear.get_tags(), 
                      'description' : gear.get_description(), 
                      'load' : character.current_load() } )
    
@app.route('/equipment/remove', methods=['POST'])
@login_required
def remove_equipment():
    user = g.user
    item = Gear.query.filter_by(id=request.json['id']).first()
    character = Character.query.filter_by(id=item.characterid).first()
    db.session.delete(item)
    db.session.commit()
    return jsonify( { 'message' : 'Yay!', 'load' : character.current_load(), 
                      'armor' : character.armor_bonus() } )
    
@app.route('/equipment/expend', methods=['POST'])
@login_required
def expend_equipment():
    user = g.user
    item = Gear.query.filter_by(id=request.json['id']).first()
    item = item.expend()
    return jsonify( { 'message' : 'Yay!' } )
    
@app.route('/money', methods=['POST'])
@login_required
def money():
    user = g.user
    character = Character.query.filter_by(id=request.json['id']).first()
    character.money += request.json['money']
    db.session.add(character)
    db.session.commit()
    return jsonify( { 'message' : 'Yay!', 'money' : character.money } )