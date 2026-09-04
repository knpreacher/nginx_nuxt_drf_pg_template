<script setup lang="ts">
const { $api } = useNuxtApp()
const toast = useToast()

const route = useRoute()
const router = useRouter()
const DEFAULT_ORDER = "-created_at"

// --- список: поиск, сортировка, пагинация. Начальное состояние берём из query,
// чтобы перезагрузка/ссылка возвращали на ту же страницу с тем же фильтром ---
const search = ref(typeof route.query.q === "string" ? route.query.q : "")
const debounced = ref(search.value)
const order = ref(
  ORDER_OPTIONS.some((o) => o.value === route.query.ordering)
    ? String(route.query.ordering)
    : DEFAULT_ORDER,
)
const page = ref(Number(route.query.page) > 1 ? Number(route.query.page) : 1)

// debounce поиска, любой сброс фильтра возвращает на первую страницу
let timer: ReturnType<typeof setTimeout>
watch(search, (v) => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    debounced.value = v
    page.value = 1
  }, 300)
})
watch(order, () => {
  page.value = 1
})

// состояние -> query (replace, чтобы не засорять историю); дефолты опускаем
watch([debounced, order, page], () => {
  const q: Record<string, string> = {}
  if (debounced.value) q.q = debounced.value
  if (order.value !== DEFAULT_ORDER) q.ordering = order.value
  if (page.value > 1) q.page = String(page.value)
  router.replace({ query: q })
})

const { data, refresh, status } = await useAsyncData(
  "catalog-list",
  () =>
    $api<Paginated<CatalogItem>>("/catalog/", {
      query: {
        search: debounced.value || undefined,
        ordering: order.value,
        page: page.value,
      },
    }),
  { watch: [debounced, order, page] },
)

const items = computed(() => data.value?.results ?? [])
const total = computed(() => data.value?.count ?? 0)

// размер страницы задаёт бэкенд (DRF), в ответе его нет —
// выводим из полной страницы: если есть next, её длина и есть page size
const pageSize = ref(PAGE_SIZE)
watch(
  data,
  (d) => {
    if (d?.next && d.results.length) pageSize.value = d.results.length
  },
  { immediate: true },
)

function fmtDate(s: string) {
  return new Date(s).toLocaleDateString("ru-RU")
}

// --- форма создания/редактирования ---
const formOpen = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: "", description: "" })
const file = ref<File | null>(null)
const preview = ref<string | null>(null)
const saving = ref(false)

function openCreate() {
  editingId.value = null
  form.name = ""
  form.description = ""
  file.value = null
  preview.value = null
  formOpen.value = true
}

function openEdit(item: CatalogItem) {
  editingId.value = item.id
  form.name = item.name
  form.description = item.description
  file.value = null
  preview.value = item.image_url
  formOpen.value = true
}

// выбран файл -> обновляем превью
watch(file, (f) => {
  if (f) preview.value = URL.createObjectURL(f)
})

async function submit() {
  if (!form.name.trim()) return
  saving.value = true
  try {
    const fd = new FormData()
    fd.append("name", form.name)
    fd.append("description", form.description)
    if (file.value) fd.append("image", file.value)
    if (editingId.value) {
      await $api(`/catalog/${editingId.value}/`, { method: "PATCH", body: fd })
    } else {
      await $api("/catalog/", { method: "POST", body: fd })
    }
    formOpen.value = false
    toast.add({ title: editingId.value ? "Сохранено" : "Создано", color: "success" })
    await refresh()
  } catch {
    toast.add({ title: "Не удалось сохранить", color: "error" })
  } finally {
    saving.value = false
  }
}

// --- удаление ---
const deleteTarget = ref<CatalogItem | null>(null)
const deleting = ref(false)

async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await $api(`/catalog/${deleteTarget.value.id}/`, { method: "DELETE" })
    toast.add({ title: "Удалено", color: "success" })
    // если снесли последнюю карточку на странице — шаг назад
    if (items.value.length === 1 && page.value > 1) {
      page.value -= 1
    } else {
      await refresh()
    }
    deleteTarget.value = null
  } catch {
    toast.add({ title: "Не удалось удалить", color: "error" })
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">Каталог</h1>
      <UBadge color="neutral" variant="subtle">{{ total }}</UBadge>
      <div class="flex-1" />
      <UButton icon="i-lucide-plus" @click="openCreate">Добавить</UButton>
    </div>

    <!-- панель: поиск + сортировка -->
    <div class="flex flex-col sm:flex-row gap-2">
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Поиск по названию и описанию"
        class="flex-1"
      />
      <USelect v-model="order" :items="ORDER_OPTIONS" value-key="value" class="w-full sm:w-56" />
    </div>

    <!-- пусто -->
    <div v-if="items.length === 0" class="py-16 text-center text-muted">
      <UIcon name="i-lucide-package-open" class="size-10 mx-auto mb-2" />
      <p>Ничего не найдено</p>
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
          <h3 class="font-medium truncate">{{ item.name }}</h3>
          <p class="text-sm text-muted line-clamp-2 flex-1">{{ item.description }}</p>
          <div class="flex items-center gap-2 pt-2">
            <span class="text-xs text-muted flex-1">{{ fmtDate(item.created_at) }}</span>
            <UButton
              icon="i-lucide-pencil"
              size="xs"
              color="neutral"
              variant="ghost"
              aria-label="Редактировать"
              @click="openEdit(item)"
            />
            <UButton
              icon="i-lucide-trash-2"
              size="xs"
              color="error"
              variant="ghost"
              aria-label="Удалить"
              @click="deleteTarget = item"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- пагинация -->
    <div v-if="total > pageSize" class="flex justify-center pt-2">
      <UPagination v-model:page="page" :total="total" :items-per-page="pageSize" />
    </div>

    <!-- форма создания/редактирования -->
    <UModal
      v-model:open="formOpen"
      :title="editingId ? 'Редактировать элемент' : 'Новый элемент'"
      :description="editingId ? 'Измените поля и сохраните' : 'Заполните поля нового элемента'"
    >
      <template #body>
        <form class="space-y-4" @submit.prevent="submit">
          <UFormField label="Название" required>
            <UInput v-model="form.name" class="w-full" />
          </UFormField>
          <UFormField label="Описание">
            <UTextarea v-model="form.description" :rows="4" class="w-full" />
          </UFormField>
          <UFormField label="Картинка">
            <UFileUpload
              v-model="file"
              accept="image/*"
              class="w-full"
              label="Перетащите картинку или нажмите"
              description="PNG, JPG"
            />
          </UFormField>
          <img
            v-if="preview"
            :src="preview"
            alt=""
            class="max-h-40 rounded border border-default object-contain"
          >
        </form>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2 w-full">
          <UButton color="neutral" variant="ghost" @click="formOpen = false">Отмена</UButton>
          <UButton :loading="saving" :disabled="!form.name.trim()" @click="submit">
            Сохранить
          </UButton>
        </div>
      </template>
    </UModal>

    <!-- подтверждение удаления -->
    <UModal
      :open="!!deleteTarget"
      title="Удалить элемент?"
      description="Действие необратимо"
      @update:open="deleteTarget = null"
    >
      <template #body>
        <p class="text-sm">
          «{{ deleteTarget?.name }}» будет удалён безвозвратно.
        </p>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2 w-full">
          <UButton color="neutral" variant="ghost" @click="deleteTarget = null">Отмена</UButton>
          <UButton color="error" :loading="deleting" @click="doDelete">Удалить</UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>
