/**
 * Admin chart components — Line chart for applications over time,
 * Bar chart for score distribution, horizontal bar for missing sections.
 *
 * @module components/Charts/AdminCharts
 */

import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, Cell,
} from 'recharts';

const TOOLTIP_STYLE = {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '8px',
    color: '#f1f5f9',
    fontSize: '13px',
};

const COLORS = ['#1D9E75', '#26B487', '#4DC29C', '#80D4B8', '#B3E6D4'];

/**
 * Applications over time — monthly LineChart.
 *
 * @param {{ data: { month: string, count: number }[] }} props
 */
export const ApplicationsLineChart = React.memo(function ApplicationsLineChart({ data = [] }) {
    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Applications Over Time</h3>
            <ResponsiveContainer width="100%" height={260}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip contentStyle={TOOLTIP_STYLE} />
                    <Line
                        type="monotone"
                        dataKey="count"
                        stroke="#1D9E75"
                        strokeWidth={2.5}
                        dot={{ fill: '#1D9E75', r: 4 }}
                        activeDot={{ r: 6, fill: '#26B487' }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
});

/**
 * Score distribution — BarChart histogram.
 *
 * @param {{ data: { range: string, count: number }[] }} props
 */
export const ScoreDistributionBar = React.memo(function ScoreDistributionBar({ data = [] }) {
    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Score Distribution</h3>
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="range" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip contentStyle={TOOLTIP_STYLE} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {data.map((_, i) => (
                            <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
});

/**
 * Missing sections — horizontal BarChart.
 *
 * @param {{ data: { section: string, count: number }[] }} props
 */
export const MissingSectionsBar = React.memo(function MissingSectionsBar({ data = [] }) {
    if (data.length === 0) {
        return (
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4">Top Missing Sections</h3>
                <p className="text-sm text-dark-400 text-center py-8">No data available</p>
            </div>
        );
    }

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Top Missing Sections</h3>
            <div className="space-y-3">
                {data.slice(0, 8).map(({ section, count }, i) => {
                    const max = Math.max(...data.map((d) => d.count));
                    const pct = max > 0 ? (count / max) * 100 : 0;
                    return (
                        <div key={i}>
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-dark-300 capitalize">{section}</span>
                                <span className="text-xs font-mono text-dark-400">{count}</span>
                            </div>
                            <div className="w-full h-2 bg-dark-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full rounded-full transition-all duration-500"
                                    style={{ width: `${pct}%`, backgroundColor: COLORS[i % COLORS.length] }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
});

// Backward compatibility
export { ApplicationsLineChart as UserGrowthChart };
export { ScoreDistributionBar as AnalysisDistributionChart };
