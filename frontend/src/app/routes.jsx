import MainLayout from "../components/layout/MainLayout";
import ProtectedRoute from "../components/layout/ProtectedRoute";

// Auth
import Login from "../pages/Auth/Login";

// Dashboard
import Dashboard from "../pages/Dashboard/Dashboard";

// Scanner
import ScannerPage from "../pages/Scanner/ScannerPage";
import ScanHistory from "../pages/Scanner/ScanHistory";

// (Optional: keep existing pages if you add later)

const router = [
  // 🔓 Public route
  {
    path: "/login",
    element: <Login />,
  },

  // 🔒 Root (default dashboard)
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <MainLayout>
          <Dashboard />
        </MainLayout>
      </ProtectedRoute>
    ),
  },

  // 🔒 Dashboard
  {
    path: "/dashboard",
    element: (
      <ProtectedRoute>
        <MainLayout>
          <Dashboard />
        </MainLayout>
      </ProtectedRoute>
    ),
  },

  // 🔒 Scanner main page (NEW 🔥)
  {
    path: "/scanner",
    element: (
      <ProtectedRoute>
        <MainLayout>
          <ScannerPage />
        </MainLayout>
      </ProtectedRoute>
    ),
  },

  // 🔒 Scan history page (NEW 🔥)
  {
    path: "/scanner/history",
    element: (
      <ProtectedRoute>
        <MainLayout>
          <ScanHistory />
        </MainLayout>
      </ProtectedRoute>
    ),
  },
];

export default router;
