<script setup lang="ts">
const { t } = useI18n()
const { user } = useAuth()
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">{{ t("profile.title") }}</h1>
    <UCard>
      <dl class="space-y-2 text-sm">
        <div class="flex gap-2">
          <dt class="w-24 text-muted">{{ t("profile.email") }}</dt>
          <dd class="font-mono">{{ user?.email }}</dd>
        </div>
        <div class="flex gap-2">
          <dt class="w-24 text-muted">{{ t("profile.staff") }}</dt>
          <dd>{{ user?.is_staff ? t("common.yes") : t("common.no") }}</dd>
        </div>
      </dl>
    </UCard>
  </div>
</template>
