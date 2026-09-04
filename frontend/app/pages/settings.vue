<script setup lang="ts">
const { t } = useI18n()
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("settings.title") }}</h1>
    <UCard>
      <p class="text-muted">{{ t("settings.stub") }}</p>
    </UCard>
  </div>
</template>
