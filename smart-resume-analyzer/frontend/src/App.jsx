import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Sidebar from './components/Layout/Sidebar';
import Topbar from './components/Layout/Topbar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AILab from './pages/AILab';
import Analysis from './pages/Analysis';
import AdminDashboard from './pages/AdminDashboard';

function ProtectedRoute({ children }) {
    const { token } = useAuthStore();
    if (!token) return <Navigate to="/login" replace />;
    return children;
}

function AppLayout({ children }) {
    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Topbar />
                <main className="flex-1 overflow-y-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default function App() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route
                path="/"
                element={
                    <ProtectedRoute>
                        <AppLayout><Dashboard /></AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/ai-lab"
                element={
                    <ProtectedRoute>
                        <AppLayout><AILab /></AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/analysis/:id"
                element={
                    <ProtectedRoute>
                        <AppLayout><Analysis /></AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin"
                element={
                    <ProtectedRoute>
                        <AppLayout><AdminDashboard /></AppLayout>
                    </ProtectedRoute>
                }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
