import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore.js'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import AILab from './pages/AILab.jsx'
import Analysis from './pages/Analysis.jsx'
import AdminDashboard from './pages/AdminDashboard.jsx'

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated } = useAuthStore()
    if (!isAuthenticated) return <Navigate to="/login" replace />
    return children
}

const AdminRoute = ({ children }) => {
    const { isAuthenticated, user } = useAuthStore()
    if (!isAuthenticated) return <Navigate to="/login" replace />
    if (user?.role !== 'admin') return <Navigate to="/dashboard" replace />
    return children
}

function App() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/lab" element={<ProtectedRoute><AILab /></ProtectedRoute>} />
            <Route path="/analysis/:id" element={<ProtectedRoute><Analysis /></ProtectedRoute>} />
            <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    )
}

export default App
