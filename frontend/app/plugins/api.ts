export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const baseURL = import.meta.server
    ? `${config.apiInternal}/api`
    : config.public.apiBase

  const api = $fetch.create({
    baseURL,
    credentials: "include",
    onRequest({ options }) {
      if (import.meta.server) {
        // прокидываем куки браузера в DRF при SSR-запросе
        const cookie = useRequestHeaders(["cookie"]).cookie
        if (cookie) {
          options.headers = new Headers(options.headers)
          options.headers.set("cookie", cookie)
        }
      }
    },
    async onResponseError({ request, options, response }) {
      if (response.status === 401 && !(options as any)._retried) {
        try {
          await $fetch("/auth/refresh/", { baseURL, method: "POST", credentials: "include" })
          ;(options as any)._retried = true
          return api(request as string, options as any)
        } catch {
          /* Пробрасываем ошибку. Вызывающий код обработает редирект */
        }
      }
    },
  })

  return { provide: { api } }
})
