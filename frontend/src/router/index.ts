import { createRouter, createWebHistory } from 'vue-router'

import { useSession } from '@/stores/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: { name: 'albums' } },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { public: true },
    },
    {
      path: '/albums',
      name: 'albums',
      component: () => import('@/views/AlbumsView.vue'),
    },
    {
      path: '/albums/mine',
      name: 'my-albums',
      component: () => import('@/views/MyAlbumsView.vue'),
    },
    {
      path: '/albums/new',
      name: 'album-new',
      component: () => import('@/views/AlbumCreateView.vue'),
    },
    {
      path: '/albums/:id(\\d+)',
      name: 'album-detail',
      component: () => import('@/views/AlbumDetailView.vue'),
    },
    {
      path: '/albums/:id(\\d+)/edit',
      name: 'album-edit',
      component: () => import('@/views/AlbumEditView.vue'),
    },
    {
      path: '/photos/:id(\\d+)',
      name: 'photo-detail',
      component: () => import('@/views/PhotoDetailView.vue'),
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'albums' } },
  ],
})

router.beforeEach(async (to) => {
  const { state, load } = useSession()
  if (to.meta.public) {
    return true
  }
  await load()
  if (!state.user) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
