<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user';

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')

async function handleRegister() {
    try {
        error.value = ''
        if (confirmPassword.value !== password.value) {
            error.value = '两次密码不一致'
            return
        }
        await userStore.register(username.value, password.value)
        router.push('/login')
    } catch (e) {
        error.value = e.response?.data?.error || '注册失败'
    }

}
</script>
<template>
    <div class="auth-page">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">智<span class="logo-accent">言</span></div>
                <p class="auth-subtitle">AI 智能客服系统</p>
            </div>
            <form @submit.prevent="handleRegister">
                <div class="field">
                    <input v-model="username" placeholder="用户名" class="input" @focus="error = ''">
                </div>
                <div class="field">
                    <input v-model="password" type="password" placeholder="密码" class="input" @focus="error = ''">
                </div>
                <div class="field">
                    <input v-model="confirmPassword" type="password" placeholder="确认密码" class="input" @focus="error = ''">
                </div>

                <p v-if="error" class="error-msg">{{ error }}</p>
                <button type="submit" class="btn">注册</button>
            </form>
            <p class="footer-text">已有账号？<router-link to="/login" class="link">登录</router-link></p>
        </div>
    </div>
</template>

<style scoped>
.auth-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(150deg, #f8faff 0%, #eef2f7 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.auth-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 44px 40px 36px;
    width: 360px;
    box-shadow: 0 2px 40px rgba(0, 0, 0, 0.06), 0 1px 8px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.7);
    animation: fadeUp 0.5s ease;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.auth-header {
    text-align: center;
    margin-bottom: 32px;
}

.auth-logo {
    font-size: 30px;
    font-weight: 700;
    color: #1e293b;
    letter-spacing: -0.5px;
}

.logo-accent {
    color: #3b82f6;
}

.auth-subtitle {
    font-size: 13.5px;
    color: #94a3b8;
    margin: 6px 0 0;
    letter-spacing: 0.3px;
}

.field {
    margin-bottom: 14px;
}

.input {
    width: 100%;
    padding: 12px 14px;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
    box-sizing: border-box;
    background: #fafbfc;
    color: #1e293b;
}

.input:focus {
    border-color: #3b82f6;
    background: white;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.input::placeholder {
    color: #94a3b8;
}

.btn {
    width: 100%;
    padding: 12px;
    background: #1e293b;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    margin-top: 4px;
}

.btn:hover {
    background: #334155;
}

.btn:active {
    transform: scale(0.98);
}

.error-msg {
    color: #ef4444;
    font-size: 13px;
    margin: -6px 0 10px;
    text-align: center;
}

.footer-text {
    text-align: center;
    margin-top: 22px;
    font-size: 14px;
    color: #94a3b8;
}

.link {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
}

.link:hover {
    text-decoration: underline;
}
</style>
