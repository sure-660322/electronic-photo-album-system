<script setup lang="ts">
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { useSession } from '@/stores/session'

const form = reactive({
  username: '',
  email: '',
  password: '',
  password_confirmation: '',
})
const fieldErrors = reactive<Record<string, string>>({})
const message = ref('')
const pending = ref(false)

const { register } = useSession()
const router = useRouter()

function localValidate(): boolean {
  for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
  if (!form.username.trim()) fieldErrors.username = '请填写用户名'
  if (!form.email.trim()) fieldErrors.email = '请填写邮箱'
  if (form.password.length < 8) fieldErrors.password = '密码至少 8 位'
  if (form.password !== form.password_confirmation) {
    fieldErrors.password_confirmation = '两次密码不一致'
  }
  return Object.keys(fieldErrors).length === 0
}

async function submit() {
  message.value = ''
  if (!localValidate()) return
  pending.value = true
  try {
    await register({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      password_confirmation: form.password_confirmation,
    })
    router.push({ name: 'login' })
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.field) fieldErrors[error.field] = error.message
      else message.value = error.message
    } else {
      message.value = '注册失败，请稍后重试'
    }
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="card auth-card">
    <h1>注册</h1>
    <p class="subtitle">注册后即可创建相册并上传照片</p>
    <form @submit.prevent="submit">
      <div class="field">
        <label for="username">用户名</label>
        <input id="username" v-model="form.username" />
        <p v-if="fieldErrors.username" class="error">{{ fieldErrors.username }}</p>
      </div>
      <div class="field">
        <label for="email">邮箱</label>
        <input id="email" v-model="form.email" type="email" />
        <p v-if="fieldErrors.email" class="error">{{ fieldErrors.email }}</p>
      </div>
      <div class="field">
        <label for="password">密码（8–128 位）</label>
        <input id="password" v-model="form.password" type="password" autocomplete="new-password" />
        <p v-if="fieldErrors.password" class="error">{{ fieldErrors.password }}</p>
      </div>
      <div class="field">
        <label for="password_confirmation">确认密码</label>
        <input id="password_confirmation" v-model="form.password_confirmation" type="password" autocomplete="new-password" />
        <p v-if="fieldErrors.password_confirmation" class="error">{{ fieldErrors.password_confirmation }}</p>
      </div>
      <p v-if="message" class="alert alert-error">{{ message }}</p>
      <div class="actions">
        <button class="btn" type="submit" :disabled="pending">注册</button>
        <RouterLink to="/login" class="hint">已有账号？去登录</RouterLink>
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
