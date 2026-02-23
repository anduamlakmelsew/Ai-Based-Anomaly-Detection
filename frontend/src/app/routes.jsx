import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "../components/layout/ProtectedRoute";
import MainLayout from "../components/layout/MainLayout";

import Login from "../pages/Auth/Login";
import Dashboard from "../pages/Dashboard/Dashboard";
import BaselineOverview from "../pages/Baseline/BaselineOverview";
import Scanner from "../pages/Scanner/ScanForm";
import AnomalyDashboard from "../pages/Anomalies/AnomalyDashboard";
import AlertList from "../pages/Alerts/AlertList";
import ReportGenerator from "../pages/Reports/ReportGenerator";

function AppRoutes() {
  return (
    <Routes>
      {/* Public Route */}
      <Route path="/login" element={<Login />} />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/baseline"
        element={
          <ProtectedRoute>
            <MainLayout>
              <BaselineOverview />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/scanner"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Scanner />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/anomalies"
        element={
          <ProtectedRoute>
            <MainLayout>
              <AnomalyDashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <MainLayout>
              <AlertList />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <MainLayout>
              <ReportGenerator />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Default Redirect */}
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

export default AppRoutes;
