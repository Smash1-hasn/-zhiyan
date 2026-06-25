<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted, nextTick } from 'vue'
import request from '../api'
import MarkdownIt from 'markdown-it'


const md = new MarkdownIt({ html: false, linkify: true })
const router = useRouter()
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const conversationId = ref(null)
const messagesRef = ref(null)
const showScrollBtn = ref(false)
const showConfirm = ref(false)
const pendingActionId = ref(null)
const pendingData = ref({})
const abortController = ref(null)
const conversations = ref([])
const conversationGroups = ref({ today: [], yesterday: [], week: [], earlier: [] })
const currentConvId = ref(null)


function stopGeneration() {
    if (abortController.value) {
        abortController.value.abort()
        abortController.value = null
    }
}

function scrollToBottom() {
    if (messagesRef.value) {
        messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
}


// 加载会话列表
async function loadConversations() {
    try {
        const res = await request.get('/conversations')
        conversations.value = res.data.data
        conversationGroups.value = getConversationGroups(res.data.data)
    } catch (e) { console.error('加载会话列表失败:',e)}
}

//切换会话
function switchConversation(convId) {
    currentConvId.value = convId
    conversationId.value = convId
    messages.value = []
    loadMessages(convId)
}

function getConversationGroups(convs) {

    const today = [], yesterday = [], week = [], earlier = []
    const now = new Date()
    const todayStr = now.toDateString()
    const yesterdayStr = new Date(now - 86400000).toDateString()
    const weekAgo = new Date(now - 7 * 86400000)

    for (const c of convs) {
        const d = new Date(c.updated_at)
        if (d.toDateString() === todayStr) today.push(c)
        else if (d.toDateString() === yesterdayStr) yesterday.push(c)
        else if (d > weekAgo) week.push(c)
        else earlier.push(c)
    }
    return { today, yesterday, week, earlier }
}


function newConversation() {
    conversationId.value = null
    messages.value = []
}

async function deleteConversation(convId) {
    try {
        await request.delete(`/conversations/${convId}`)
        loadConversations()
        if (conversationId.value === convId) {
            conversationId.value = null
            messages.value = []
        }
    } catch (e) { console.error('删除会话失败',e) }

}

// 加载历史消息
async function loadMessages(convId) {
    try {
        const res = await request.get(`/conversations/${convId}/messages`)
        messages.value = res.data.data
    } catch (e) { console.error('加载历史消息失败:','e')}
}

// 检查是否登录
onMounted(() => {
    if (!localStorage.getItem('token')) {
        router.push('/login')
    }
    loadConversations()
    messagesRef.value?.addEventListener('scroll', () => {
        const el = messagesRef.value
        if (!el) return
        const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60
        showScrollBtn.value = !atBottom
    })
})

async function sendMessage() {
    const text = inputText.value.trim()
    if (!text || loading.value) return

    // 用户消息展示到列表
    messages.value.push({ role: 'user', content: text })
    inputText.value = ''
    loading.value = true
    // 先放一个空白的ai气泡，内容逐步填充
    messages.value.push({ role: 'assistant', content: '' })
    const aiIndex = messages.value.length - 1


    try {
        const controller = new AbortController()
        abortController.value = controller
        const token = localStorage.getItem('token')
        const res = await fetch('http://localhost:5000/api/chat', {
            signal: controller.signal,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                message: text,
                conversation_id: conversationId.value
            })
        })
        if (res.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            router.push('/login')
            return
        }
        let buffer = ''
        const reader = res.body.getReader()
        const decoder = new TextDecoder()


        while (true) {
            const { done, value } = await reader.read()
            if (done) break
            buffer += decoder.decode(value, { stream: true })
            const parts = buffer.split('\n\n')
            buffer = parts.pop() || ''
            for (const part of parts) {
                if (part.startsWith('data:')) {
                    try {
                        const data = JSON.parse(part.slice(5))
                        if (data.token) {
                            messages.value[aiIndex].content += data.token
                            // 智能触底跟随
                            nextTick(() => {
                                if (messagesRef.value) {
                                    const threshold = 60 //距离底部60px以内视为在看底部消息
                                    const atBottom = messagesRef.value.scrollHeight - messagesRef.value.scrollTop - messagesRef.value.clientHeight < threshold
                                    showScrollBtn.value = !atBottom
                                    if (atBottom) {
                                        messagesRef.value.scrollTop = messagesRef.value.scrollHeight
                                    }
                                }
                            })
                        } else if (data.conversation_id) {
                            conversationId.value = data.conversation_id
                        } else if (data.type === 'requires_confirmation') {
                            pendingActionId.value = data.action_id
                            pendingData.value = data.data
                            showConfirm.value = true
                        } else if (data.type === 'tool_call') {
                            messages.value.push({
                                role: 'tool_call',
                                tool: data.tool,
                                args: data.args,
                                result: null
                            })
                        } else if (data.type === 'tool_result') {
                            const last = messages.value[messages.value.length - 1]
                            if (last.role === 'tool_call') {
                                last.result = data.result
                            }
                        }

                    } catch (e) {
                        // 忽略解析失败的行（如心跳包、格式错误等），保证流不中断
                        console.log('SSE解析跳过:', part)
                    }
                }
            }
        }
        loadConversations()
    } catch (e) {
        if (e.name === 'AbortError') return //用户手动停止不报错
        if (e.message?.includes('401') || e.toString().includes('401')) {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            router.push('/login')
            return
        }
        messages.value[aiIndex].content = '出错了,请稍后重试'

    } finally {
        loading.value = false
    }
}
async function confirmAction() {
    try {
        const res = await request.post('/confirm', {
            action_id: pendingActionId.value
        })
        messages.value.push({ role: 'assistant', content: res.data.result })
    } catch (e) {
        messages.value.push({ role: 'assistant', content: '确认失败，请稍候重新再试' })
    }
    showConfirm.value = false
    pendingActionId.value = null
    pendingData.value = {}
}

