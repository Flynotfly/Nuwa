import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getSession, login as apiLogin, logout as apiLogout, refreshToken as apiRefreshToken, register as apiRegister } from '../api/api';
import { SessionData, SignInData, SignUpData } from './types';

interface AuthContextType {
  user: SessionData | null;
  loading: boolean;
  login: (data: SignInData) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: SignUpData) => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const session = await getSession();
        setUser(session);
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (data: SignInData) => {
    apiLogin(data)
    .then(() => getSession().then((session) => setUser(session))); 
  };

  const logout = async () => {
    apiLogout().then(() => setUser(null));
  };

  const register = async (data: SignUpData) => {
    await apiRegister(data);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated: user?.isAuthenticated || false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};