export function useCatalogList(endpoint: string) {
  const { $api } = useNuxtApp()
  const route = useRoute()
  const router = useRouter()
  const DEFAULT_ORDER = "-created_at"

  // начальное состояние из query — чтобы перезагрузка/ссылка возвращали ту же страницу с тем же фильтром
  const search = ref(typeof route.query.q === "string" ? route.query.q : "")
  const debounced = ref(search.value)
  const order = ref(
    ORDER_OPTIONS.some((o) => o.value === route.query.ordering)
      ? String(route.query.ordering)
      : DEFAULT_ORDER,
  )
  const page = ref(Number(route.query.page) > 1 ? Number(route.query.page) : 1)

  // debounce поиска; любой сброс фильтра возвращает на первую страницу
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

  // состояние -> query (replace, чтобы не засорять историю)
  watch([debounced, order, page], () => {
    const q: Record<string, string> = {}
    if (debounced.value) q.q = debounced.value
    if (order.value !== DEFAULT_ORDER) q.ordering = order.value
    if (page.value > 1) q.page = String(page.value)
    router.replace({ query: q })
  })

  const ready = useAsyncData(
    `catalog-list:${endpoint}`,
    () =>
      $api<Paginated<CatalogItem>>(endpoint, {
        query: {
          search: debounced.value || undefined,
          ordering: order.value,
          page: page.value,
        },
      }),
    { watch: [debounced, order, page] },
  )
  const { data, refresh, status } = ready

  const items = computed(() => data.value?.results ?? [])
  const total = computed(() => data.value?.count ?? 0)

  // размер страницы задает бэкенд (DRF), в ответе его нет —
  // выводим из полной страницы: если есть next, ее длина и есть page size
  const pageSize = ref(PAGE_SIZE)
  watch(
    data,
    (d) => {
      if (d?.next && d.results.length) pageSize.value = d.results.length
    },
    { immediate: true },
  )

  return { search, order, page, debounced, items, total, pageSize, data, refresh, status, ready }
}
