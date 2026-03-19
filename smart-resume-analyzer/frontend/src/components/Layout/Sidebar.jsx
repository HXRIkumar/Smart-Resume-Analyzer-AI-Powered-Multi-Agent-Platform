/**
 * Sidebar navigation component.
 *
 * Features:
 * - Teal-accented logo ("Smart Resume")
 * - NavLink items with active state styling
 * - Admin link visible only to admin users
 * - User avatar + name + role at bottom
 * - Logout button
 *
 * @module components/Layout/Sidebar
 */

import React, { useCallback } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
    LayoutDashboard,
    FlaskConical,
    BarChart3,
    Shield,
    LogOut,
    FileText,
    Sparkles,
} from 'lucide-react';

/** @type {{ to: string, icon: React.ElementType, label: string, adminOnly?: boolean }[]} */
const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/lab', icon: FlaskConical, label: 'AI Lab' },
    { to: '/admin', icon: Shield, label: 'Admin', adminOnly: true },
];

const Sidebar = React.memo(function Sidebar() {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = useCallback(() => {
        logout();
        navigate('/login');
    }, [logout, navigate]);

    const isAdmin = user?.role === 'admin';

    return (
        <aside className="w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
            {/* Logo */}
            <div className="p-6 border-b border-dark-700">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-500/25">
                        <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold">
                            <span className="text-white">Smart</span>{' '}
                            <span className="text-primary-400">Resume</span>
                        </h1>
                        <p className="text-xs text-dark-400 tracking-wider">ANALYZER</p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems
                    .filter((item) => !item.adminOnly || isAdmin)
                    .map(({ to, icon: Icon, label }) => (
                        <NavLink
                            key={to}
                            to={to}
                            end={to === '/dashboard'}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                                    ? 'bg-primary-500/15 text-primary-400 border border-primary-500/30'
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
                        <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold text-white">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <div>
                            <p className="text-sm font-medium truncate max-w-[120px]">
                                {user?.full_name || 'User'}
                            </p>
                            <p className="text-xs text-dark-400 truncate max-w-[120px]">
                                {user?.role || 'user'}
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
});

export default Sidebar;
