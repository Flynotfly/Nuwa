import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { ReactNode } from 'react';

export const AnonymousRoute: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return <>{children}</>;
};