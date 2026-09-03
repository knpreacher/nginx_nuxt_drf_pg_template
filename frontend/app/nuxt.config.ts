export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  srcDir: ".",
  modules: ["@nuxt/ui"],
  css: ["~/assets/css/main.css"],
  icon: {
    localApiEndpoint: "/_nuxt_icon",
    clientBundle: { scan: true },
  },
  runtimeConfig: {
    // только сервер: Nuxt SSR -> backend по docker-сети
    apiInternal: process.env.NUXT_API_INTERNAL || "http://backend:8000",
    public: {
      // браузер -> nginx (тот же origin)
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "/api",
    },
  },
})
