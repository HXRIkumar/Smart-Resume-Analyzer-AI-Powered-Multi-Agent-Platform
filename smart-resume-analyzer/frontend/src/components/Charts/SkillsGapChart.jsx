/**
 * Skills Gap donut chart — PieChart showing present vs missing skill counts.
 *
 * @param {{ presentCount: number, missingCount: number, presentSkills?: string[], missingSkills?: string[] }} props
 * @module components/Charts/SkillsGapChart
 */

import React from 'react';
import {
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
} from 'recharts';

const COLORS = ['#1D9E75', '#ef4444'];

const SkillsGapChart = React.memo(function SkillsGapChart({
    presentCount = 0,
    missingCount = 0,
    presentSkills = [],
    missingSkills = [],
}) {
    const data = [
        { name: 'Present Skills', value: presentCount || presentSkills.length },
        { name: 'Missing Skills', value: missingCount || missingSkills.length },
    ];

    const total = data[0].value + data[1].value;

    if (total === 0) {
        return (
            <div className="glass-card p-6 flex items-center justify-center h-[300px]">
                <p className="text-sm text-dark-400">No skill data available yet</p>
            </div>
        );
    }

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Skills Gap Analysis</h3>
            <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={4}
                        dataKey="value"
                        strokeWidth={0}
                    >
                        {data.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                            fontSize: '13px',
                        }}
                    />
                </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2">
                <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-full bg-primary-500" />
                    <span className="text-dark-400">Present ({data[0].value})</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <span className="text-dark-400">Missing ({data[1].value})</span>
                </div>
            </div>
        </div>
    );
});

export default SkillsGapChart;
