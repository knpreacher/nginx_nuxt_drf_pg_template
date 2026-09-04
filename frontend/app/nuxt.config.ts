export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  srcDir: ".",
  modules: ["@nuxt/ui", "@nuxtjs/i18n"],
  css: ["~/assets/css/main.css"],
  icon: {
    localApiEndpoint: "/_nuxt_icon",
    clientBundle: { scan: true },
  },
  i18n: {
    // язык не в URL: храним в cookie, переключаем из UI
    strategy: "no_prefix",
    defaultLocale: "ru",
    locales: [
      { code: "ru", name: "Русский", file: "ru.json" },
      { code: "en", name: "English", file: "en.json" },
    ],
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: "i18n_locale",
      fallbackLocale: "ru",
      redirectOn: "root",
    },
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
