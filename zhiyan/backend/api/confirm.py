from flask import Blueprint,jsonify,request
from flask_jwt_extended import get_jwt_identity,jwt_required
from models import db,PendingAction,Conversation,Message
from ai.tools import submit_refund
import json
import logging

logger = logging.getLogger(__name__)

confirm_bp = Blueprint('confirm',__name__)
@confirm_bp.route('',methods=['POST'])
@jwt_required()
def confirm_action():
    data = request.get_json()
    action_id = data.get('action_id')
    if not action_id:
        return jsonify({'error':'缺少action_id'}),400
    
    user_id = int(get_jwt_identity())
    # 查找确认操作
    pending = PendingAction.query.get(action_id)
    if not pending:
        return jsonify({'error':'待确认操作不存在'}),404
    # 校验归属：只能确认自己会话的操作
    conv = Conversation.query.get(pending.conversation_id)
    if not conv or conv.user_id != user_id:
        return jsonify({'error':'无权操作！'}),403
    if pending.status != 'pending':
        return jsonify({'error':'该操作已经被处理'}),400
    action = json.loads(pending.action_data)
    result = ''
    
    try:
        #执行退款
        result = submit_refund.invoke(action)
        pending.status = 'confirmed'
    except Exception as e:
        logger.error(f'退款执行失败:{e}')
        result = "退款执行失败,请联系人工客服"
        pending.status = 'failed'
    # 插入结果消息
    
    msg = Message(
        conversation_id = pending.conversation_id,
        role = 'assistant',
        content = result
    )
    
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({'message':'操作完成','result':result}),200