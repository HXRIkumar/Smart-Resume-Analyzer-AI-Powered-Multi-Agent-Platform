/**
 * Admin Dashboard page — Platform-wide analytics, charts, and user management.
 *
 * Features:
 * - 4 stat cards from /admin/analytics
 * - Applications Over Time (LineChart)
 * - Score Distribution (BarChart)
 * - Top Missing Sections (horizontal bars)
 * - Users table with search, filter chips, pagination
 *
 * @module pages/AdminDashboard
 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import { getAnalytics, getUsers, getAnalyses } from '../api/admin';
import ScoreCard from '../components/UI/ScoreCard';
import {
    ApplicationsLineChart,
    ScoreDistributionBar,
    MissingSectionsBar,
} from '../components/Charts/AdminCharts';
import { Users, FileText, Zap, TrendingUp, Search, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE = 10;
const FILTER_OPTIONS = ['All', 'Pending', 'Reviewed'];

export default function AdminDashboard() {
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [analyses, setAnalyses] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilter, setActiveFilter] = useState('All');
    const [page, setPage] = useState(0);

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            try {
                const [statsRes, usersRes, analysesRes] = await Promise.all([
                    getAnalytics(),
                    getUsers(0, 200),
                    getAnalyses(),
                ]);
                if (cancelled) return;
                setStats(statsRes.data);
                setUsers(Array.isArray(usersRes.data) ? usersRes.data : []);
                setAnalyses(Array.isArray(analysesRes.data) ? analysesRes.data : []);
            } catch {
                // Admin endpoints may not be accessible
            } finally {
                if (!cancelled) setIsLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, []);

    // ─── Chart data transforms ───────────────────────────────────────────
    const applicationsData = useMemo(() => {
        if (!stats?.applications_over_time) return [];
        return stats.applications_over_time.map((item) => ({
            month: item.month,
            count: item.count,
        }));
    }, [stats]);

    const scoreDistData = useMemo(() => {
        if (!stats?.score_histogram) return [];
        return stats.score_histogram.map((item) => ({
            range: item.range || item.bucket,
            count: item.count,
        }));
    }, [stats]);

    const missingSectionsData = useMemo(() => {
        if (!stats?.top_missing_sections) return [];
        return stats.top_missing_sections.map((item) => ({
            section: typeof item === 'string' ? item : item.section || item.name,
            count: typeof item === 'string' ? 1 : item.count || 1,
        }));
    }, [stats]);

    // ─── Filtered/paginated users ────────────────────────────────────────
    const filteredUsers = useMemo(() => {
        let result = users;
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            result = result.filter(
                (u) =>
                    u.full_name?.toLowerCase().includes(q) ||
                    u.email?.toLowerCase().includes(q),
            );
        }
        if (activeFilter !== 'All') {
            result = result.filter((u) =>
                activeFilter === 'Pending' ? !u.is_active : u.is_active,
            );
        }
        return result;
    }, [users, searchQuery, activeFilter]);

    const paginatedUsers = useMemo(() => {
        const start = page * PAGE_SIZE;
        return filteredUsers.slice(start, start + PAGE_SIZE);
    }, [filteredUsers, page]);

    const totalPages = Math.ceil(filteredUsers.length / PAGE_SIZE);

    const handleSearch = useCallback((e) => {
        setSearchQuery(e.target.value);
        setPage(0);
    }, []);

    if (isLoading) {
        return (
            <div className="space-y-6 animate-fade-in">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="glass-card p-6">
                            <div className="skeleton w-24 h-4 mb-3" />
                            <div className="skeleton w-16 h-8" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold font-display">Admin Dashboard</h1>
                <p className="text-dark-400 mt-1">Platform-wide analytics and user management</p>
            </div>

            {/* Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <ScoreCard
                    title="Total Applications"
                    value={stats?.total_analyses ?? 0}
                    icon={Zap}
                    color="primary"
                />
                <ScoreCard
                    title="Avg Score"
                    value={stats?.average_resume_score ? Math.round(stats.average_resume_score) : 0}
                    subtitle="out of 100"
                    icon={TrendingUp}
                    color="success"
                />
                <ScoreCard
                    title="Total Users"
                    value={stats?.total_users ?? 0}
                    icon={Users}
                    color="warning"
                />
                <ScoreCard
                    title="Top Career"
                    value={stats?.most_popular_career ?? 'N/A'}
                    icon={FileText}
                    color="danger"
                />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ApplicationsLineChart data={applicationsData} />
                <ScoreDistributionBar data={scoreDistData} />
            </div>

            {/* Missing Sections */}
            <MissingSectionsBar data={missingSectionsData} />

            {/* Users Table */}
            <div className="glass-card p-6">
                {/* Search + Filters */}
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
                    <h3 className="text-lg font-semibold">Users</h3>
                    <div className="flex items-center gap-3 flex-wrap">
                        {/* Filter chips */}
                        <div className="flex gap-2">
                            {FILTER_OPTIONS.map((filter) => (
                                <button
                                    key={filter}
                                    onClick={() => { setActiveFilter(filter); setPage(0); }}
                                    className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-all ${activeFilter === filter
                                            ? 'bg-primary-500/15 text-primary-400 border-primary-500/30'
                                            : 'bg-dark-800/50 text-dark-400 border-dark-700 hover:border-dark-600'
                                        }`}
                                >
                                    {filter}
                                </button>
                            ))}
                        </div>
                        {/* Search */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={handleSearch}
                                placeholder="Search users..."
                                className="pl-9 pr-4 py-2 bg-dark-800 border border-dark-700 rounded-lg text-sm text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                            />
                        </div>
                    </div>
                </div>

                {/* Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-dark-700">
                                <th className="text-left py-3 px-4 text-dark-400 font-medium">Name</th>
                                <th className="text-left py-3 px-4 text-dark-400 font-medium">Email</th>
                                <th className="text-left py-3 px-4 text-dark-400 font-medium">Provider</th>
                                <th className="text-left py-3 px-4 text-dark-400 font-medium">Status</th>
                                <th className="text-left py-3 px-4 text-dark-400 font-medium">Joined</th>
                            </tr>
                        </thead>
                        <tbody>
                            {paginatedUsers.map((user) => (
                                <tr
                                    key={user.id}
                                    className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors"
                                >
                                    <td className="py-3 px-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-7 h-7 rounded-full bg-primary-600 flex items-center justify-center text-xs font-bold text-white">
                                                {user.full_name?.charAt(0) || 'U'}
                                            </div>
                                            <span className="font-medium">{user.full_name}</span>
                                        </div>
                                    </td>
                                    <td className="py-3 px-4 text-dark-400">{user.email}</td>
                                    <td className="py-3 px-4">
                                        <span className="px-2 py-0.5 text-xs rounded-full bg-dark-700 text-dark-300">
                                            {user.auth_provider || 'local'}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4">
                                        <span
                                            className={`px-2 py-0.5 text-xs rounded-full ${user.is_active
                                                    ? 'bg-emerald-500/10 text-emerald-400'
                                                    : 'bg-red-500/10 text-red-400'
                                                }`}
                                        >
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-dark-400 font-mono text-xs">
                                        {user.created_at
                                            ? new Date(user.created_at).toLocaleDateString()
                                            : '—'}
                                    </td>
                                </tr>
                            ))}
                            {paginatedUsers.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="py-8 text-center text-dark-400">
                                        {searchQuery ? 'No users match your search' : 'No users found'}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-dark-700">
                        <p className="text-xs text-dark-400">
                            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, filteredUsers.length)} of{' '}
                            {filteredUsers.length} users
                        </p>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setPage((p) => Math.max(0, p - 1))}
                                disabled={page === 0}
                                className="p-1.5 rounded-lg bg-dark-800 text-dark-400 hover:text-dark-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <span className="text-xs text-dark-400 font-mono">
                                {page + 1}/{totalPages}
                            </span>
                            <button
                                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                                disabled={page >= totalPages - 1}
                                className="p-1.5 rounded-lg bg-dark-800 text-dark-400 hover:text-dark-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
