from flask import Flask
from flask_cors import CORS
from config import config
from extensions import db,migrate,jwt



def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost"]}}, supports_credentials=True)

    import models
    
    from api.auth import auth_bp
    from api.chat import chat_bp
    from api.confirm import confirm_bp
    from api.conversation import conv_bp
    from api.admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(confirm_bp,url_prefix='/api/confirm')
    app.register_blueprint(conv_bp,url_prefix='/api/conversations')
    app.register_blueprint(admin_bp,url_prefix='/api/admin')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()    