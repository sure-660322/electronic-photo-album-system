<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'

import { useSession } from '@/stores/session'

const { state, logout } = useSession()
const router = useRouter()

async function onLogout() {
  await logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="shell">
    <header class="topbar" v-if="state.user">
      <span class="brand">电子相册</span>
      <nav class="nav">
        <RouterLink :to="{ name: 'albums' }">浏览相册</RouterLink>
        <RouterLink v-if="state.user.role === 'member'" :to="{ name: 'my-albums' }">我的相册</RouterLink>
      </nav>
      <div class="who">
        <span>{{ state.user.username }}（{{ state.user.role === 'admin' ? '管理员' : '普通用户' }}）</span>
        <button class="btn btn-ghost" @click="onLogout">退出登录</button>
      </div>
    </header>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>
