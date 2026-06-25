from flask import jsonify,request,Blueprint
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token
from models import User,db
auth_bp = Blueprint('auth',__name__)
@auth_bp.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error':'用户名和密码不能为空',}),400
    username = data['username'].strip()
    password = data['password']
    if User.query.filter_by(username=username).first():
        return jsonify({'error':'用户名已存在'}),409
    user = User(
        username = username,
        password_hash = generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message':'注册成功！'})

@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error':'用户名和密码不能为空'}),400
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash,password):
        return jsonify({'error':'用户名或密码错误'}),401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token':access_token,'username':user.username}),200
    
