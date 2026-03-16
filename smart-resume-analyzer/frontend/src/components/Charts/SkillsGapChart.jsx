import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8'];

export default function SkillsGapChart({ skills = [], gaps = [] }) {
    const data = [
        ...skills.slice(0, 5).map((s) => ({
            name: typeof s === 'string' ? s : s.name,
            value: 1,
            type: 'present',
        })),
        ...gaps.slice(0, 5).map((g) => ({
            name: typeof g === 'string' ? g : g.name,
            value: 1,
            type: 'gap',
        })),
    ];

    if (data.length === 0) {
        return (
            <div className="glass-card p-6 text-center text-dark-400">
                <p>No skill data available yet</p>
            </div>
        );
    }

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Skills Gap Analysis</h3>
            <ResponsiveContainer width="100%" height={250}>
                <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" hide />
                    <YAxis
                        type="category"
                        dataKey="name"
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        width={80}
                    />
                    <Tooltip
                        contentStyle={{
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {data.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.type === 'present' ? COLORS[index % COLORS.length] : '#ef4444'}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-3 text-xs">
                <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded bg-primary-500" />
                    <span className="text-dark-400">Present</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded bg-red-500" />
                    <span className="text-dark-400">Gap</span>
                </div>
            </div>
        </div>
    );
}
