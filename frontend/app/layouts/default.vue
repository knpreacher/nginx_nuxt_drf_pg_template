<script setup lang="ts">
const { user, logout } = useAuth()
const route = useRoute()
const { t, locale, locales, setLocale } = useI18n()
const colorMode = useColorMode()
const drawerOpen = ref(false)

// пункты переключателя языка
const localeItems = computed(() =>
  (locales.value as { code: string; name: string }[]).map((l) => ({ label: l.name, value: l.code })),
)

// тумблер темы: тёмная <-> светлая
function toggleTheme() {
  colorMode.preference = colorMode.value === "dark" ? "light" : "dark"
}

// drawer закрываем при смене роута
watch(() => route.path, () => {
  drawerOpen.value = false
})

async function onLogout() {
  await logout()
  await navigateTo("/login")
}
</script>

<template>
  <div class="min-h-screen flex bg-default">
    <!-- десктопный сайдбар -->
    <aside class="hidden lg:flex lg:flex-col w-64 shrink-0 border-r border-default p-4 gap-4">
      <NuxtLink to="/" class="px-2 text-lg font-semibold hover:text-primary">{{ t("common.appName") }}</NuxtLink>
      <AppNav class="flex-1" />
      <div class="border-t border-default pt-3">
        <p class="px-2 text-sm text-muted truncate">{{ user?.email }}</p>
        <UButton
          class="mt-1 justify-start"
          icon="i-lucide-log-out"
          color="neutral"
          variant="ghost"
          block
          @click="onLogout"
        >
          {{ t("common.logout") }}
        </UButton>
      </div>
    </aside>

    <!-- правая колонка -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-14 flex items-center gap-3 border-b border-default px-4">
        <UButton
          class="lg:hidden"
          icon="i-lucide-menu"
          color="neutral"
          variant="ghost"
          :aria-label="t('common.menu')"
          @click="drawerOpen = true"
        />
        <NuxtLink to="/" class="font-semibold lg:hidden hover:text-primary">{{ t("common.appName") }}</NuxtLink>
        <div class="flex-1" />
        <!-- вариант 1: своя кнопка-тоггл (солнце/луна) -->
        <ClientOnly>
          <UButton
            :icon="colorMode.value === 'dark' ? 'i-lucide-moon' : 'i-lucide-sun'"
            color="neutral"
            variant="ghost"
            :aria-label="t('common.theme')"
            @click="toggleTheme"
          />
          <template #fallback>
            <UButton icon="i-lucide-sun" color="neutral" variant="ghost" disabled />
          </template>
        </ClientOnly>
        <!-- вариант 2: готовый компонент из @nuxt/ui v4 (иконки/состояние — внутри) -->
        <UColorModeSwitch />
        <USelect
          :model-value="locale"
          :items="localeItems"
          value-key="value"
          size="sm"
          class="w-28"
          @update:model-value="setLocale($event)"
        />
        <span class="hidden sm:block text-sm text-muted truncate max-w-[40vw]">{{ user?.email }}</span>
        <UButton
          icon="i-lucide-log-out"
          color="neutral"
          variant="ghost"
          :aria-label="t('common.logout')"
          @click="onLogout"
        />
      </header>

      <main class="flex-1 p-4 sm:p-6">
        <slot />
      </main>
    </div>

    <!-- мобильный drawer с той же навигацией -->
    <USlideover v-model:open="drawerOpen" side="left" :title="t('common.appName')">
      <template #body>
        <AppNav @navigate="drawerOpen = false" />
      </template>
    </USlideover>
  </div>
</template>
