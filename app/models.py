from app import db
import collections, json, re, os, xmltodict

class_directory = '/home/kitka/src/dwcharbuilder/app/static/data/classes'
item_directory = '/home/kitka/src/dwcharbuilder/app/static/data/equipment'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    characters = db.relationship('Character', backref='player', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3

    def __repr__(self):
        return '<User %r>' % (self.username)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_name = db.Column(db.String(128))
    class_file = db.Column(db.String(256))
    level = db.Column(db.Integer)
    xp = db.Column(db.Integer)
    look = db.Column(db.String(128)) # { 'type' : 'Choice', 'type' : 'Choice' ... }
    # Stats
    strength = db.Column(db.Integer)
    dexterity = db.Column(db.Integer)
    constitution = db.Column(db.Integer)
    intelligence = db.Column(db.Integer)
    wisdom = db.Column(db.Integer)
    charisma = db.Column(db.Integer)
    # Stats
    hp_bonus = db.Column(db.Integer)
    alignment = db.Column(db.String(32))
    race = db.Column(db.String(32))
    bonds = db.Column(db.String(64)) # ['Name', 'Name', ... ]
    moves = db.Column(db.Text) # { 'Move' : '', 'Move' : '[Choices]', ... }
    race_choice = db.Column(db.String(128))
    # Equipment
    money = db.Column(db.Integer, default=0)
    gear = db.relationship('Gear', backref='character', lazy='dynamic')
    # Spells
    spellbook = db.Column(db.Text) # ['Spell', 'Spell', ... ]
    spells_prepared = db.Column(db.Text) # ['Spell', 'Spell', ... ]
            
    def armor_bonus(self):
        armor = 0
        for item in self.gear:
            if item.equipped and item.armor_bonus():
                armor += item.armor_bonus()
        return armor
    
    def max_hp(self):
        return self.hp_bonus + self.constitution
    
    def level_up(self):
        if self.xp >= self.level + 7:
            self.xp -= self.level + self.level
            self.level += 1
            # Add a new advanced move from class
            # Wizards get a new spell in spellbook
            # Increase one stat by 1 (max 18)
            db.session.add(self)
            db.session.commit()
        return self
    
    def current_load(self):
        load = 0
        for item in self.gear:
            if item.carried:
                load += item.get_weight()
        return load
            
    def modifier(self, score):
        if score <= 3:
            return -3
        elif score <= 5:
            return -2
        elif score <= 8:
            return -1
        elif score <= 12:
            return 0
        elif score <= 15:
            return 1
        elif score <= 17:
            return 2
        elif score == 18:
            return 3
            
    def bond_text(self, name, text):
        return text.replace('[BLANK]', '<b>' + name + '</b>')

    def __repr__(self):
        return '<Character %r>' % (self.name)
        
class Gear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    characterid = db.Column(db.Integer, db.ForeignKey('character.id'))
    type = db.Column(db.String(64)) # weapon, armor, gear, poison
    source = db.Column(db.String(128)) # if blank, it's a custom item
    
    equipped = db.Column(db.Boolean, default=False)
    carried = db.Column(db.Boolean, default=True)
    
    # Optional
    tags = db.Column(db.String(256)) # tag, tag, tag
    weight = db.Column(db.Integer)
    armor = db.Column(db.Integer)
    description = db.Column(db.String(256))
    remaining_uses = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    
    def armor_bonus(self):
        if (self.type == 'armor' or self.type == 'shield'):
            if self.armor:
                return self.armor
            else:
                with open(os.path.join(item_directory, self.source), 'r') as fd:
                    rawdata = xmltodict.parse(fd.read())
                items = rawdata['items'][self.type + 's'][self.type]
                item = [ x for x in items if x['@name'] == self.name ][0]
                return int( item['@bonus'] )
    
    def equip(self):
        if (self.type == 'armor' or self.type == 'shield') and self.equipped == False:
            old_armor = Gear.query.filter_by(equipped=True, type=self.type).first()
            old_armor.equipped = False
            self.equipped = True
            db.session.add(self)
            db.session.add(old_armor)
            db.session.commit()
    
    def unequip(self):
        self.equipped = False
        db.session.add(self)
        db.session.commit()
        return self
        
    def get_weight(self):
        if self.weight:
            return self.weight
        else: 
            with open(os.path.join(item_directory, self.source), 'r') as fd:
                rawdata = xmltodict.parse(fd.read())
            items = rawdata['items'][self.type + 's'][self.type]
            item = [ x for x in items if x['@name'] == self.name ][0]
            return int( item['@weight'] )
    
    def get_description(self):
        if self.source:
            with open(os.path.join(item_directory, self.source), 'r') as fd:
                rawdata = xmltodict.parse(fd.read())
            items = rawdata['items'][self.type + 's'][self.type]
            item = [ x for x in items if x['@name'] == self.name ][0]
            if 'description' in item:
                return item['description']
            else:
                return ""
        else:
            return self.description
    
    def list_tags(self, list):
        temp = []
        for i in list:
            if '#text' in i:
                temp.append(i['#text'])
            else:
                temp.append(i)
        return ', '.join(temp)
    
    def get_tags(self):
        if self.source:
            with open(os.path.join(item_directory, self.source), 'r') as fd:
                rawdata = xmltodict.parse(fd.read())
            items = rawdata['items'][self.type + 's'][self.type]
            item = [ x for x in items if x['@name'] == self.name ][0]
            print( item );
            tags = '(' + self.list_tags(item['tag']) + ')'
            print( tags );
            return tags
        else: 
            return '(' + self.tags + ')'
    
    def expend(self):
        if self.uses: 
            self.remaining_uses -= 1
            if self.remaining_uses == 0:
                db.session.delete(self)
                db.session.commit()
                return None
            else:
                db.session.add(self)
                db.session.commit()
                return self
        return self

    def __repr__(self):
        return '<Gear %r>' % (self.name)
        
class Spell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    characterid = db.Column(db.Integer, db.ForeignKey('character.id'))
    caster_class = db.Column(db.String(64)) # cleric, wizard
    source = db.Column(db.String(128)) # if blank, it's a custom item
    level = db.Column(db.Integer)
    
    # Optional
    tags = db.Column(db.String(128))
    description = db.Column(db.String(256))
    
    def __repr__(self):
        return '<Spell %r>' % (self.name)