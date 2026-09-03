<script setup lang="ts">
const emit = defineEmits<{ navigate: [] }>()
const route = useRoute()

const items = computed(() =>
  useNav().map((i) => ({
    label: i.label,
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
