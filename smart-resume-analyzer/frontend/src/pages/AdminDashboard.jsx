import { useEffect, useState } from 'react';
import ScoreCard from '../components/UI/ScoreCard';
import { UserGrowthChart, AnalysisDistributionChart } from '../components/Charts/AdminCharts';
import { Users, FileText, Zap, TrendingUp } from 'lucide-react';
import client from '../api/client';

export default function AdminDashboard() {
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const load = async () => {
            try {
                const [statsRes, usersRes] = await Promise.all([
                    client.get('/admin/stats'),
                    client.get('/admin/users'),
                ]);
                setStats(statsRes.data);
                setUsers(usersRes.data.users || []);
            } catch {
                // Admin endpoints may not be accessible
            }
        };
        load();
    }, []);

    // Mock chart data
    const userGrowthData = [
        { month: 'Jan', users: 12 },
        { month: 'Feb', users: 28 },
        { month: 'Mar', users: 45 },
        { month: 'Apr', users: 72 },
        { month: 'May', users: 98 },
        { month: 'Jun', users: 134 },
    ];

    const distributionData = [
        { name: '90-100', value: 15 },
        { name: '70-89', value: 35 },
        { name: '50-69', value: 30 },
        { name: '<50', value: 20 },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Admin Dashboard</h1>
                <p className="text-dark-400 mt-1">Platform-wide analytics and user management</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <ScoreCard title="Total Users" value={stats?.total_users ?? 0} icon={Users} color="primary" />
                <ScoreCard title="Total Resumes" value={stats?.total_resumes ?? 0} icon={FileText} color="success" />
                <ScoreCard title="Total Analyses" value={stats?.total_analyses ?? 0} icon={Zap} color="warning" />
                <ScoreCard title="Avg Score" value={stats?.average_score ?? 0} icon={TrendingUp} color="danger" />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <UserGrowthChart data={userGrowthData} />
                <AnalysisDistributionChart data={distributionData} />
            </div>

            {/* Users table */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4">Users</h3>
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
                            {users.map((user) => (
                                <tr key={user.id} className="border-b border-dark-800 hover:bg-dark-800/50 transition-colors">
                                    <td className="py-3 px-4 font-medium">{user.full_name}</td>
                                    <td className="py-3 px-4 text-dark-400">{user.email}</td>
                                    <td className="py-3 px-4">
                                        <span className="px-2 py-0.5 text-xs rounded-full bg-dark-700 text-dark-300">
                                            {user.auth_provider}
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
                                    <td className="py-3 px-4 text-dark-400">
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))}
                            {users.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="py-8 text-center text-dark-400">
                                        No users found
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
