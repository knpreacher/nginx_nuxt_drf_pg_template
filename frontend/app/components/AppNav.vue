<script setup lang="ts">
const emit = defineEmits<{ navigate: [] }>()
const route = useRoute()
const { t } = useI18n()

const items = computed(() =>
  useNav().map((i) => ({
    label: t(i.labelKey),
    icon: i.icon,
    to: i.to,
    active: route.path === i.to,
    onSelect: () => emit("navigate"),
  })),
)
</script>

<template>
  <UNavigationMenu orientation="vertical" :items="items" class="w-full" />
</template>
