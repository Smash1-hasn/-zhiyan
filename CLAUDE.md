# 智言项目规范

## 代码交付审查清单（每次给代码前必须过）

### 语法正确性
- [ ] 变量名/函数名是否拼写正确
- [ ] 条件判断逻辑是否正确（`if/elif/else` 顺序、`and/or` 使用）
- [ ] HTML 属性是否用空格分隔（禁止逗号）
- [ ] Python 字典/列表/函数调用括号是否正确
- [ ] 模板字符串引号是否冲突（`f'...{dict[\'key\']}...'` → 应改为双引号外层）

### 导入完整性
- [ ] 文件头部所有 import 是否齐全
- [ ] `__init__.py` 是否导出了需要的类/函数
- [ ] 蓝图是否在 `app.py` 或 `api/__init__.py` 注册
- [ ] 数据模型是否在 `models/__init__.py` 注册
- [ ] 迁移是否已生成并执行

### 异常处理
- [ ] 数据库操作是否有 `try/except` 兜底
- [ ] `@jwt_required()` 是否加了括号
- [ ] 生成器/流式输出中发生异常是否仍能 yield `done` 事件
- [ ] 多次 `db.session.commit()` 应合并为一次（事务一致性）

### 安全
- [ ] 跨会话操作是否校验了 `user_id` 归属
- [ ] 高风险操作是否有二次确认机制
- [ ] token 过期是否有 401 处理

### 模板/View
- [ ] `v-for` 和 `v-if` 层级是否正确
- [ ] `v-for` 有 `:key`
- [ ] `ref` 变量在 `<script>` 中定义了、在 `<template>` 中绑定了
- [ ] 事件类型用英文小写（`token`/`tool_call`/`tool_result`/`done`）

## 项目约定

### 文件命名
- Python 文件：全小写下划线（`order_agent.py`）
- Vue 文件：首字母大写（`Chat.vue`）
- 类名：首字母大写驼峰（`OrderAgent`、`IntentClassifier`）
- 函数/变量：全小写下划线（`send_message`、`conversation_id`）

### API 事件格式（SSE）
```json
{"type": "token", "content": "..."}
{"type": "tool_call", "tool": "query_order", "args": {...}}
{"type": "tool_result", "result": "..."}
{"type": "requires_confirmation", "action_id": 1, "data": {...}}
{"type": "conversation_id", "conversation_id": 1}
{"type": "done"}
```

### 三层架构
- `api/` — HTTP 接口层（只负责请求/响应）
- `ai/` — AI 逻辑层（Agent、工具、意图分类）
- `models/` — 数据模型层（SQLAlchemy 表定义）

层间调用方向：`api/` → `ai/` → `models/`
禁止反向调用（`models/` 里不能 import `api/`）

### 常见错误备忘
1. `@jwt_required` 忘记加括号写成 `@jwt_required`
2. SSE 事件结尾缺 `\n\n`
3. `v-for` 内用 `v-else-if` 层级错误（应用 `v-if`/`v-else` 在 `v-for` 的**内部元素**上）
4. 流式生成器中未捕获异常导致前端 stream 中断
5. `db.session.commit()` 拼成 `db.sessiond.commit()`
