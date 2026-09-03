export default defineNuxtRouteMiddleware(async (to) => {
  const { user, fetchMe } = useAuth()
  if (to.path === "/login") return
  if (!user.value) {
    const me = await fetchMe()
    if (!me) return navigateTo("/login")
  }
})
