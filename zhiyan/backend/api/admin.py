from flask import Blueprint,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from models import db,Conversation,ToolCallLog,Message
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin',__name__)
@admin_bp.route('/stats',methods=['GET'])
@jwt_required()
def stats():
    user_id = int(get_jwt_identity())
    today = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
    
    try:
        #今日咨询量
        today_convs = Conversation.query.filter(
            Conversation.user_id == user_id,
            Conversation.created_at >= today
        ).count()
        
        #总会话数
        total_convs = Conversation.query.filter_by(
            user_id = user_id,status ='active' 
        ).count()
        
        #Token 和成本统计
        token_stats = db.session.query(
            db.func.sum(ToolCallLog.token_count).label('total_tokens'),
            db.func.sum(ToolCallLog.cost).label('total_cost')
        ).join(
            Conversation,ToolCallLog.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id
        ).first()
        
        total_tokens = token_stats.total_tokens or 0
        total_cost = round(token_stats.total_cost or 0, 6)

        
        #工具调用统计(只查当前用户的)
        tool_stats = db.session.query(
            ToolCallLog.tool_name,
            db.func.count(ToolCallLog.id).label('total'),
            db.func.avg(ToolCallLog.duration_ms).label('avg_duration'),
            db.func.sum(db.cast(ToolCallLog.success,db.Integer)).label('success_count')
            ).join(
                Conversation,ToolCallLog.conversation_id == Conversation.id
            ).filter(
                Conversation.user_id == user_id
            ).group_by(ToolCallLog.tool_name).all()
        
        tool_data = [{
            'tool':t.tool_name,
            'total':t.total,
            'success_rate':round(t.success_count / t.total * 100,1) if t.total>0 else 0,
            'avg_duration':round(t.avg_duration,0) if t.avg_duration else 0
        } for t in tool_stats]
        
        return jsonify({
            'today_conversations': today_convs,
            'total_conversations':total_convs,
            'total_tokens':total_tokens,
            'total_cost':total_cost,
            'tools':tool_data
        }),200
    except Exception as e:
        logger.error(f'获取统计数据异常:{e}')
        return jsonify({'error':'服务器错误'}),500
    
        