import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthProvider";

// Components
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Login from "./pages/Auth/Login";
import EnhancedLogin from "./pages/Auth/EnhancedLogin";
import Register from "./pages/Auth/Register";
import ForgotPassword from "./pages/Auth/ForgotPassword";
import Dashboard from "./pages/Dashboard/Dashboard";
import EnhancedDashboard from "./pages/Dashboard/EnhancedDashboard";
import ScannerPage from "./pages/Scanner/ScannerPage";
import EnhancedScannerPage from "./pages/Scanner/EnhancedScannerPage";
import ScanForm from "./pages/Scanner/ScanForm";
import ScanHistory from "./pages/Scanner/ScanHistory";
import ScanResult from "./pages/Scanner/ScanResult";
import EnhancedScanResult from "./pages/Scanner/EnhancedScanResult";

// Alerts
import AlertList from "./pages/Alerts/AlertList";
import EnhancedAlertList from "./pages/Alerts/EnhancedAlertList";
import IncidentDetails from "./pages/Alerts/IncidentDetails";

// Anomalies
import AnomalyDashboard from "./pages/Anomalies/AnomalyDashboard";
import EnhancedAnomalyDashboard from "./pages/Anomalies/EnhancedAnomalyDashboard";
import ModelPerformance from "./pages/Anomalies/ModelPerformance";
import TrafficGraph from "./pages/Anomalies/TrafficGraph";

// Reports
import ReportGenerator from "./pages/Reports/ReportGenerator";
import EnhancedReportGenerator from "./pages/Reports/EnhancedReportGenerator";
import ReportHistory from "./pages/Reports/ReportHistory";

// Settings
import AdminSettings from "./pages/Settings/AdminSettings";
import NotificationSettings from "./pages/Settings/NotificationSettings";
import SecuritySettings from "./pages/Settings/SecuritySettings";
import UserSettings from "./pages/Settings/UserSettings";

const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#0f172a',
        color: '#fff'
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<EnhancedLogin />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <EnhancedDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scanner"
          element={
            <ProtectedRoute>
              <EnhancedScannerPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scanner/form"
          element={
            <ProtectedRoute>
              <ScanForm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scanner/history"
          element={
            <ProtectedRoute>
              <ScanHistory />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scanner/result/:id"
          element={
            <ProtectedRoute>
              <ScanResult />
            </ProtectedRoute>
          }
        />

        {/* Alerts */}
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <EnhancedAlertList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts/:id"
          element={
            <ProtectedRoute>
              <IncidentDetails />
            </ProtectedRoute>
          }
        />

        {/* Anomalies */}
        <Route
          path="/anomalies"
          element={
            <ProtectedRoute>
              <EnhancedAnomalyDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/anomalies/model-performance"
          element={
            <ProtectedRoute>
              <ModelPerformance />
            </ProtectedRoute>
          }
        />
        <Route
          path="/anomalies/traffic-graph"
          element={
            <ProtectedRoute>
              <TrafficGraph />
            </ProtectedRoute>
          }
        />

        {/* Reports */}
        <Route
          path="/reports/generator"
          element={
            <ProtectedRoute>
              <EnhancedReportGenerator />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports/history"
          element={
            <ProtectedRoute>
              <ReportHistory />
            </ProtectedRoute>
          }
        />

        {/* Settings */}
        <Route
          path="/settings/admin"
          element={
            <ProtectedRoute>
              <AdminSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/notifications"
          element={
            <ProtectedRoute>
              <NotificationSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/security"
          element={
            <ProtectedRoute>
              <SecuritySettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/user"
          element={
            <ProtectedRoute>
              <UserSettings />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
