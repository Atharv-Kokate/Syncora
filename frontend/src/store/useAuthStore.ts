import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  username?: string; // Optional for backward compatibility with our frontend mocks
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      setAuth: (token, user) => 
        set({ 
          token, 
          user, 
          isAuthenticated: true 
        }),

      logout: () => 
        set({ 
          token: null, 
          user: null, 
          isAuthenticated: false 
        }),
    }),
    {
      name: "auth-storage", // The key used in localStorage
    }
  )
);
