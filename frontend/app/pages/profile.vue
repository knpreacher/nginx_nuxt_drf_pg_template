<script setup lang="ts">
const { user } = useAuth()
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">Profile</h1>
    <UCard>
      <dl class="space-y-2 text-sm">
        <div class="flex gap-2">
          <dt class="w-24 text-muted">Email</dt>
          <dd class="font-mono">{{ user?.email }}</dd>
        </div>
        <div class="flex gap-2">
          <dt class="w-24 text-muted">Staff</dt>
          <dd>{{ user?.is_staff ? "да" : "нет" }}</dd>
        </div>
      </dl>
    </UCard>
  </div>
</template>
