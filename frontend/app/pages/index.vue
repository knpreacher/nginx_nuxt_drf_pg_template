<script setup lang="ts">
const { $api } = useNuxtApp()
const { t } = useI18n()
const { user } = useAuth()
const { data: health } = await useAsyncData("health", () => $api<{ status: string }>("/health/"))
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("index.welcome", { email: user?.email }) }}</h1>
    <UCard>
      <p>{{ t("index.health") }} <span class="font-mono">{{ health?.status }}</span></p>
      <p class="text-sm text-muted">{{ t("index.chain") }}</p>
    </UCard>
  </div>
</template>