function cancelConfirm() {
    showConfirm.value = false
    pendingActionId.value = null
    pendingData.value = {}
}
</script>

<template>
    <div class="app-layout">
        <!-- 左栏 -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>智言</h2>
            </div>
            <button @click="newConversation" class="new-chat-btn">＋ 新对话</button>
            <div class="conv-list">
                <div v-for="(convs, group) in conversationGroups" :key="group">
                    <div v-if="convs.length" class="group-label">{{ group === 'today' ? '今天' : group === 'yesterday' ?
                        '昨天' : group === 'week' ? '最近7天' : '更早' }}</div>
                    <div v-for="conv in convs" :key="conv.id"
                        :class="['conv-item', { active: conv.id === conversationId }]"
                        @click="switchConversation(conv.id)">
                        <div class="conv-title">{{ conv.title || '新会话' }}</div>
                        <button @click.stop="deleteConversation(conv.id)" class="del-btn">✕</button>
                    </div>
                </div>
            </div>

            <div class="sidebar-footer">
                <button @click="router.push('/admin')" class="sidebar-link">管理面板</button>
                <button @click="router.push('/login')" class="sidebar-link">退出</button>
            </div>
        </div>

        <!-- 主区 -->
        <div class="main">
            <div class="messages" ref="messagesRef">
                <div v-for="(msg, i) in messages" :key="i">
                    <template v-if="msg.role === 'tool_call'">
                        <div class="tool-card">
                            <div class="tool-card-header">🔧 {{ msg.tool }}</div>
                            <div class="tool-card-body">
                                <div class="tool-args">参数:{{ JSON.stringify(msg.args) }}</div>
                                <div v-if="msg.result" class="tool-result">结果:{{ msg.result }}</div>
                                <div v-else class="tool-loading">执行中...</div>
                            </div>
                        </div>
                    </template>
                    <template v-else>
                        <div :class="['msg-row', msg.role]">
                            <div class="bubble" v-html="md.render(msg.content)"></div>
                        </div>
                    </template>
                </div>
                <div v-if="loading" class="msg-row assistant">
                    <div class="bubble">思考中...</div>
                </div>
            </div>
            <button v-if="showScrollBtn" class="scroll-btn" @click="scrollToBottom">↓ </button>

            <div class="input-area">
                <textarea v-model="inputText" placeholder="输入消息..." @keydown.enter.exact="sendMessage"
                    :disabled="loading" rows="1" class="input-box"></textarea>
                <button v-if="loading" class="stop-btn" @click="stopGeneration">停止</button>
                <button v-else @click="sendMessage" :disabled="!inputText.trim()" class="send-btn">发送</button>
            </div>
        </div>

        <!-- 确认弹窗 -->
        <div v-if="showConfirm" class="confirm-overlay">
            <div class="confirm-dialog">
                <h3>确认退款操作</h3>
                <div class="confirm-detail">
                    <p><strong>订单号:</strong> {{ pendingData.order_id }}</p>
                    <p><strong>退款金额:</strong> {{ pendingData.amount }} 元</p>
                    <p><strong>退款原因:</strong> {{ pendingData.reason }}</p>
                </div>
                <div class="confirm-buttons">
                    <button @click="cancelConfirm" class="cancel-btn">取消</button>
                    <button @click="confirmAction" class="confirm-btn">确认退款</button>
                </div>
            </div>
        </div>
    </div>
</template>


<style scoped>
.app-layout {
    display: flex;
    height: 100vh;
    background: #fff;
    width: 100%;
}

