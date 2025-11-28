import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/common/ProtectedRoute';

import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';

import UserDashboardPage from '../pages/user/UserDashboardPage';
import UserTripDetailPage from '../pages/user/UserTripDetailPage';
import UserMyPage from '../pages/user/UserMyPage';

import CityDashboardSafeDriving from '../pages/city/CityDashboardSafeDriving';
import CityDashboardIllegalParking from '../pages/city/CityDashboardIllegalParking';
import CityDashboardMissingPerson from '../pages/city/CityDashboardMissingPerson';

import AdminDashboardPage from '../pages/admin/AdminDashboardPage';
import AdminUserManagementPage from '../pages/admin/AdminUserManagementPage';
import AdminLogMonitoringPage from '../pages/admin/AdminLogMonitoringPage';

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/user/dashboard"
        element={
          <ProtectedRoute allowedRoles={['general']}>
            <UserDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/user/trip-detail/:vehicleId"
        element={
          <ProtectedRoute allowedRoles={['general']}>
            <UserTripDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/user/mypage"
        element={
          <ProtectedRoute allowedRoles={['general']}>
            <UserMyPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/city/main"
        element={
          <ProtectedRoute allowedRoles={['city']}>
            <Navigate to="/city/safe-driving" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/city/safe-driving"
        element={
          <ProtectedRoute allowedRoles={['city']}>
            <CityDashboardSafeDriving />
          </ProtectedRoute>
        }
      />
      <Route
        path="/city/illegal-parking"
        element={
          <ProtectedRoute allowedRoles={['city']}>
            <CityDashboardIllegalParking />
          </ProtectedRoute>
        }
      />
      <Route
        path="/city/missing-person"
        element={
          <ProtectedRoute allowedRoles={['city']}>
            <CityDashboardMissingPerson />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/main"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminUserManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/logs"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLogMonitoringPage />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

