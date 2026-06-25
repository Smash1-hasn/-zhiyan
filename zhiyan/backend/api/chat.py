from flask import Blueprint,request,jsonify,Response,stream_with_context
from flask_jwt_extended import jwt_required,get_jwt_identity
from ai.agents import OrderAgent,AfterSalesAgent,GeneralAgent
from ai.intent import IntentClassifier
from models import db,Conversation,Message,PendingAction,ToolCallLog
import json


chat_bp = Blueprint('chat',__name__)
@chat_bp.route('',methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error':'消息不能为空'}),400
    
    user_id = int(get_jwt_identity())
    message_text = data['message'].strip()
    conversation_id = data.get('conversation_id')
    
    if not conversation_id:
        conversation = Conversation(
            user_id = user_id,
            title = message_text[:30],
            template_id = None,
            status = 'active'
        )
        db.session.add(conversation)
        db.session.commit()
        conversation_id = conversation.id
    else:
        if not isinstance(conversation_id,int):
            conversation_id = int(conversation_id)
        conversation = Conversation.query.get(conversation_id)
        
        # 安全校验
        if not conversation or conversation.user_id != user_id:
            return jsonify({'error':'会话不存在'}),404
    user_msg = Message(
        conversation_id = conversation_id,
        role = 'user',
        content = message_text
    )
    db.session.add(user_msg)
    db.session.commit()
    def generate():
        # 加载历史消息 → 构建含上下文的 messages 列表
        history = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        messages = [{'role':'system','content':'你是一个智能客服助手,请用中文回答'}]
        #滑动窗口，只保留最近10轮对话（20条信息）
        for msg in history[-20:]:
            messages.append({'role':msg.role,'content':msg.content})
        #再加载当前用户信息
        messages.append({'role':'user','content':message_text})
        
        #意图识别
        classifier = IntentClassifier()
        intent_result = classifier.classify(message_text)
        
        #路由对应Agent
        agent_map = {
            'order_query':OrderAgent(),
            'after_sales':AfterSalesAgent(),
            'general':GeneralAgent()
        }
        agent = agent_map.get(intent_result.intent,GeneralAgent())
        
        #先发conversation_id
        data = json.dumps({"conversation_id":conversation_id})
        yield f"data:{data}\n\n"
       
        #Agent流式执行
        full_response = ''
        import time
   
        for event in agent.stream(messages):
            if event['type'] == 'token':
                full_response += event['content']
                data = json.dumps({"token": event['content']})
                yield f"data:{data}\n\n"

            elif event['type'] == 'tool_call':
                    _tool_call_start = time.time()
                    _tool_call_name = event['tool']
                    _tool_call_args = event['args']
                    data = json.dumps({"type":"tool_call","tool":event['tool'],"args":event["args"]})
                    yield f"data:{data}\n\n"

            elif event['type'] == 'tool_result':
                log = ToolCallLog(
                    conversation_id = conversation_id,
                    tool_name = _tool_call_name,
                    input_args = json.dumps(_tool_call_args,ensure_ascii=False),
                    result = event['content'],
                    duration_ms = int((time.time()-_tool_call_start)*1000) if _tool_call_start else None,
                    success = True,
                    token_count = len(json.dumps(_tool_call_args) + event['content']) // 2,
                    cost = round(len(json.dumps(_tool_call_args) + event['content']) // 2 *  0.0000002, 6)
                )
                db.session.add(log)
                db.session.commit()
                data = json.dumps({"type":"tool_result","result":event['content']})
                yield f"data:{data}\n\n"
            elif event['type'] == 'done':
                 #检查是否需要确认
                if event.get("has_refund"):
                    #存待确认确认动作到数据库
                    pending = PendingAction(
                        conversation_id = conversation_id,
                        action_type = 'refund',
                        action_data = json.dumps(event.get("refund_data",{})),
                        status = 'pending'
                    )
                    db.session.add(pending)
                    db.session.commit()
                    data = json.dumps({'type':'requires_confirmation','action_id':pending.id,'data':event['refund_data']})
                    yield f"data:{data}\n\n"
                      
                # AI回复完整后存数据库
                db.session.add(Message(
                    conversation_id = conversation_id,
                    role = 'assistant',
                    content = full_response
                ))
                db.session.commit()
                data = json.dumps({'done':True})
                yield f"data:{data}\n\n"
        
      
        
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control':'no-cache','X-Accel-Buffering':'no'}
    )