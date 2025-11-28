import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserRole } from '../types/user';
import { removeStorageItem } from '../utils/helpers';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, role: UserRole) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
}

const mockUsers: Record<string, { user: User; token: string }> = {
  'user1': {
    user: {
      id: '1',
      username: 'user1',
      email: 'user1@example.com',
      role: 'general',
      name: '일반 사용자',
      createdAt: new Date().toISOString(),
    },
    token: 'mock-access-token-1',
  },
  'city1': {
    user: {
      id: '2',
      username: 'city1',
      email: 'city1@busan.go.kr',
      role: 'city',
      name: '부산시 관리자',
      createdAt: new Date().toISOString(),
    },
    token: 'mock-access-token-2',
  },
  'admin1': {
    user: {
      id: '3',
      username: 'admin1',
      email: 'admin1@example.com',
      role: 'admin',
      name: '시스템 관리자',
      createdAt: new Date().toISOString(),
    },
    token: 'mock-access-token-3',
  },
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, _password: string, role: UserRole) => {
        set({ isLoading: true });
        await new Promise((resolve) => setTimeout(resolve, 300));
        
        const mockUser = mockUsers[username];
        
        if (!mockUser) {
          const newUser: User = {
            id: Date.now().toString(),
            username,
            email: `${username}@example.com`,
            role,
            name: role === 'general' ? '일반 사용자' : role === 'city' ? '부산시 관리자' : '시스템 관리자',
            createdAt: new Date().toISOString(),
          };
          localStorage.setItem('accessToken', `mock-token-${username}`);
          localStorage.setItem('refreshToken', `refresh-token-${username}`);
          set({
            user: newUser,
            isAuthenticated: true,
            isLoading: false,
          });
        } else if (mockUser.user.role === role) {
          localStorage.setItem('accessToken', mockUser.token);
          localStorage.setItem('refreshToken', `refresh-${mockUser.token}`);
          set({
            user: mockUser.user,
            isAuthenticated: true,
            isLoading: false,
          });
        } else {
          const updatedUser = { ...mockUser.user, role };
          localStorage.setItem('accessToken', mockUser.token);
          localStorage.setItem('refreshToken', `refresh-${mockUser.token}`);
          set({
            user: updatedUser,
            isAuthenticated: true,
            isLoading: false,
          });
        }
      },

      logout: async () => {
        removeStorageItem('accessToken');
        removeStorageItem('refreshToken');
        set({
          user: null,
          isAuthenticated: false,
        });
      },

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

