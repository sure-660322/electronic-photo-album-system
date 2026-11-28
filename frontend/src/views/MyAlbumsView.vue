<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, type Album } from '@/api/client'

const albums = ref<Album[]>([])
const message = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await api.get<{ items: Album[] }>('/api/albums?scope=mine')
    albums.value = data.items
  } catch {
    message.value = '我的相册加载失败，请刷新重试'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="card">
    <div class="head-row">
      <div>
        <h1>我的相册</h1>
        <p class="subtitle">创建相册、修改相册、上传图片都从这里进入</p>
      </div>
      <RouterLink class="btn" :to="{ name: 'album-new' }">创建相册</RouterLink>
    </div>
    <p v-if="message" class="alert alert-error">{{ message }}</p>
    <div v-if="loading" class="empty">加载中……</div>
    <div v-else-if="albums.length === 0" class="empty">还没有相册，点击右上角“创建相册”开始</div>
    <div v-else class="grid">
      <RouterLink
        v-for="album in albums"
        :key="album.id"
        class="tile"
        :to="{ name: 'album-detail', params: { id: album.id } }"
      >
        <div class="tile-body">
          <div class="tile-title">{{ album.name }}</div>
          <div class="tile-meta">
            <span class="tag" :class="album.visibility === 'public' ? 'tag-public' : 'tag-private'">
              {{ album.visibility === 'public' ? '公开' : '私有' }}
            </span>
            {{ album.category.name }}
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.head-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}
</style>
