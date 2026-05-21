import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, isPremium }) => {
  if (!isPremium) {
    return <Navigate to="/pricing" replace />;
  }

  return children;
};

export default ProtectedRoute;
