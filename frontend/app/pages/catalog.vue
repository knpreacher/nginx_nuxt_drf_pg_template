<script setup lang="ts">
const { $api } = useNuxtApp()
const toast = useToast()
const { t } = useI18n()
const { confirm } = useConfirm()

// список с CRUD; сам листинг живет в компоненте, отсюда только перезагружаем
const listRef = useTemplateRef("listRef")

// форма создания/редактирования: null = создание, объект = правка
const formOpen = ref(false)
const editingItem = ref<CatalogItem | null>(null)

function openCreate() {
  editingItem.value = null
  formOpen.value = true
}

function openEdit(item: CatalogItem) {
  editingItem.value = item
  formOpen.value = true
}

// удаление через общий диалог подтверждения
async function onDelete(item: CatalogItem) {
  const ok = await confirm({
    title: t("catalog.deleteTitle"),
    description: t("catalog.deleteDesc"),
    message: t("catalog.deleteConfirm", { name: item.name }),
    confirm: { label: t("common.delete"), color: "error" },
  })
  if (!ok) return
  try {
    await $api(`/catalog/${item.id}/`, { method: "DELETE" })
    toast.add({ title: t("catalog.toast.deleted"), color: "success" })
    listRef.value?.reloadAfterRemoval()
  } catch {
    toast.add({ title: t("catalog.toast.deleteError"), color: "error" })
  }
}
</script>

<template>
  <div class="space-y-4">
    <CatalogList
      ref="listRef"
      endpoint="/catalog/"
      editable
      @create="openCreate"
      @edit="openEdit"
      @delete="onDelete"
    />

    <!-- форма создания/редактирования -->
    <CatalogItemForm v-model:open="formOpen" :item="editingItem" @saved="listRef?.refresh()" />
  </div>
</template>
