<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError, api, type Album, type Category } from '@/api/client'

const route = useRoute()
const router = useRouter()

const albumId = Number(route.params.id)
const categories = ref<Category[]>([])
const form = reactive({
  name: '',
  category_id: 0,
  visibility: 'public' as 'public' | 'private',
  version: 0,
})
const fieldErrors = reactive<Record<string, string>>({})
const message = ref('')
const notice = ref('')
const pending = ref(false)
const loaded = ref(false)

async function reloadAlbum(keepDraft: boolean) {
  const album = await api.get<Album>(`/api/albums/${albumId}?scope=mine`)
  if (!keepDraft) {
    form.name = album.name
    form.category_id = album.category.id
    form.visibility = album.visibility
  }
  form.version = album.version
}

onMounted(async () => {
  try {
    await reloadAlbum(false)
    const data = await api.get<{ items: Category[] }>('/api/categories')
    categories.value = data.items
  } catch (error) {
    message.value = error instanceof ApiError ? error.message : '相册加载失败'
  } finally {
    loaded.value = true
  }
})

async function submit() {
  message.value = ''
  notice.value = ''
  for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
  if (!form.name.trim()) {
    fieldErrors.name = '请填写相册名称'
    return
  }
  pending.value = true
  try {
    await api.put(`/api/albums/${albumId}`, {
      name: form.name.trim(),
      category_id: form.category_id,
      visibility: form.visibility,
      version: form.version,
    })
    router.push({ name: 'my-albums' })
  } catch (error) {
    if (!(error instanceof ApiError)) {
      message.value = '保存失败，请稍后重试'
      return
    }
    if (error.field) {
      fieldErrors[error.field] = error.message
      return
    }
    if (error.code === 'ALBUM_VERSION_CONFLICT') {
      // 保留本次草稿，取最新版本号供用户确认后重新提交。
      notice.value = '相册已被其他页面修改，已按最新数据刷新版本，请核对后重新保存'
      await reloadAlbum(true)
    } else if (error.code === 'CATEGORY_UNAVAILABLE') {
      notice.value = '所选类别已失效，请重新选择类别'
      const data = await api.get<{ items: Category[] }>('/api/categories')
      categories.value = data.items
      if (data.items.length > 0 && !data.items.some((c) => c.id === form.category_id)) {
        form.category_id = data.items[0].id
      }
    } else if (error.code === 'ALBUM_UNAVAILABLE') {
      message.value = '相册不存在或无权修改'
    } else {
      message.value = error.message
    }
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="card form-card">
    <h1>修改相册</h1>
    <p class="subtitle">提交时按载入版本做并发检查，版本过期会提示刷新</p>
    <template v-if="loaded">
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
        <p v-if="notice" class="alert alert-info">{{ notice }}</p>
        <p v-if="message" class="alert alert-error">{{ message }}</p>
        <div class="actions">
          <button class="btn" type="submit" :disabled="pending">保存修改</button>
          <RouterLink class="btn btn-ghost" :to="{ name: 'my-albums' }">返回</RouterLink>
        </div>
      </form>
    </template>
  </div>
</template>

<style scoped>
.form-card {
  max-width: 520px;
}
</style>
