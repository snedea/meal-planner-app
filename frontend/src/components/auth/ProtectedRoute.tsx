// Protected route wrapper

import React, { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Spinner } from '../common/Spinner';

export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, token, fetchCurrentUser, user } = useAuthStore();

  useEffect(() => {
    // If we have a token but no user, fetch the user
    if (token && !user) {
      fetchCurrentUser();
    }
  }, [token, user, fetchCurrentUser]);

  // If not authenticated, redirect to login
  if (!isAuthenticated || !token) {
    return <Navigate to="/login" replace />;
  }

  // If authenticated but still loading user data, show spinner
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  // Authenticated and user loaded, render protected content
  return <Outlet />;
};
