from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),unique=True,nullable=False)
    password_hash = db.Column(db.String(256),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    
    #关系
    conversations = db.relationship('Conversation',backref='user',lazy='dynamic')

    