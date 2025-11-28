export type UserRole = 'general' | 'city' | 'admin';

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  name?: string;
  phone?: string;
  createdAt: string;
}

