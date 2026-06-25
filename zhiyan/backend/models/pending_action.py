from app import db
from datetime import datetime
import json


class PendingAction(db.Model):
    __tablename__ = 'pending_action'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    action_data = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'action_type': self.action_type,
            'action_data': json.loads(self.action_data) if self.action_data else {},
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
