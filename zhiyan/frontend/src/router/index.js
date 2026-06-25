import { createRouter, createWebHistory } from 'vue-router'


const routes = [
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/register', component: () => import('../views/Register.vue') },
    { path: '/chat', component: () => import('../views/Chat.vue') },
    { path: '/admin', component: () => import('../views/Admin.vue') },
    { path: '/', redirect: '/chat' }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to) => {
    const token = localStorage.getItem('token')
    if (to.path !== '/login' && to.path !== '/register' && !token) {
        return '/login'
    }
})

export default router