export interface NavItem {
  labelKey: string
  icon: string
  to: string
}

// пункты навигации; перевод labelKey делает вызывающий компонент (t на верхнем уровне setup)
export function useNav(): NavItem[] {
  return [
    { labelKey: "nav.control", icon: "i-lucide-layout-dashboard", to: "/control" },
    { labelKey: "nav.catalog", icon: "i-lucide-boxes", to: "/catalog" },
    { labelKey: "nav.profile", icon: "i-lucide-user", to: "/profile" },
    { labelKey: "nav.settings", icon: "i-lucide-settings", to: "/settings" },
  ]
}
