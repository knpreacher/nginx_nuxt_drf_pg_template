<script setup lang="ts">
// публичный лендинг: витрина опубликованного каталога, доступен без авторизации
definePageMeta({ layout: "landing", public: true })
const { t } = useI18n()

// тот же листинг, что и на /catalog, только публичный эндпоинт и read-only
const list = useCatalogList("/public/catalog/")
await list.ready // блокируем SSR до загрузки — карточки уходят в разметку
const { search, order, page, items, total, pageSize } = list

// подписи сортировки берем из локали
const orderItems = computed(() =>
  ORDER_OPTIONS.map((o) => ({ label: t(`catalog.order.${o.key}`), value: o.value })),
)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">{{ t("catalog.title") }}</h1>
      <UBadge color="neutral" variant="subtle">{{ total }}</UBadge>
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

    <!-- сетка (read-only, без действий) -->
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
          <h3 class="font-medium truncate">{{ item.name }}</h3>
          <p class="text-sm text-muted line-clamp-2 flex-1">{{ item.description }}</p>
        </div>
      </div>
    </div>

    <!-- пагинация -->
    <div v-if="total > pageSize" class="flex justify-center pt-2">
      <UPagination v-model:page="page" :total="total" :items-per-page="pageSize" />
    </div>
  </div>
</template>
