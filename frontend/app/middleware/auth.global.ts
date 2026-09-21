export default defineNuxtRouteMiddleware(async (to) => {
  const { user, fetchMe } = useAuth()
  // узнаем, кто в системе — нужно и на публичных страницах (аватар vs кнопка входа)
  if (!user.value) await fetchMe()
  // публичные страницы пускаем всегда
  if (to.meta.public) return
  // приватные — только авторизованным, иначе на логин с возвратом на исходный путь
  if (!user.value) return navigateTo(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
})
