from  flask import Blueprint,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from models import db,Conversation,Message
from datetime import datetime

conv_bp = Blueprint('conversation',__name__)

@conv_bp.route('',methods=["GET"])
@jwt_required()
def list_conversation():
    user_id = int(get_jwt_identity())
    convs = Conversation.query.filter_by(user_id=user_id,status='active')\
        .order_by(Conversation.updated_at.desc()).all()
    result = []
    for c in convs:
        last_msg = Message.query.filter_by(conversation_id=c.id)\
            .order_by(Message.created_at.desc()).first()
        result.append({
            'id':c.id,
            'title':c.title,
            'last_message':last_msg.content[:50] if last_msg else "",
            'updated_at' : c.updated_at.isoformat() if c.updated_at else ""  
        })
    return jsonify({'data':result}),200

@conv_bp.route('/<int:conv_id>',methods=['DELETE'])
@jwt_required()
def delete_conversation(conv_id):
    user_id = int(get_jwt_identity())
    conv = Conversation.query.get(conv_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error':'会话不存在'}),404
    conv.status = 'archived'
    db.session.commit()
    return jsonify({'message':'已删除'}),200

@conv_bp.route('/<int:conv_id>/messages',methods=['GET'])
@jwt_required()
def list_messages(conv_id):
    user_id = int(get_jwt_identity())
    try:
        conv = Conversation.query.get(conv_id)
        if not conv or conv.user_id != user_id:
            return jsonify({'error':'会话不存在'}),404
        msgs = Message.query.filter_by(conversation_id = conv_id )\
            .order_by(Message.created_at.asc()).all()
        return jsonify({'data':[{
            'role':m.role,
            'content':m.content
            } for m in msgs]}),200
    except Exception as e:
        return jsonify({'error':'服务器错误'}),500
    
        