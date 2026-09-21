<script setup lang="ts">
const { user, logout } = useAuth()
const { t, locale, locales, setLocale } = useI18n()

// пункты переключателя языка
const localeItems = computed(() =>
  (locales.value as { code: string; name: string }[]).map((l) => ({ label: l.name, value: l.code })),
)

// инициалы для аватара: имя+фамилия, иначе первая буква email
const initials = computed(() => {
  const u = user.value
  if (!u) return ""
  const fn = (u.first_name || "").trim()
  const ln = (u.last_name || "").trim()
  if (fn || ln) return ((fn[0] || "") + (ln[0] || "")).toUpperCase()
  return (u.email[0] || "?").toUpperCase()
})
// имя рядом с аватаром: полное имя или email
const displayName = computed(() => {
  const u = user.value
  if (!u) return ""
  const full = [u.first_name, u.last_name].filter(Boolean).join(" ").trim()
  return full || u.email
})

// меню аватара
const menuItems = computed(() => [[
  { label: t("landing.menu.control"), icon: "i-lucide-layout-dashboard", to: "/control" },
  { label: t("common.logout"), icon: "i-lucide-log-out", onSelect: onLogout },
]])

async function onLogout() {
  await logout()
  await navigateTo("/")
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-default">
    <header class="h-14 flex items-center gap-3 border-b border-default px-4 sm:px-6">
      <NuxtLink to="/" class="font-semibold hover:text-primary">{{ t("common.appName") }}</NuxtLink>
      <div class="flex-1" />
      <!-- переключатель темы (готовый компонент @nuxt/ui) -->
      <UColorModeSwitch />
      <!-- язык -->
      <USelect
        :model-value="locale"
        :items="localeItems"
        value-key="value"
        size="sm"
        class="w-28"
        @update:model-value="setLocale($event)"
      />
      <!-- гость: кнопка входа -->
      <UButton v-if="!user" icon="i-lucide-log-in" to="/login">{{ t("landing.login") }}</UButton>
      <!-- авторизован: кликабельный аватар с меню -->
      <UDropdownMenu v-else :items="menuItems">
        <UButton color="neutral" variant="ghost" class="gap-2">
          <UAvatar :text="initials" size="sm" />
          <span class="hidden sm:block text-sm truncate max-w-[30vw]">{{ displayName }}</span>
        </UButton>
      </UDropdownMenu>
    </header>

    <main class="flex-1 w-full max-w-6xl mx-auto p-4 sm:p-6">
      <slot />
    </main>
  </div>
</template>
