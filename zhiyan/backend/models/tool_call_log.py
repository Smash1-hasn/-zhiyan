from app import db
from datetime import datetime
import json


class ToolCallLog(db.Model):
    __tablename__ = 'tool_call_log'
    
    id = db.Column(db.Integer,primary_key=True)
    conversation_id = db.Column(db.Integer,db.ForeignKey('conversation.id'),nullable=False)
    tool_name = db.Column(db.String(50),nullable=False)
    input_args = db.Column(db.Text,nullable=True)
    result = db.Column(db.Text,nullable=True)
    duration_ms = db.Column(db.Integer,nullable=True)
    success = db.Column(db.Boolean,default=True)
    created_at = db.Column(db.DateTime,default=datetime.now)
    token_count = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=True)
    
