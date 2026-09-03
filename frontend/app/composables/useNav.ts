export interface NavItem {
  label: string
  icon: string
  to: string
}

// пункты навигации
export function useNav(): NavItem[] {
  return [
    { label: "Home", icon: "i-lucide-home", to: "/" },
    { label: "Profile", icon: "i-lucide-user", to: "/profile" },
    { label: "Settings", icon: "i-lucide-settings", to: "/settings" },
  ]
}
