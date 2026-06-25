import { defineStore } from 'pinia'
import {ref} from 'vue'
import request from '../api'

export const useUserStore = defineStore('user',()=>{
    const token = ref(localStorage.getItem('token')||'')
    const username = ref(localStorage.getItem('username')||'')

    async function register(usernameInput,password){
        const res = await request.post('/auth/register',{
            username:usernameInput,
            password
        })
        return res.data
    }

    async function login(usernameInput,password) {
        const res = await request.post('/auth/login',{
            username:usernameInput,
            password
        })
        token.value = res.data.access_token
        username.value = res.data.username
        localStorage.setItem('token',res.data.access_token)
        localStorage.setItem('username',res.data.username)
    }

    async function logout() {
        token.value = ''
        username.value = ''
        localStorage.removeItem('token')
        localStorage.removeItem('username')
    }
    return {token,username,register,login,logout}
})