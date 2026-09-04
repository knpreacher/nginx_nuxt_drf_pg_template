interface AuthUser {
  id: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
}

export function useAuth() {
  const user = useState<AuthUser | null>("auth_user", () => null)
  const { $api } = useNuxtApp()

  async function fetchMe() {
    try {
      user.value = await $api<AuthUser>("/auth/me/")
    } catch {
      user.value = null
    }
    return user.value
  }

  async function login(email: string, password: string) {
    // retry:0 — неверный пароль не должен повторять POST (глобальный retryStatusCodes)
    user.value = await $api<AuthUser>("/auth/login/", {
      method: "POST",
      body: { email, password },
      retry: 0,
    })
  }

  async function logout() {
    await $api("/auth/logout/", { method: "POST" })
    user.value = null
  }

  return { user, fetchMe, login, logout }
}
