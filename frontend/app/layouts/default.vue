<script setup lang="ts">
const { user, logout } = useAuth()
const route = useRoute()
const drawerOpen = ref(false)

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
      <div class="px-2 text-lg font-semibold">App</div>
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
          Выйти
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
          aria-label="Меню"
          @click="drawerOpen = true"
        />
        <div class="font-semibold lg:hidden">App</div>
        <div class="flex-1" />
        <span class="hidden sm:block text-sm text-muted truncate max-w-[50vw]">{{ user?.email }}</span>
        <UButton
          icon="i-lucide-log-out"
          color="neutral"
          variant="ghost"
          aria-label="Выйти"
          @click="onLogout"
        />
      </header>

      <main class="flex-1 p-4 sm:p-6">
        <slot />
      </main>
    </div>

    <!-- мобильный drawer с той же навигацией -->
    <USlideover v-model:open="drawerOpen" side="left" title="App">
      <template #body>
        <AppNav @navigate="drawerOpen = false" />
      </template>
    </USlideover>
  </div>
</template>
