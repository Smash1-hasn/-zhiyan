<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '../api';

const router = useRouter()
const stats = ref(null)

onMounted(() => {
    if (!localStorage.getItem('token')) {
        router.push('/login')
        return
    }
    loadStats()
})

async function loadStats() {
    try {
        const res = await request.get('/admin/stats')
        stats.value = res.data
    } catch (e) {
        if (e.response?.status === 401) router.push('/login')
        console.error('加载统计数据失败', e)
    }
}
</script>

<template>
    <div class="admin-page">
        <div class="admin-header">
            <h2>管理面板</h2>
            <button @click="router.push('/chat')" class="back-btn">返回对话</button>
        </div>


        <div class="stats-grid" v-if="stats">
            <div class="stat-card">
                <div class="stat-number">{{ stats.today_conversations }}</div>
                <div class="stat-label">今日咨询</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_conversations }}</div>
                <div class="stat-label">总会话数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_tokens }}</div>
                <div class="stat-label">总token消耗</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${{ stats.total_cost }}</div>
                <div class="stat-label">预估成本</div>
            </div>
        </div>

        <div class="section" v-if="stats?.tools?.length">
            <h3>工具调用统计</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>工具名</th>
                        <th>调用次数</th>
                        <th>成功率</th>
                        <th>平均耗时</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="t in stats.tools" :key="t.tool">
                        <td>{{ t.tool }}</td>
                        <td>{{ t.total }}</td>
                        <td>{{ t.success_rate }}</td>
                        <td>{{ t.avg_duration }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div v-else class="empty-state">暂无工具调用记录</div>
    </div>
</template>

<style scoped>
.admin-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 24px;
}

.admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.back-btn {
    padding: 8px 16px;
    background: #4a90d9;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}


.stat-card {
    background: #f0f4f8;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}

.stat-number {
    font-size: 36px;
    font-weight: bold;
    color: #4a90d9;
}

.stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 4px;
}

.section {
    background: white;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 16px;
}

.section h3 {
    margin: 0 0 16px;
    font-size: 16px;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.data-table th,
.data-table td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #eee;
}

.data-table th {
    color: #999;
    font-weight: normal;
    font-size: 12px;
    text-transform: uppercase;
}

.empty-state {
    text-align: center;
    padding: 40px;
    color: #999;
    font-size: 14px;
}
</style>