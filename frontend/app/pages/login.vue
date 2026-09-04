<script setup lang="ts">
definePageMeta({ layout: "auth" })

const { t } = useI18n()
const { login } = useAuth()
const email = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function onSubmit() {
  error.value = ""
  loading.value = true
  try {
    await login(email.value, password.value)
    await navigateTo("/")
  } catch {
    error.value = t("login.error")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UCard class="w-full max-w-sm">
    <template #header><h1 class="text-lg font-semibold">{{ t("login.title") }}</h1></template>
    <form class="space-y-4" @submit.prevent="onSubmit">
      <UFormField :label="t('login.email')"><UInput v-model="email" type="email" required /></UFormField>
      <UFormField :label="t('login.password')"><UInput v-model="password" type="password" required /></UFormField>
      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      <UButton type="submit" :loading="loading" block>{{ t("login.submit") }}</UButton>
    </form>
  </UCard>
</template>
