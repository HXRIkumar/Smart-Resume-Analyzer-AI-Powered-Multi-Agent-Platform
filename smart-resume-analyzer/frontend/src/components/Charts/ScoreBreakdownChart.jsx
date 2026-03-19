/**
 * Score breakdown component — 5 horizontal progress bars.
 *
 * Displays: Objectives, Skills, Projects, Formatting, Experience scores.
 *
 * @param {{ scores: { label: string, value: number, color?: string }[] }} props
 * @module components/Charts/ScoreBreakdownChart
 */

import React from 'react';

const defaultScores = [
    { label: 'Objectives', value: 0, color: '#1D9E75' },
    { label: 'Skills', value: 0, color: '#26B487' },
    { label: 'Projects', value: 0, color: '#4DC29C' },
    { label: 'Formatting', value: 0, color: '#80D4B8' },
    { label: 'Experience', value: 0, color: '#B3E6D4' },
];

const ScoreBreakdownChart = React.memo(function ScoreBreakdownChart({ scores }) {
    const data = scores?.length ? scores : defaultScores;

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-5">Score Breakdown</h3>
            <div className="space-y-4">
                {data.map(({ label, value, color }, i) => (
                    <div key={i}>
                        <div className="flex items-center justify-between mb-1.5">
                            <span className="text-sm text-dark-300">{label}</span>
                            <span className="text-sm font-mono font-bold text-dark-200">
                                {Math.round(value)}%
                            </span>
                        </div>
                        <div className="w-full h-2.5 bg-dark-800 rounded-full overflow-hidden">
                            <div
                                className="h-full rounded-full transition-all duration-700 ease-out"
                                style={{
                                    width: `${Math.min(value, 100)}%`,
                                    backgroundColor: color || '#1D9E75',
                                }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
});

export default ScoreBreakdownChart;
