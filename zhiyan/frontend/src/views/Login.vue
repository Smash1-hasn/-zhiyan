<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore() 

const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
    try{
        error.value = ''
        await userStore.login(username.value,password.value)
        router.push('/chat')
    } catch(e){
        error.value = e.response?.data?.error || '登录失败'
    }
}
</script>

<template>
    <div class="login-page">
        <h2>登录</h2>
        <form @submit.prevent="handleLogin">
            <input v-model="username" placeholder="用户名">
            <input v-model="password" type="password" placeholder='密码'>
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit">登录</button>
        </form>

        <p>还没有账号? <router-link to="/register">注册</router-link></p>
    </div>
</template>

<style scoped>
.login-page { max-width: 400px; margin: 100px auto; padding: 20px; }
input { display: block; width: 100%; margin-bottom: 12px; padding: 8px; }
button { width: 100%; padding: 10px; background: #4a90d9; color: white; border: none; border-radius: 4px; cursor: pointer; }
.error { color: red; font-size: 14px; }
</style>