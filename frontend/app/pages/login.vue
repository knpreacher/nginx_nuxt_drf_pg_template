<script setup lang="ts">
definePageMeta({ layout: "auth" })

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
    error.value = "Invalid email or password"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UCard class="w-full max-w-sm">
    <template #header><h1 class="text-lg font-semibold">Sign in</h1></template>
    <form class="space-y-4" @submit.prevent="onSubmit">
      <UFormField label="Email"><UInput v-model="email" type="email" required /></UFormField>
      <UFormField label="Password"><UInput v-model="password" type="password" required /></UFormField>
      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      <UButton type="submit" :loading="loading" block>Sign in</UButton>
    </form>
  </UCard>
</template>
