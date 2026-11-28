<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { api, type PhotoDetail } from '@/api/client'

const route = useRoute()
const photoId = Number(route.params.id)

const detail = ref<PhotoDetail | null>(null)
const message = ref('')

function formatTime(value: string): string {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(async () => {
  try {
    detail.value = await api.get<PhotoDetail>(`/api/photos/${photoId}`)
  } catch {
    message.value = '照片不可访问'
  }
})
</script>

<template>
  <div class="card">
    <template v-if="detail">
      <div class="photo-frame">
        <img :src="detail.original_url" :alt="`照片 ${detail.photo.id}`" />
      </div>
      <p class="meta-line">
        上传者：{{ detail.photo.uploader.username }} ｜ 上传时间：{{ formatTime(detail.photo.created_at) }} ｜
        相册编号：{{ detail.photo.album_id }}
      </p>
      <p class="meta-line">
        点赞：{{ detail.like.like_count }}<template v-if="detail.like.liked">（已点赞）</template>
      </p>
      <h2>评论（{{ detail.comments.length }}）</h2>
      <div v-if="detail.comments.length === 0" class="hint">暂无评论</div>
      <div v-for="comment in detail.comments" :key="comment.id" class="comment">
        <div class="comment-meta">{{ comment.author.username }} · {{ formatTime(comment.created_at) }}</div>
        <div>{{ comment.body }}</div>
      </div>
      <p class="hint">评论与点赞操作将在对应模块联调时开放</p>
    </template>
    <template v-else>
      <p v-if="message" class="alert alert-error">{{ message }}</p>
    </template>
    <div class="actions">
      <RouterLink class="btn btn-ghost" :to="{ name: 'album-detail', params: { id: detail?.photo.album_id } }">
        返回相册
      </RouterLink>
    </div>
  </div>
</template>
