from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Create user table"""    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Board(db.Model):
    """Create user board"""    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    title = db.Column(db.String(128))
    context = db.Column(db.String(2048))

    def __init__(self, username, title, context):
        self.username = username
        self.title = title
        self.context = context
        
  