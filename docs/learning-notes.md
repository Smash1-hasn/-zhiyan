# 🧠 智言项目 · 学习笔记

> 每次学新概念就追加在这里，方便复习。
> 日期格式：YYYY-MM-DD

---

## 2026-06-08

### 1. Flask 工厂模式（create_app）

**场景：** 为什么不用 `app = Flask(__name__)` 直接写在全局？

**一句话：** 为了灵活——测试时可以创建多个不同的 app 实例。

**具体做法：**
```python
db = SQLAlchemy()          # 先创建对象，不绑定 app

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)        # 再绑定到 app
    return app
```

**面试关联：** "Flask 如何避免循环导入？" → 工厂函数 + SQLAlchemy 延迟初始化（`init_app`）

### 2. `db = SQLAlchemy()` vs `db = SQLAlchemy(app)`

| 写法 | 特点 | 什么时候用 |
|------|------|-----------|
| `SQLAlchemy(app)` | 简单直接 | 小脚本、永远不会切换环境 |
| `SQLAlchemy()` + `init_app` | 灵活，可切换环境 | 实际项目、需要测试 |

### 3. 蓝图（Blueprint）

**用途：** 把路由按功能分组。

```python
# api/__init__.py
from flask import Blueprint
api_bp = Blueprint('api', __name__)

# app.py 注册
app.register_blueprint(api_bp, url_prefix='/api')
```

效果：`api/auth.py` 里定义的路由自动挂在 `/api/auth/xxx` 下。

### 4. SQLAlchemy 模型基础

一个模型 = 一张数据库表。

```python
class User(db.Model):
    __tablename__ = 'user'           # 数据库里的表名
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
```

**常用字段类型：**
- `db.Integer` — 整数
- `db.String(N)` — 字符串，N 是最大长度
- `db.Text` — 长文本
- `db.Float` — 浮点数
- `db.Boolean` — 布尔值
- `db.DateTime` — 日期时间
- `db.Enum('a','b')` — 枚举

**常用约束：**
- `primary_key=True` — 主键
- `unique=True` — 唯一
- `nullable=False` — 不能为空
- `default=xxx` — 默认值

**关系（relationship）：**
```python
# "一个用户有多条对话" → 一对多
class User(db.Model):
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic')

class Conversation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # backref='user' 表示可以从 Conversation 直接 .user 拿到对应的 User 对象
```

### 5. Flask-Migrate（数据库迁移）

当模型变了（比如加了字段），不需要手写 ALTER TABLE，而是：
```bash
flask db init       # 第一次：初始化迁移目录
flask db migrate    # 每次模型变化：生成迁移脚本
flask db upgrade    # 执行迁移到数据库
```

### 6. JSON 在 MySQL 里的存法

注意：SQLAlchemy 没有完美的 JSON 字段支持（旧版本），所以：
- 存的时候：`json.dumps(data)` → 变成字符串
- 取的时候：`json.loads(data)` → 变回字典
- 字段类型用 `db.Text`

---

## 2026-06-09

### 7. 蓝图（Blueprint）基础定义

Blueprint = 路由分组。最小定义：

```python
from flask import Blueprint
api_bp = Blueprint('api', __name__)
```

然后在 app.py 里：
```python
from api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')
```

### 8. Flask-Migrate 必知：必须 import 模型

Flask-Migrate 只认识**被导入过的模型**。如果 `models/` 没有被任何文件 import，`flask db migrate` 会生成空脚本。

**解决：** 在 `create_app()` 函数里加一行：
```python
import models  # 让 Migrate 能检测到所有模型
```

### 9. 迁移三连

```bash
flask db init          # 只跑一次，创建 migrations/ 目录
flask db migrate -m "备注"  # 每次模型变化跑这个
flask db upgrade       # 真正改数据库
```

### 10. .flaskenv 文件

在项目根目录放 `.flaskenv`，可以免去每次敲 export：

```
FLASK_APP=app.py
FLASK_ENV=development
```

Flask 启动时会自动读取（需要 python-dotenv 包）。

---

## 2026-06-09（续）

### 11. API 设计规范——状态码

| 状态码 | 意思 | 什么时候用 |
|--------|------|-----------|
| 200 | 成功 | GET 请求、登录成功 |
| 201 | 创建成功 | POST 注册成功 |
| 400 | 请求参数错误 | 缺字段、格式不对 |
| 401 | 未认证 | 用户名或密码错误 |
| 409 | 冲突 | 用户名已存在 |

### 12. Python 逻辑运算陷阱：not + and/or

```python
# ❌ 错误（只会拦住"全都缺"的情况）
if not data and not data.get('username') and not data.get('password'):

# ✅ 正确（"只要有一样缺"就拦住）
if not data or not data.get('username') or not data.get('password'):
```

**记忆口诀：** 检查参数缺失用 `or`——只要有一个不对就报错。

### 13. 蓝图嵌套（Blueprint 套 Blueprint）

```python
# api/__init__.py
from .auth import auth_bp

api_bp = Blueprint('api', __name__)
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
```

路径计算：`/api`(api_bp) + `/auth`(子蓝图前缀) + `/register`(路由)
→ 最终：`POST /api/auth/register`

---

## 待补充知识点占点

（每次学新内容追加到这里）