/* 左栏 */
.sidebar {
    width: 260px;
    min-width: 260px;
    background: #f7f7f8;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #e5e5e5;
}

.sidebar-header {
    padding: 16px 16px 0;
}

.sidebar-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}

.new-chat-btn {
    margin: 12px;
    padding: 10px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    text-align: center;
}

.new-chat-btn:hover {
    background: #f0f0f0;
}

.conv-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px 8px;
}

.conv-item {
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    margin-bottom: 2px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

.conv-item:hover {
    background: #e8e8ea;
}

.conv-item.active {
    background: #e3e3e5;
}

.conv-title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
}

.del-btn {
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    font-size: 12px;
    display: none;
    padding: 2px 4px;
}

.conv-item:hover .del-btn {
    display: block;
}

.sidebar-footer {
    padding: 8px 12px;
    border-top: 1px solid #e5e5e5;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.sidebar-link {
    padding: 8px 12px;
    background: none;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-size: 13px;
    color: #666;
}

.sidebar-link:hover {
    background: #e8e8ea;
}

/* 主区 */
.main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px 40px;
}

.msg-row {
    margin-bottom: 24px;
    display: flex;
}

.msg-row.user {
    justify-content: flex-end;
}

.msg-row.assistant {
    justify-content: flex-start;
}

.bubble {
    max-width: 60%;
    padding: 8px 14px;
    line-height: 1.6;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
    width: fit-content;
}

.msg-row.user .bubble {
    background: #e8e8ea;
    color: #333;
    border-radius: 16px 16px 4px 16px;
}


.msg-row.assistant .bubble {
    background: none;
    padding: 0;
    max-width: 100%;
    color: #333;
}


/* 输入区 */
.input-area {
    padding: 12px 40px;
    border-top: 1px solid #e5e5e5;
    display: flex;
    gap: 8px;
    align-items: flex-end;
    background: #fff;
}

.input-box {
    flex: 1;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 12px;
    outline: none;
    resize: none;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    max-height: 150px;
}

.input-box:focus {
    border-color: #3b82f6;
}

.send-btn {
    padding: 10px 24px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
}

.send-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.stop-btn {
    padding: 8px 20px;
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 13px;
}

/* 工具卡片 */
.tool-card {
    margin-bottom: 12px;
}

.tool-card-header {
    background: #f0f4f8;
    padding: 8px 12px;
    border-radius: 8px 8px 0 0;
    font-size: 13px;
    font-weight: 600;
    color: #2563eb;
}

.tool-card-body {
    background: #f8fafc;
    padding: 8px 12px;
    border-radius: 0 0 8px 8px;
    font-size: 13px;
}

.tool-args {
    font-family: monospace;
    background: #eee;
    padding: 4px 8px;
    border-radius: 4px;
    margin: 4px 0;
    font-size: 12px;
}

.tool-result {
    margin-top: 4px;
    padding: 4px 8px;
    background: #e8f5e9;
    border-radius: 4px;
    font-size: 12px;
}

.tool-loading {
    color: #999;
    font-style: italic;
    margin-top: 4px;
    font-size: 12px;
}

/* 确认弹窗 */
.confirm-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.confirm-dialog {
    background: white;
    padding: 24px;
    border-radius: 12px;
    max-width: 420px;
    width: 90%;
}

.confirm-dialog h3 {
    margin: 0 0 16px;
    color: #e74c3c;
}

.confirm-detail {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 14px;
}

.confirm-buttons {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
}

.confirm-btn {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 8px 24px;
    border-radius: 6px;
    cursor: pointer;
}

.cancel-btn {
    background: #95a5a6;
    color: white;
    border: none;
    padding: 8px 24px;
    border-radius: 6px;
    cursor: pointer;
}

.bubble :deep(code) {
    background: #e8e8e8;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    font-family: monospace;
}

.bubble :deep(pre) {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;
}

.bubble :deep(pre code) {
    background: none;
    padding: 0;
    color: inherit;
}

.bubble :deep(p) {
    margin: 8px 0;
}

.bubble :deep(ul),
.bubble :deep(ol) {
    padding-left: 20px;
    margin: 8px 0;
}

.bubble :deep(li) {
    margin: 4px 0;
}

.bubble :deep(a) {
    color: #3b82f6;
    text-decoration: underline;
}

.scroll-btn {
    position: fixed;
    bottom: 80px;
    left: 50%;
    transform: translateX(-50%);
    padding: 8px 20px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 20px;
    cursor: pointer;
    font-size: 13px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 10;
}

.scroll-btn:hover {
    background: #f5f5f5;
}

.group-label {
    padding: 8px 12px 4px;
    font-size: 11px;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>

<style>
#app {
    max-width: none !important;
    width: 100% !important;
    margin: 0 !important;
    border-inline: none !important;
    text-align: left !important;
}
</style>
