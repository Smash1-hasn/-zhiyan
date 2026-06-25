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
    try{
        error.value = ''
        if (confirmPassword.value !== password.value){
            error.value = '两次密码不一致'
            return 
        } 
        await userStore.register(username.value,password.value)
        router.push('/login')
    } catch(e){
        error.value = e.response?.data?.error || '注册失败' 
    }
    
}
</script>

<template>
    <div class="register-page">
        <h2>注册</h2>
        <form @submit.prevent="handleRegister">
            <input v-model="username" placeholder="用户名">
            <input v-model="password" type="password" placeholder="密码">
            <input v-model="confirmPassword" type="password" placeholder="确认密码">
            <p v-if="error" class="error">{{ error }}</p>
            <button type="submit">注册</button>
        </form>
        
        <p>已有账号? <router-link to="/login">登录</router-link></p>
    </div>
</template>

<style scoped>
.register-page { max-width: 400px; margin: 100px auto; padding: 20px; }
input { display: block; width: 100%; margin-bottom: 12px; padding: 8px; }
button { width: 100%; padding: 10px; background: #4a90d9; color: white; border: none; border-radius: 4px; cursor: pointer; }
.error { color: red; font-size: 14px; }
</style>