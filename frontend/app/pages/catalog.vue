<script setup lang="ts">
const { $api } = useNuxtApp()
const toast = useToast()
const { t, locale } = useI18n()

// общий листинг (поиск, сортировка, пагинация, синхронизация с query) на приватном эндпоинте
const list = useCatalogList("/catalog/")
await list.ready // блокируем SSR до загрузки
const { search, order, page, items, total, pageSize, refresh } = list

// подписи сортировки берём из локали
const orderItems = computed(() =>
  ORDER_OPTIONS.map((o) => ({ label: t(`catalog.order.${o.key}`), value: o.value })),
)

function fmtDate(s: string) {
  return new Date(s).toLocaleDateString(locale.value)
}

// --- форма создания/редактирования ---
const formOpen = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: "", description: "", is_public: false })
const file = ref<File | null>(null) // новый выбранный файл
const filePreview = ref<string | null>(null) // object-url нового файла
const editingUrl = ref<string | null>(null) // уже сохраненная картинка (при редактировании)
const cleared = ref(false) // пользователь удалил существующую картинку
const saving = ref(false)

// что показываем: новый файл важнее, затем существующая картинка (если не удалена)
const shownImage = computed(() =>
  file.value ? filePreview.value : !cleared.value ? editingUrl.value : null,
)

// выбран файл -> строим превью
watch(file, (f) => {
  filePreview.value = f ? URL.createObjectURL(f) : null
})

// крестик: сперва снимаем новый файл, повторно — убираем существующую
function removeImage() {
  if (file.value) file.value = null
  else cleared.value = true
}

function openCreate() {
  editingId.value = null
  form.name = ""
  form.description = ""
  form.is_public = false
  file.value = null
  editingUrl.value = null
  cleared.value = false
  formOpen.value = true
}

function openEdit(item: CatalogItem) {
  editingId.value = item.id
  form.name = item.name
  form.description = item.description
  form.is_public = item.is_public
  file.value = null
  editingUrl.value = item.image_url
  cleared.value = false
  formOpen.value = true
}

async function submit() {
  if (!form.name.trim()) return
  saving.value = true
  try {
    const fd = new FormData()
    fd.append("name", form.name)
    fd.append("description", form.description)
    fd.append("is_public", form.is_public ? "true" : "false")
    if (file.value) fd.append("image", file.value)
    else if (cleared.value) fd.append("remove_image", "true")
    if (editingId.value) {
      await $api(`/catalog/${editingId.value}/`, { method: "PATCH", body: fd })
    } else {
      await $api("/catalog/", { method: "POST", body: fd })
    }
    formOpen.value = false
    toast.add({ title: t(editingId.value ? "catalog.toast.saved" : "catalog.toast.created"), color: "success" })
    await refresh()
  } catch {
    toast.add({ title: t("catalog.toast.saveError"), color: "error" })
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
    toast.add({ title: t("catalog.toast.deleted"), color: "success" })
    // если снесли последнюю карточку на странице — шаг назад
    if (items.value.length === 1 && page.value > 1) {
      page.value -= 1
    } else {
      await refresh()
    }
    deleteTarget.value = null
  } catch {
    toast.add({ title: t("catalog.toast.deleteError"), color: "error" })
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">{{ t("catalog.title") }}</h1>
      <UBadge color="neutral" variant="subtle">{{ total }}</UBadge>
      <div class="flex-1" />
      <UButton icon="i-lucide-plus" @click="openCreate">{{ t("catalog.add") }}</UButton>
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
            <!-- бейдж публичности -->
            <UBadge v-if="item.is_public" color="primary" variant="subtle" size="sm">
              {{ t("catalog.public") }}
            </UBadge>
          </div>
          <p class="text-sm text-muted line-clamp-2 flex-1">{{ item.description }}</p>
          <div class="flex items-center gap-2 pt-2">
            <span class="text-xs text-muted flex-1">{{ fmtDate(item.created_at) }}</span>
            <UButton
              icon="i-lucide-pencil"
              size="xs"
              color="neutral"
              variant="ghost"
              :aria-label="t('common.edit')"
              @click="openEdit(item)"
            />
            <UButton
              icon="i-lucide-trash-2"
              size="xs"
              color="error"
              variant="ghost"
              :aria-label="t('common.delete')"
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
      :title="editingId ? t('catalog.editTitle') : t('catalog.newTitle')"
      :description="editingId ? t('catalog.editDesc') : t('catalog.newDesc')"
    >
      <template #body>
        <form class="space-y-4" @submit.prevent="submit">
          <UFormField :label="t('catalog.fieldName')" required>
            <UInput v-model="form.name" class="w-full" />
          </UFormField>
          <UFormField :label="t('catalog.fieldDescription')">
            <UTextarea v-model="form.description" :rows="4" class="w-full" />
          </UFormField>
          <UFormField :label="t('catalog.imageLabel')">
            <!-- есть картинка: показываем ее с кнопкой удаления -->
            <div v-if="shownImage" class="relative inline-block">
              <img
                :src="shownImage"
                alt=""
                class="max-h-48 rounded border border-default object-contain"
              >
              <UButton
                icon="i-lucide-x"
                size="xs"
                color="neutral"
                class="absolute top-1 right-1"
                :aria-label="t('catalog.removeImage')"
                @click="removeImage"
              />
            </div>
            <!-- нет картинки: дропзона -->
            <UFileUpload
              v-else
              v-model="file"
              accept="image/*"
              class="w-full"
              :label="t('catalog.dropzoneLabel')"
              :description="t('catalog.dropzoneHint')"
            />
          </UFormField>
          <!-- публичность: виден ли элемент на лендинге -->
          <UFormField :label="t('catalog.public')">
            <USwitch v-model="form.is_public" />
          </UFormField>
        </form>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2 w-full">
          <UButton color="neutral" variant="ghost" @click="formOpen = false">{{ t("common.cancel") }}</UButton>
          <UButton :loading="saving" :disabled="!form.name.trim()" @click="submit">
            {{ t("common.save") }}
          </UButton>
        </div>
      </template>
    </UModal>

    <!-- подтверждение удаления -->
    <UModal
      :open="!!deleteTarget"
      :title="t('catalog.deleteTitle')"
      :description="t('catalog.deleteDesc')"
      @update:open="deleteTarget = null"
    >
      <template #body>
        <p class="text-sm">
          {{ t("catalog.deleteConfirm", { name: deleteTarget?.name }) }}
        </p>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2 w-full">
          <UButton color="neutral" variant="ghost" @click="deleteTarget = null">{{ t("common.cancel") }}</UButton>
          <UButton color="error" :loading="deleting" @click="doDelete">{{ t("common.delete") }}</UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>
