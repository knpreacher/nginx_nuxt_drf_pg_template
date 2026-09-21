<script setup lang="ts">
// публичный лендинг: витрина опубликованного каталога, доступен без авторизации
definePageMeta({ layout: "landing", public: true })
</script>

<template>
  <CatalogList endpoint="/public/catalog/" />
</template>
