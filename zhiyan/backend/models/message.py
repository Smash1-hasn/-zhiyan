from app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer,primary_key=True)
    conversation_id = db.Column(db.Integer,db.ForeignKey('conversation.id'),nullable=False)
    role = db.Column(db.String(20),nullable=False)
    content = db.Column(db.Text,nullable=False)
    metadata_json = db.Column(db.Text,nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.now)
    