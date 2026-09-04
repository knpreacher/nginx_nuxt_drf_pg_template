export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const baseURL = import.meta.server
    ? `${config.apiInternal}/api`
    : config.public.apiBase

  // на SSR держим куку текущего запроса; после refresh подменяем на свежую,
  // чтобы встроенный retry ушел уже с новым access (плагин на сервере живет один запрос)
  const event = import.meta.server ? useRequestEvent() : null
  let serverCookie = import.meta.server ? useRequestHeaders(["cookie"]).cookie ?? "" : ""

  const api = $fetch.create({
    baseURL,
    credentials: "include",
    // повтор запроса и возврат результата делает сам ofetch; мы лишь освежаем токен
    retry: 1,
    retryStatusCodes: [401],
    onRequest({ options }) {
      // на клиенте куки шлет браузер; на сервере прокидываем руками
      if (import.meta.server && serverCookie) {
        options.headers = new Headers(options.headers)
        options.headers.set("cookie", serverCookie)
      }
    },
    async onResponseError({ request, options, response }) {
      if (response.status !== 401) return
      const url = typeof request === "string" ? request : request.url
      // на login/refresh/logout рефрешить нечего; делаем refresh один раз на запрос
      if (/\/auth\/(login|refresh|logout)\//.test(url)) return
      const opts = options as { _refreshed?: boolean }
      if (opts._refreshed) return
      opts._refreshed = true
      try {
        if (import.meta.server) {
          await refreshOnServer()
        } else {
          await $fetch("/auth/refresh/", { baseURL, method: "POST", credentials: "include" })
        }
      } catch {
        /* refresh не удался — retry получит повторный 401 и ошибка уйдет вызывающему */
      }
    },
  })

  // форвардим refresh-куку, свежий Set-Cookie берем в retry и отдаем браузеру
  async function refreshOnServer() {
    const res = await $fetch.raw("/auth/refresh/", {
      baseURL,
      method: "POST",
      headers: serverCookie ? { cookie: serverCookie } : undefined,
    })
    const setCookies =
      res.headers.getSetCookie?.() ??
      (res.headers.get("set-cookie") ? [res.headers.get("set-cookie") as string] : [])
    if (!setCookies.length) return
    // подменяем куку для retry
    for (const sc of setCookies) serverCookie = mergeCookie(serverCookie, sc)
    // отдаем свежие куки браузеру
    if (event) {
      try {
        const { appendResponseHeader } = await import("h3")
        for (const sc of setCookies) appendResponseHeader(event, "set-cookie", sc)
      } catch {
        /* проброс в браузер не удался — на текущий рендер не влияет */
      }
    }
  }

  return { provide: { api } }
})

// подменяем/добавляем cookie из строки Set-Cookie в заголовок Cookie
function mergeCookie(cookie: string, setCookie: string): string {
  const pair = setCookie.split(";")[0]?.trim() ?? ""
  const name = pair.split("=")[0]?.trim()
  if (!name) return cookie
  const rest = (cookie ? cookie.split("; ") : []).filter(
    (p) => p.split("=")[0]?.trim() !== name,
  )
  rest.push(pair)
  return rest.join("; ")
}
