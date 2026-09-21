<script setup lang="ts">
// форма создания/редактирования элемента каталога; режим задает prop item
const props = defineProps<{ open: boolean; item: CatalogItem | null }>()
const emit = defineEmits<{ "update:open": [boolean]; saved: [] }>()

const { $api } = useNuxtApp()
const toast = useToast()
const { t } = useI18n()

const ENDPOINT = "/catalog/"

// редактируем существующий элемент или создаем новый
const isEdit = computed(() => !!props.item)

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

// открытие модалки -> заполняем из item либо чистим под создание
watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    const it = props.item
    form.name = it?.name ?? ""
    form.description = it?.description ?? ""
    form.is_public = it?.is_public ?? false
    file.value = null
    editingUrl.value = it?.image_url ?? null
    cleared.value = false
  },
)

// крестик: сперва снимаем новый файл, повторно — убираем существующую
function removeImage() {
  if (file.value) file.value = null
  else cleared.value = true
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
    if (props.item) {
      await $api(`${ENDPOINT}${props.item.id}/`, { method: "PATCH", body: fd })
    } else {
      await $api(ENDPOINT, { method: "POST", body: fd })
    }
    toast.add({ title: t(isEdit.value ? "catalog.toast.saved" : "catalog.toast.created"), color: "success" })
    emit("saved")
    emit("update:open", false)
  } catch {
    toast.add({ title: t("catalog.toast.saveError"), color: "error" })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <UModal
    :open="open"
    :title="isEdit ? t('catalog.editTitle') : t('catalog.newTitle')"
    :description="isEdit ? t('catalog.editDesc') : t('catalog.newDesc')"
    @update:open="emit('update:open', $event)"
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
        <UButton color="neutral" variant="ghost" @click="emit('update:open', false)">{{ t("common.cancel") }}</UButton>
        <UButton :loading="saving" :disabled="!form.name.trim()" @click="submit">
          {{ t("common.save") }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>
