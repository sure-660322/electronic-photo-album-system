<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { useSession } from '@/stores/session'

const username = ref('')
const password = ref('')
const message = ref('')
const pending = ref(false)

const { login } = useSession()
const router = useRouter()
const route = useRoute()

async function submit() {
  message.value = ''
  pending.value = true
  try {
    const user = await login(username.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
    if (redirect) {
      router.push(redirect)
    } else {
      // 管理员进入类别管理后台（待该模块实现，暂到浏览页），普通用户进入浏览页。
      router.push({ name: 'albums' })
      void user
    }
  } catch (error) {
    message.value = error instanceof ApiError ? error.message : '登录失败，请稍后重试'
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="card auth-card">
    <h1>登录</h1>
    <p class="subtitle">普通用户与管理员共用登录入口</p>
    <form @submit.prevent="submit">
      <div class="field">
        <label for="username">用户名</label>
        <input id="username" v-model="username" autocomplete="username" />
      </div>
      <div class="field">
        <label for="password">密码</label>
        <input id="password" v-model="password" type="password" autocomplete="current-password" />
      </div>
      <p v-if="message" class="alert alert-error">{{ message }}</p>
      <div class="actions">
        <button class="btn" type="submit" :disabled="pending">登录</button>
        <RouterLink to="/register" class="hint">没有账号？去注册</RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped>
.auth-card {
  max-width: 420px;
  margin: 48px auto;
}
</style>
