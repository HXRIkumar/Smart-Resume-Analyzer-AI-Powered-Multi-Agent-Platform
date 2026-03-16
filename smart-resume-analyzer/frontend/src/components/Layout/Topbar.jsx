import { Bell, Search } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export default function Topbar() {
    const { user } = useAuthStore();

    return (
        <header className="h-16 bg-dark-900/80 backdrop-blur-md border-b border-dark-700 flex items-center justify-between px-6">
            {/* Search */}
            <div className="relative w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                <input
                    type="text"
                    placeholder="Search resumes, analyses..."
                    className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-sm text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                />
            </div>

            {/* Right side */}
            <div className="flex items-center gap-4">
                {/* Notifications */}
                <button className="relative p-2 text-dark-400 hover:text-dark-200 transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                </button>

                {/* Environment badge */}
                <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {import.meta.env.MODE}
                </span>

                {/* User greeting */}
                <span className="text-sm text-dark-400">
                    Welcome, <span className="text-dark-200 font-medium">{user?.full_name?.split(' ')[0] || 'User'}</span>
                </span>
            </div>
        </header>
    );
}
