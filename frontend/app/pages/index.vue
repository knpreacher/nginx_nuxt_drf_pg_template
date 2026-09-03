<script setup lang="ts">
const { $api } = useNuxtApp()
const { user } = useAuth()
const { data: health } = await useAsyncData("health", () => $api<{ status: string }>("/health/"))
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">Welcome, {{ user?.email }}</h1>
    <UCard>
      <p>Backend health: <span class="font-mono">{{ health?.status }}</span></p>
      <p class="text-sm text-muted">nginx → nuxt (SSR) → drf → postgres ✅</p>
    </UCard>
  </div>
</template>
