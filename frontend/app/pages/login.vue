<script setup lang="ts">
definePageMeta({ layout: "auth", public: true })

const { t } = useI18n()
const { login, user } = useAuth()
const route = useRoute()

// куда уходим после входа: из query (только внутренний путь), иначе панель управления
const redirect = computed(() => {
  const r = route.query.redirect
  return typeof r === "string" && r.startsWith("/") ? r : "/control"
})

// уже авторизован — незачем показывать форму
if (user.value) await navigateTo(redirect.value)

const email = ref("")
const password = ref("")
const error = ref("")
const loading = ref(false)

async function onSubmit() {
  error.value = ""
  loading.value = true
  try {
    await login(email.value, password.value)
    await navigateTo(redirect.value)
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
