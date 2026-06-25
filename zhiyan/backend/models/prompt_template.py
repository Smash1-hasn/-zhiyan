from app import db
from datetime import datetime

class PromptTemplate(db.Model):
    __tablename__ = 'prompt_template'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    description = db.Column(db.String(200))
    system_prompt = db.Column(db.Text,nullable=False)
    temperature = db.Column(db.Float,default=0.7)
    is_default = db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    