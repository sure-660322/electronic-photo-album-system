<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError, api, type Category } from '@/api/client'

const categories = ref<Category[]>([])
const form = reactive({ name: '', category_id: 0, visibility: 'public' as 'public' | 'private' })
const fieldErrors = reactive<Record<string, string>>({})
const message = ref('')
const pending = ref(false)

const router = useRouter()

onMounted(async () => {
  const data = await api.get<{ items: Category[] }>('/api/categories')
  categories.value = data.items
  if (data.items.length === 0) {
    message.value = '暂无可用类别，请联系管理员维护类别后再创建相册'
  } else {
    form.category_id = data.items[0].id
  }
})

async function submit() {
  message.value = ''
  for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
  if (!form.name.trim()) {
    fieldErrors.name = '请填写相册名称'
    return
  }
  pending.value = true
  try {
    await api.post('/api/albums', {
      name: form.name.trim(),
      category_id: form.category_id,
      visibility: form.visibility,
    })
    router.push({ name: 'my-albums' })
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.field) fieldErrors[error.field] = error.message
      else message.value = error.message
      if (error.code === 'CATEGORY_UNAVAILABLE') {
        const data = await api.get<{ items: Category[] }>('/api/categories')
        categories.value = data.items
        if (data.items.length > 0) form.category_id = data.items[0].id
      }
    } else {
      message.value = '创建失败，请稍后重试'
    }
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="card form-card">
    <h1>创建相册</h1>
    <p class="subtitle">相册创建后可在“我的相册”中修改名称、类别与可见性</p>
    <form @submit.prevent="submit">
      <div class="field">
        <label for="name">相册名称（1–100 字符）</label>
        <input id="name" v-model="form.name" maxlength="100" />
        <p v-if="fieldErrors.name" class="error">{{ fieldErrors.name }}</p>
      </div>
      <div class="field">
        <label for="category">类别</label>
        <select id="category" v-model.number="form.category_id">
          <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <p v-if="fieldErrors.category_id" class="error">{{ fieldErrors.category_id }}</p>
      </div>
      <div class="field">
        <label>可见性</label>
        <select v-model="form.visibility">
          <option value="public">公开（所有登录用户可浏览）</option>
          <option value="private">私有（仅本人可浏览）</option>
        </select>
      </div>
      <p v-if="message" class="alert alert-error">{{ message }}</p>
      <div class="actions">
        <button class="btn" type="submit" :disabled="pending">创建</button>
        <RouterLink class="btn btn-ghost" :to="{ name: 'my-albums' }">返回</RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped>
.form-card {
  max-width: 520px;
}
</style>
