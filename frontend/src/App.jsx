import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";

import Navbar from "./components/layout/Navbar";
import Sidebar from "./components/layout/Sidebar";

// Auth Pages
import Login from "./pages/Auth/Login";
import Register from "./pages/Auth/Register";
import ForgotPassword from "./pages/Auth/ForgotPassword";

// Dashboard
import Dashboard from "./pages/Dashboard/Dashboard";

// Scanner
import ScannerPage from "./pages/Scanner/ScannerPage";
import ScanForm from "./pages/Scanner/ScanForm";
import ScanHistory from "./pages/Scanner/ScanHistory";
import ScanResult from "./pages/Scanner/ScanResult";

// Alerts
import AlertList from "./pages/Alerts/AlertList";
import IncidentDetails from "./pages/Alerts/IncidentDetails";

// Anomalies
import AnomalyDashboard from "./pages/Anomalies/AnomalyDashboard";
import ModelPerformance from "./pages/Anomalies/ModelPerformance";
import TrafficGraph from "./pages/Anomalies/TrafficGraph";

// Baseline
import BaselineOverview from "./pages/Baseline/BaselineOverview";
import BaselineVersioning from "./pages/Baseline/BaselineVersioning";
import ComplianceStandards from "./pages/Baseline/ComplianceStandards";

// Reports
import ReportGenerator from "./pages/Reports/ReportGenerator";
import ReportHistory from "./pages/Reports/ReportHistory";

// Settings
import AdminSettings from "./pages/Settings/AdminSettings";
import NotificationSettings from "./pages/Settings/NotificationSettings";
import SecuritySettings from "./pages/Settings/SecuritySettings";
import UserSettings from "./pages/Settings/UserSettings";

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
};

function AppContent() {
  const { user } = useAuth();

  if (!user) {
    // 🔐 NOT LOGGED IN
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    );
  }

  // 🔓 LOGGED IN
  return (
    <div className="app-layout">
      <Navbar />
      <div style={{ display: "flex" }}>
        <Sidebar />
        <div style={{ flex: 1, padding: "20px" }}>
          <Routes>
            {/* Dashboard */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* Scanner */}
            <Route
              path="/scanner"
              element={
                <ProtectedRoute>
                  <ScannerPage />
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
                  <AlertList />
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
                  <AnomalyDashboard />
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

            {/* Baseline */}
            <Route
              path="/baseline/overview"
              element={
                <ProtectedRoute>
                  <BaselineOverview />
                </ProtectedRoute>
              }
            />
            <Route
              path="/baseline/versioning"
              element={
                <ProtectedRoute>
                  <BaselineVersioning />
                </ProtectedRoute>
              }
            />
            <Route
              path="/baseline/compliance"
              element={
                <ProtectedRoute>
                  <ComplianceStandards />
                </ProtectedRoute>
              }
            />

            {/* Reports */}
            <Route
              path="/reports/generator"
              element={
                <ProtectedRoute>
                  <ReportGenerator />
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

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router>
          <AppContent />
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}
