<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { ApiError, api, type Album, type Photo } from '@/api/client'
import { useSession } from '@/stores/session'

const route = useRoute()
const albumId = Number(route.params.id)
const { state } = useSession()

const album = ref<Album | null>(null)
const photos = ref<Photo[]>([])
const message = ref('')
const uploadMessage = ref('')
const pendingUpload = ref(false)
const loading = ref(true)

const isOwner = () =>
  album.value !== null && state.user !== null && album.value.owner_id === state.user.id

async function loadPhotos() {
  const data = await api.get<{ items: Photo[] }>(`/api/albums/${albumId}/photos`)
  photos.value = data.items
}

onMounted(async () => {
  try {
    album.value = await api.get<Album>(`/api/albums/${albumId}`)
    await loadPhotos()
  } catch (error) {
    message.value =
      error instanceof ApiError && error.code === 'ALBUM_UNAVAILABLE'
        ? '相册不可访问'
        : '相册加载失败'
  } finally {
    loading.value = false
  }
})

async function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploadMessage.value = ''
  pendingUpload.value = true
  // 每次选择生成新的 upload_id；同一文件重试时沿用，服务端按其幂等去重。
  const formData = new FormData()
  formData.append('file', file)
  formData.append('upload_id', crypto.randomUUID())
  try {
    await api.upload(`/api/albums/${albumId}/photos`, formData)
    await loadPhotos()
    input.value = ''
  } catch (error) {
    if (error instanceof ApiError) {
      uploadMessage.value = error.message
    } else {
      uploadMessage.value = '上传失败，请重试'
    }
  } finally {
    pendingUpload.value = false
  }
}

function onThumbError(event: Event) {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="190" height="150"><rect width="100%" height="100%" fill="%23eceef1"/><text x="50%" y="50%" fill="%236b7683" text-anchor="middle" dy=".3em" font-size="13">缩略图加载失败</text></svg>'
}
</script>

<template>
  <div class="card">
    <div class="head-row">
      <div>
        <h1>{{ album?.name ?? '相册' }}</h1>
        <p v-if="album" class="subtitle">
          <span class="tag" :class="album.visibility === 'public' ? 'tag-public' : 'tag-private'">
            {{ album.visibility === 'public' ? '公开' : '私有' }}
          </span>
          类别：{{ album.category.name }}
        </p>
      </div>
      <div v-if="isOwner()" class="actions">
        <RouterLink class="btn btn-ghost" :to="{ name: 'album-edit', params: { id: albumId } }">修改相册</RouterLink>
        <label class="btn" :class="{ disabled: pendingUpload }">
          {{ pendingUpload ? '上传中……' : '上传图片' }}
          <input
            type="file"
            accept=".jpg,.jpeg,.png,.gif"
            hidden
            :disabled="pendingUpload"
            @change="onFileChange"
          />
        </label>
      </div>
    </div>
    <p class="hint">仅支持 jpg/png/gif，且不超过 10MB</p>
    <p v-if="uploadMessage" class="alert alert-error">{{ uploadMessage }}</p>
    <p v-if="message" class="alert alert-error">{{ message }}</p>
    <div v-if="loading" class="empty">加载中……</div>
    <template v-else-if="album">
      <div v-if="photos.length === 0" class="empty">暂无照片</div>
      <div v-else class="grid">
        <RouterLink
          v-for="photo in photos"
          :key="photo.id"
          class="tile"
          :to="{ name: 'photo-detail', params: { id: photo.id } }"
        >
          <img :src="photo.thumbnail_url" :alt="`照片 ${photo.id}`" @error="onThumbError" />
          <div class="tile-body">
            <div class="tile-meta">上传者 {{ photo.uploader.username }}</div>
          </div>
        </RouterLink>
      </div>
    </template>
    <div class="actions">
      <RouterLink class="btn btn-ghost" :to="{ name: 'albums' }">返回相册列表</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.head-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

label.btn.disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
