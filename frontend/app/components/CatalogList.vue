<script setup lang="ts">
const props = withDefaults(defineProps<{ endpoint: string; editable?: boolean }>(), {
  editable: false,
})
const emit = defineEmits<{
  create: []
  edit: [item: CatalogItem]
  delete: [item: CatalogItem]
}>()

const { t, locale } = useI18n()

const list = useCatalogList(props.endpoint)
await list.ready // блокируем SSR до загрузки — карточки уходят в разметку
const { search, order, page, items, total, pageSize } = list

// родителю отдаем перезагрузку списка после CRUD
defineExpose({ refresh: list.refresh, reloadAfterRemoval: list.reloadAfterRemoval })

// подписи сортировки берем из локали
const orderItems = computed(() =>
  ORDER_OPTIONS.map((o) => ({ label: t(`catalog.order.${o.key}`), value: o.value })),
)

function fmtDate(s: string) {
  return new Date(s).toLocaleDateString(locale.value)
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">{{ t("catalog.title") }}</h1>
      <UBadge color="neutral" variant="subtle">{{ total }}</UBadge>
      <template v-if="editable">
        <div class="flex-1" />
        <UButton icon="i-lucide-plus" @click="emit('create')">{{ t("catalog.add") }}</UButton>
      </template>
    </div>

    <!-- панель: поиск + сортировка -->
    <div class="flex flex-col sm:flex-row gap-2">
      <UInput
        v-model="search"
        icon="i-lucide-search"
        :placeholder="t('catalog.searchPlaceholder')"
        class="flex-1"
      />
      <USelect v-model="order" :items="orderItems" value-key="value" class="w-full sm:w-56" />
    </div>

    <!-- пусто -->
    <div v-if="items.length === 0" class="py-16 text-center text-muted">
      <UIcon name="i-lucide-package-open" class="size-10 mx-auto mb-2" />
      <p>{{ t("catalog.empty") }}</p>
    </div>

    <!-- сетка -->
    <div v-else class="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="flex flex-col border border-default rounded-lg overflow-hidden bg-default"
      >
        <div class="aspect-video bg-elevated flex items-center justify-center overflow-hidden">
          <img
            v-if="item.image_url"
            :src="item.image_url"
            :alt="item.name"
            class="w-full h-full object-cover"
          >
          <UIcon v-else name="i-lucide-image" class="size-10 text-muted" />
        </div>
        <div class="flex flex-col flex-1 p-3 gap-1">
          <div class="flex items-center gap-2">
            <h3 class="font-medium truncate flex-1">{{ item.name }}</h3>
            <!-- бейдж публичности (только в режиме управления) -->
            <UBadge v-if="editable && item.is_public" color="primary" variant="subtle" size="sm">
              {{ t("catalog.public") }}
            </UBadge>
          </div>
          <p class="text-sm text-muted line-clamp-2 flex-1">{{ item.description }}</p>
          <!-- действия: дата + правка/удаление -->
          <div v-if="editable" class="flex items-center gap-2 pt-2">
            <span class="text-xs text-muted flex-1">{{ fmtDate(item.created_at) }}</span>
            <UButton
              icon="i-lucide-pencil"
              size="xs"
              color="neutral"
              variant="ghost"
              :aria-label="t('common.edit')"
              @click="emit('edit', item)"
            />
            <UButton
              icon="i-lucide-trash-2"
              size="xs"
              color="error"
              variant="ghost"
              :aria-label="t('common.delete')"
              @click="emit('delete', item)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- пагинация -->
    <div v-if="total > pageSize" class="flex justify-center pt-2">
      <UPagination v-model:page="page" :total="total" :items-per-page="pageSize" />
    </div>
  </div>
</template>
