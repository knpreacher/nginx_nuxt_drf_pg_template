// пропсы кнопки диалога: текст + любые пропсы UButton (color/variant/icon...),
// уходят в кнопку через v-bind, поэтому набор оставляем открытым

export interface ConfirmButton {
  label?: string
  color?: string
  variant?: string
  icon?: string
  [key: string]: unknown
}

export interface ConfirmOptions {
  title: string
  description?: string // подзаголовок модалки
  message?: string // абзац в теле
  confirm?: ConfirmButton
  cancel?: ConfirmButton
}

// резолвер текущего промиса; живет только на клиенте (confirm зовут по клику)
let resolver: ((value: boolean) => void) | null = null

// единый await-диалог подтверждения; разметку рисует <ConfirmDialog> в app.vue
export function useConfirm() {
  const state = useState<{ open: boolean; options: ConfirmOptions | null }>(
    "confirm-dialog",
    () => ({ open: false, options: null }),
  )

  // открыть диалог и дождаться выбора: true = подтвердил, false = отмена
  function confirm(options: ConfirmOptions): Promise<boolean> {
    state.value = { open: true, options }
    return new Promise((resolve) => {
      resolver = resolve
    })
  }

  // закрыть и отдать результат в ожидающий промис
  function _settle(result: boolean) {
    state.value.open = false
    resolver?.(result)
    resolver = null
  }

  return { confirm, state, _settle }
}
