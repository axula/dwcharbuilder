from app import db
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    #characters = db.relationship('Character', backref='player', lazy='dynamic')

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

'''class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    class_name = db.Column(db.String(128))
    level = db.Column(db.Integer)
    xp = db.Column(db.Integer)
    look = db.Column(db.String(128)) # [ 'Choice', 'Choice', 'Choice' ... ]
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
    moves = db.Column(db.Text) # ['Move1', 'Move2', ... ]
    race_choice = db.Column(db.String(128))
    move_choices = db.Column(db.Text) # { 'Move' : 'Choice', 'Move' : '[Choices]', ... }
    # Equipment
    weapons = db.Column(db.Text) # ['Item (tags)', 'Item (tags)', ... ]
    armor = db.Column(db.Text) # ['Item (tags)', 'Item (tags)', ... ]
    gear = db.Column(db.Text) # ['Item (tags)', 'Item (tags)', ... ]
    magic_items = db.Column(db.Text)
    # Spells
    spellbook = db.Column(db.Text) # ['Spell', 'Spell', ... ]
    spells_prepared = db.Column(db.Text) # ['Spell', 'Spell', ... ]
    
    def get_move_choices(self, move):
        if move in json.loads(self.moves):
            move_choices = json.loads(self.move_choices)
            return move_choices[move]
            
    def max_hp(self):
        return self.hp_bonus + self.constitution
            
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
        return text.replace('[BLANK]', name)'''