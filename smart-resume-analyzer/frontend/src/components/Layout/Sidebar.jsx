import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
    LayoutDashboard,
    FlaskConical,
    Shield,
    LogOut,
    FileText,
    Sparkles,
} from 'lucide-react';

const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/ai-lab', icon: FlaskConical, label: 'AI Lab' },
    { to: '/admin', icon: Shield, label: 'Admin', adminOnly: true },
];

export default function Sidebar() {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside className="w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-dark-700">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
                        <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold gradient-text">SRA</h1>
                        <p className="text-xs text-dark-400">Resume Analyzer</p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems
                    .filter((item) => !item.adminOnly || user?.is_admin)
                    .map(({ to, icon: Icon, label }) => (
                        <NavLink
                            key={to}
                            to={to}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                                    ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30'
                                    : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'
                                }`
                            }
                        >
                            <Icon className="w-5 h-5" />
                            {label}
                        </NavLink>
                    ))}
            </nav>

            {/* AI Badge */}
            <div className="p-4 mx-4 mb-4 glass-card">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-primary-400" />
                    <span className="text-xs font-semibold text-primary-400">AI Powered</span>
                </div>
                <p className="text-xs text-dark-400">
                    Multi-agent pipeline for deep resume analysis
                </p>
            </div>

            {/* User & Logout */}
            <div className="p-4 border-t border-dark-700">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <div>
                            <p className="text-sm font-medium truncate max-w-[120px]">
                                {user?.full_name || 'User'}
                            </p>
                            <p className="text-xs text-dark-400 truncate max-w-[120px]">
                                {user?.email || ''}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="p-2 text-dark-400 hover:text-red-400 transition-colors"
                        title="Logout"
                    >
                        <LogOut className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
}
