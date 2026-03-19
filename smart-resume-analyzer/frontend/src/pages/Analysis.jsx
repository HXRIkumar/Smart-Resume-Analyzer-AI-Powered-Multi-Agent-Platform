/**
 * Analysis detail page — KPI cards, strengths/improvements, radar chart, AI feedback.
 *
 * Features:
 * - 4 KPI cards: Score, AI Confidence, ATS Score, Improvements count
 * - Strengths section (green checks)
 * - Areas to Improve (amber warnings)
 * - Recent activity feed with colored dots
 * - AI Feedback card (monospace font)
 * - Radar chart (5 axes: Skills, Projects, Experience, Education, Formatting)
 *
 * @module pages/Analysis
 */

import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAnalysisStore } from '../store/analysisStore';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
} from 'recharts';
import {
    CheckCircle, AlertTriangle, Loader2, TrendingUp,
    Shield, Brain, Target, ArrowLeft, Sparkles,
} from 'lucide-react';

export default function Analysis() {
    const { id } = useParams();
    const { currentAnalysis, fetchAnalysis, isLoading } = useAnalysisStore();

    useEffect(() => {
        if (id) fetchAnalysis(id);
    }, [id, fetchAnalysis]);

    if (isLoading || !currentAnalysis) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
        );
    }

    const a = currentAnalysis;

    // ─── KPI data ────────────────────────────────────────────────────────
    const kpis = [
        {
            label: 'Resume Score',
            value: a.resume_score ?? 0,
            suffix: '/100',
            icon: TrendingUp,
            color: 'primary',
        },
        {
            label: 'AI Confidence',
            value: a.ai_confidence ? `${Math.round(a.ai_confidence * 100)}%` : 'N/A',
            icon: Brain,
            color: 'purple',
        },
        {
            label: 'ATS Score',
            value: a.ats_score ?? 0,
            suffix: '/100',
            icon: Shield,
            color: 'blue',
        },
        {
            label: 'Improvements',
            value: a.improvements?.length ?? 0,
            icon: Target,
            color: 'amber',
        },
    ];

    const colorMap = {
        primary: { bg: 'bg-primary-500/10', text: 'text-primary-400', border: 'border-primary-500/20' },
        purple: { bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20' },
        blue: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20' },
        amber: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
    };

    // ─── Strengths & improvements ────────────────────────────────────────
    const strengths = a.strengths ?? a.present_skills ?? [];
    const improvements = a.improvements ?? a.missing_skills ?? [];

    // ─── Radar chart data ────────────────────────────────────────────────
    const radarData = [
        { axis: 'Skills', value: a.resume_score ? Math.min(a.resume_score + 5, 100) : 50 },
        { axis: 'Projects', value: a.ai_confidence ? a.ai_confidence * 100 : 45 },
        { axis: 'Experience', value: a.ats_score ? Math.min(a.ats_score - 5, 100) : 40 },
        { axis: 'Education', value: a.resume_score ? Math.min(a.resume_score - 10, 100) : 55 },
        { axis: 'Formatting', value: a.ats_score ?? 60 },
    ];

    // ─── Feedback ────────────────────────────────────────────────────────
    const feedback = a.feedback_text || a.feedback || '';

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link
                        to="/dashboard"
                        className="p-2 rounded-lg bg-dark-800 text-dark-400 hover:text-dark-200 hover:bg-dark-700 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold font-display">Analysis Report</h1>
                        <p className="text-sm text-dark-400 mt-0.5">
                            ID: <span className="font-mono text-dark-500">{a.id}</span>
                        </p>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-4xl font-mono font-bold gradient-text">{a.resume_score ?? 0}</p>
                    <p className="text-xs text-dark-400">Overall Score</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {kpis.map(({ label, value, suffix, icon: Icon, color }, i) => {
                    const c = colorMap[color];
                    return (
                        <div key={i} className={`glass-card p-5 border ${c.border}`}>
                            <div className="flex items-center gap-3 mb-3">
                                <div className={`p-2.5 rounded-xl ${c.bg}`}>
                                    <Icon className={`w-5 h-5 ${c.text}`} />
                                </div>
                            </div>
                            <p className="text-2xl font-mono font-bold">
                                {value}
                                {suffix && <span className="text-sm text-dark-500 font-sans">{suffix}</span>}
                            </p>
                            <p className="text-xs text-dark-400 mt-1">{label}</p>
                        </div>
                    );
                })}
            </div>

            {/* Strengths + Improvements + Radar */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Strengths */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-emerald-400" />
                        Strengths
                    </h3>
                    <div className="space-y-3">
                        {strengths.length > 0 ? (
                            strengths.slice(0, 6).map((item, i) => {
                                const text = typeof item === 'string' ? item : item?.name || item;
                                return (
                                    <div key={i} className="flex items-start gap-3">
                                        <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                                        <p className="text-sm text-dark-300">{text}</p>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="text-sm text-dark-500">No strengths identified yet</p>
                        )}
                    </div>
                </div>

                {/* Areas to Improve */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-400" />
                        Areas to Improve
                    </h3>
                    <div className="space-y-3">
                        {improvements.length > 0 ? (
                            improvements.slice(0, 6).map((item, i) => {
                                const text = typeof item === 'string' ? item : item?.name || item;
                                return (
                                    <div key={i} className="flex items-start gap-3">
                                        <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                                        <p className="text-sm text-dark-300">{text}</p>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="text-sm text-dark-500">No improvements identified yet</p>
                        )}
                    </div>
                </div>

                {/* Radar Chart */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Score Radar</h3>
                    <ResponsiveContainer width="100%" height={220}>
                        <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
                            <PolarGrid stroke="#334155" />
                            <PolarAngleAxis
                                dataKey="axis"
                                tick={{ fill: '#94a3b8', fontSize: 11 }}
                            />
                            <PolarRadiusAxis
                                angle={90}
                                domain={[0, 100]}
                                tick={{ fill: '#64748b', fontSize: 10 }}
                            />
                            <Radar
                                dataKey="value"
                                stroke="#1D9E75"
                                fill="#1D9E75"
                                fillOpacity={0.2}
                                strokeWidth={2}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* AI Feedback */}
            {feedback && (
                <div className="glass-card p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Sparkles className="w-5 h-5 text-primary-400" />
                        <h3 className="text-lg font-semibold">AI Feedback</h3>
                    </div>
                    <div className="bg-dark-800/50 border border-dark-700 rounded-xl p-5">
                        <pre className="font-mono text-sm text-dark-300 leading-relaxed whitespace-pre-wrap">
                            {feedback}
                        </pre>
                    </div>
                </div>
            )}

            {/* Activity Timeline */}
            {a.audit_log && Array.isArray(a.audit_log) && a.audit_log.length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Analysis Timeline</h3>
                    <div className="space-y-4">
                        {a.audit_log.map((entry, i) => (
                            <div key={i} className="flex items-start gap-3">
                                <div className="w-2.5 h-2.5 rounded-full bg-primary-500 mt-1.5 flex-shrink-0" />
                                <div>
                                    <p className="text-sm font-medium text-dark-300">
                                        {entry.agent || entry.action || `Step ${i + 1}`}
                                    </p>
                                    <p className="text-xs text-dark-500 mt-0.5">
                                        {entry.message || entry.detail || ''}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
