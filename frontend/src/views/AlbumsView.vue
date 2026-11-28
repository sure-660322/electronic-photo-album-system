<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { api, type Album } from '@/api/client'

const albums = ref<Album[]>([])
const message = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await api.get<{ items: Album[] }>('/api/albums?scope=visible')
    albums.value = data.items
  } catch {
    message.value = '相册列表加载失败，请刷新重试'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="card">
    <h1>浏览相册</h1>
    <p class="subtitle">可见范围为所有公开相册与本人全部相册</p>
    <p v-if="message" class="alert alert-error">{{ message }}</p>
    <div v-if="loading" class="empty">加载中……</div>
    <div v-else-if="albums.length === 0" class="empty">暂无相册</div>
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
