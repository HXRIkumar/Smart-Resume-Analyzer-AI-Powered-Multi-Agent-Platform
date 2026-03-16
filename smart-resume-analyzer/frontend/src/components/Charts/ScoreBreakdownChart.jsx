import {
    RadialBarChart, RadialBar, ResponsiveContainer, Legend, Tooltip,
} from 'recharts';

export default function ScoreBreakdownChart({ overall = 0, ats = 0, skillMatch = 0 }) {
    const data = [
        { name: 'Skill Match', value: skillMatch, fill: '#a78bfa' },
        { name: 'ATS Score', value: ats, fill: '#8b5cf6' },
        { name: 'Overall', value: overall, fill: '#6366f1' },
    ];

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Score Breakdown</h3>
            <ResponsiveContainer width="100%" height={280}>
                <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="30%"
                    outerRadius="100%"
                    data={data}
                    startAngle={180}
                    endAngle={0}
                >
                    <RadialBar
                        background={{ fill: '#1e293b' }}
                        dataKey="value"
                        cornerRadius={6}
                    />
                    <Tooltip
                        contentStyle={{
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                        }}
                    />
                    <Legend
                        iconSize={10}
                        layout="horizontal"
                        verticalAlign="bottom"
                        wrapperStyle={{ color: '#94a3b8', fontSize: '12px' }}
                    />
                </RadialBarChart>
            </ResponsiveContainer>
        </div>
    );
}
