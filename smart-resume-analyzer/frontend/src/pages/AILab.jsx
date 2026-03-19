/**
 * AI Lab page — Live scan animation, agent pipeline, career predictions, keyword heatmap.
 *
 * Features:
 * - Scan animation (CSS beam over resume)
 * - 5-agent pipeline status with checkmark/spinner
 * - Poll GET /analysis/result/{id} every 2s while analyzing
 * - AI Decision Breakdown: 5 metric cards
 * - Career Path Predictions with confidence bars
 * - Keyword Heatmap chips (sized by impact)
 *
 * @module pages/AILab
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAnalysisStore } from '../store/analysisStore';
import {
    Upload, Zap, CheckCircle, Loader2, Brain, Target,
    TrendingUp, Award, FileText, Search,
} from 'lucide-react';

/** Pipeline agent steps */
const PIPELINE_STEPS = [
    { key: 'parser', label: 'Resume Parser', icon: FileText },
    { key: 'skills', label: 'Skill Analyzer', icon: Search },
    { key: 'ats', label: 'ATS Evaluator', icon: Target },
    { key: 'career', label: 'Career Predictor', icon: TrendingUp },
    { key: 'feedback', label: 'Feedback Agent', icon: Brain },
];

export default function AILab() {
    const navigate = useNavigate();
    const {
        currentAnalysis, isAnalyzing, analysisProgress,
        uploadAndAnalyze, pollAnalysis,
    } = useAnalysisStore();
    const [activeStep, setActiveStep] = useState(-1);
    const [analysisId, setAnalysisId] = useState(null);
    const cleanupRef = useRef(null);

    // Simulate pipeline step progression
    useEffect(() => {
        if (!isAnalyzing) {
            setActiveStep(-1);
            return;
        }
        let step = 0;
        const timer = setInterval(() => {
            setActiveStep(step);
            step++;
            if (step >= PIPELINE_STEPS.length) clearInterval(timer);
        }, 800);
        return () => clearInterval(timer);
    }, [isAnalyzing]);

    // Poll for result
    useEffect(() => {
        if (analysisId && isAnalyzing) {
            cleanupRef.current = pollAnalysis(analysisId);
        }
        return () => {
            if (cleanupRef.current) cleanupRef.current();
        };
    }, [analysisId, isAnalyzing, pollAnalysis]);

    const onDrop = useCallback(
        async (files) => {
            const file = files[0];
            if (!file) return;
            if (file.type !== 'application/pdf') {
                toast.error('Only PDF files are accepted');
                return;
            }
            try {
                const result = await uploadAndAnalyze(file);
                if (result?.id) {
                    setAnalysisId(result.id);
                    toast.success('Analysis complete!');
                }
            } catch {
                toast.error('Analysis failed');
            }
        },
        [uploadAndAnalyze],
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024,
    });

    const a = currentAnalysis;

    // ─── Decision breakdown metrics ──────────────────────────────────────
    const decisionMetrics = a
        ? [
            { label: 'Skills Match', value: 35, icon: Zap, color: '#1D9E75' },
            { label: 'Project Quality', value: 25, icon: Award, color: '#26B487' },
            { label: 'Experience Depth', value: 20, icon: TrendingUp, color: '#4DC29C' },
            { label: 'Education Fit', value: 10, icon: Brain, color: '#80D4B8' },
            { label: 'Formatting', value: 10, icon: FileText, color: '#B3E6D4' },
        ]
        : [];

    // ─── Career predictions ──────────────────────────────────────────────
    const careerPredictions = (() => {
        if (!a?.career_predictions) return [];
        const preds = a.career_predictions?.predictions || a.career_predictions;
        if (Array.isArray(preds)) return preds.slice(0, 5);
        return [];
    })();

    // ─── Keywords extraction ─────────────────────────────────────────────
    const keywords = (() => {
        const skills = a?.present_skills ?? [];
        const missing = a?.missing_skills ?? [];
        return [
            ...skills.map((s) => ({
                text: typeof s === 'string' ? s : s?.name,
                impact: 'high',
            })),
            ...missing.map((s) => ({
                text: typeof s === 'string' ? s : s?.name,
                impact: 'low',
            })),
        ].filter(Boolean).slice(0, 20);
    })();

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold font-display">AI Lab</h1>
                <p className="text-dark-400 mt-1">
                    Watch the multi-agent pipeline analyze your resume in real-time
                </p>
            </div>

            {/* Scanner + Upload */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Scan animation area */}
                <div className="glass-card p-6 relative overflow-hidden min-h-[320px] flex flex-col items-center justify-center">
                    {isAnalyzing && (
                        <div className="absolute inset-0 pointer-events-none">
                            <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-primary-400 to-transparent animate-scan" />
                        </div>
                    )}

                    {isAnalyzing ? (
                        <div className="text-center z-10">
                            <Loader2 className="w-16 h-16 text-primary-400 animate-spin mx-auto mb-4" />
                            <p className="text-lg font-semibold text-primary-400">{analysisProgress}</p>
                            <p className="text-sm text-dark-400 mt-2">Processing through 5 AI agents...</p>
                        </div>
                    ) : a ? (
                        <div className="text-center">
                            <div className="w-24 h-24 rounded-full bg-primary-500/10 border-2 border-primary-500/30 flex items-center justify-center mx-auto mb-4">
                                <span className="text-3xl font-mono font-bold text-primary-400">
                                    {a.resume_score ?? 0}
                                </span>
                            </div>
                            <p className="text-lg font-semibold">Analysis Complete</p>
                            <p className="text-sm text-dark-400 mt-1">Resume Score</p>
                            <button
                                onClick={() => navigate(`/analysis/${a.id}`)}
                                className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-500 transition-colors text-sm font-medium"
                            >
                                View Full Report
                            </button>
                        </div>
                    ) : (
                        <div {...getRootProps()} className="text-center cursor-pointer">
                            <input {...getInputProps()} />
                            <Upload className="w-16 h-16 text-dark-500 mx-auto mb-4" />
                            <p className="text-lg font-medium">
                                {isDragActive ? 'Drop to scan' : 'Drop a resume to start scanning'}
                            </p>
                            <p className="text-sm text-dark-400 mt-2">PDF only • Max 10MB</p>
                        </div>
                    )}
                </div>

                {/* Pipeline Steps */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-5">Agent Pipeline</h3>
                    <div className="space-y-4">
                        {PIPELINE_STEPS.map(({ key, label, icon: Icon }, i) => {
                            const isDone = activeStep > i || (!isAnalyzing && a);
                            const isActive = activeStep === i && isAnalyzing;
                            return (
                                <div
                                    key={key}
                                    className={`flex items-center gap-4 p-3 rounded-lg transition-all duration-300 ${isActive
                                            ? 'bg-primary-500/10 border border-primary-500/30'
                                            : isDone
                                                ? 'bg-dark-800/30'
                                                : 'bg-dark-800/10'
                                        }`}
                                >
                                    <div
                                        className={`w-9 h-9 rounded-lg flex items-center justify-center ${isDone
                                                ? 'bg-primary-500/20 text-primary-400'
                                                : isActive
                                                    ? 'bg-primary-500/20 text-primary-400'
                                                    : 'bg-dark-800 text-dark-500'
                                            }`}
                                    >
                                        {isDone ? (
                                            <CheckCircle className="w-5 h-5" />
                                        ) : isActive ? (
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                        ) : (
                                            <Icon className="w-5 h-5" />
                                        )}
                                    </div>
                                    <div className="flex-1">
                                        <p className={`text-sm font-medium ${isDone || isActive ? 'text-dark-200' : 'text-dark-500'}`}>
                                            {label}
                                        </p>
                                        <p className="text-xs text-dark-500">
                                            {isDone ? 'Completed' : isActive ? 'Processing...' : 'Waiting'}
                                        </p>
                                    </div>
                                    <span className={`text-xs font-mono ${isDone ? 'text-primary-400' : 'text-dark-600'}`}>
                                        {isDone ? '✓' : `0${i + 1}`}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* AI Decision Breakdown */}
            {decisionMetrics.length > 0 && (
                <div>
                    <h3 className="text-lg font-semibold mb-4">AI Decision Breakdown</h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        {decisionMetrics.map(({ label, value, icon: Icon, color }, i) => (
                            <div
                                key={i}
                                className="glass-card p-4 text-center hover:scale-[1.02] transition-transform"
                            >
                                <div
                                    className="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-3"
                                    style={{ backgroundColor: `${color}15` }}
                                >
                                    <Icon className="w-5 h-5" style={{ color }} />
                                </div>
                                <p className="text-2xl font-mono font-bold" style={{ color }}>
                                    {value}%
                                </p>
                                <p className="text-xs text-dark-400 mt-1">{label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Career Path Predictions */}
            {careerPredictions.length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Career Path Predictions</h3>
                    <div className="space-y-4">
                        {careerPredictions.map((pred, i) => {
                            const role = typeof pred === 'string' ? pred : pred?.role || pred?.title;
                            const confidence = typeof pred === 'string' ? 90 - i * 15 : (pred?.confidence ?? (90 - i * 15));
                            return (
                                <div key={i} className="flex items-center gap-4">
                                    <div className="w-8 h-8 rounded-lg bg-primary-500/10 flex items-center justify-center text-sm font-mono font-bold text-primary-400">
                                        #{i + 1}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium mb-1">{role}</p>
                                        <div className="w-full h-2 bg-dark-800 rounded-full overflow-hidden">
                                            <div
                                                className="h-full rounded-full bg-primary-500 transition-all duration-700"
                                                style={{ width: `${confidence}%` }}
                                            />
                                        </div>
                                    </div>
                                    <span className="text-sm font-mono text-primary-400">
                                        {Math.round(confidence)}%
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Keyword Heatmap */}
            {keywords.length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Keyword Impact Map</h3>
                    <div className="flex flex-wrap gap-2">
                        {keywords.map(({ text, impact }, i) => (
                            <span
                                key={i}
                                className={`inline-flex items-center rounded-full font-medium border transition-all duration-200 hover:scale-105 ${impact === 'high'
                                        ? 'px-4 py-2 text-sm bg-primary-500/10 text-primary-400 border-primary-500/20'
                                        : impact === 'medium'
                                            ? 'px-3 py-1.5 text-xs bg-amber-500/10 text-amber-400 border-amber-500/20'
                                            : 'px-2.5 py-1 text-xs bg-red-500/10 text-red-400 border-red-500/20'
                                    }`}
                            >
                                {text}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
