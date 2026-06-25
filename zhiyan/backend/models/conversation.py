from app import db
from datetime import datetime

class Conversation(db.Model):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    title = db.Column(db.String(100),default='新会话')
    template_id = db.Column(db.Integer,db.ForeignKey('prompt_template.id'),nullable=True)
    status = db.Column(db.String(20),default='active')
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    
    messages = db.relationship('Message',backref='conversation',cascade='all,delete-orphan') 