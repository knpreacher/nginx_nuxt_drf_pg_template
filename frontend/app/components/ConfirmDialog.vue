<script setup lang="ts">
// единственный экземпляр диалога подтверждения (в app.vue), управляется через useConfirm
const { state, _settle } = useConfirm()
const { t } = useI18n()

// label вынимаем из пропсов кнопок — на UButton он не нужен
const confirmProps = computed(() => {
  const { label, ...rest } = state.value.options?.confirm ?? {}
  return rest
})
const cancelProps = computed(() => {
  const { label, ...rest } = state.value.options?.cancel ?? {}
  return rest
})
</script>

<template>
  <UModal
    :open="state.open"
    :title="state.options?.title"
    :description="state.options?.description"
    @update:open="(v) => { if (!v) _settle(false) }"
  >
    <template v-if="state.options?.message" #body>
      <p class="text-sm">{{ state.options.message }}</p>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2 w-full">
        <UButton color="neutral" variant="ghost" v-bind="cancelProps" @click="_settle(false)">
          {{ state.options?.cancel?.label ?? t("common.cancel") }}
        </UButton>
        <UButton v-bind="confirmProps" @click="_settle(true)">
          {{ state.options?.confirm?.label ?? t("common.confirm") }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>
