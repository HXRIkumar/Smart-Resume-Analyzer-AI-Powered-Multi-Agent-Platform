import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAnalysisStore } from '../store/analysisStore';
import ScoreBreakdownChart from '../components/Charts/ScoreBreakdownChart';
import SkillsGapChart from '../components/Charts/SkillsGapChart';
import SkillChip from '../components/UI/SkillChip';
import { CheckCircle, Clock, AlertTriangle, Loader2 } from 'lucide-react';

const statusIcons = {
    completed: <CheckCircle className="w-5 h-5 text-emerald-400" />,
    processing: <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />,
    pending: <Clock className="w-5 h-5 text-amber-400" />,
    failed: <AlertTriangle className="w-5 h-5 text-red-400" />,
};

export default function Analysis() {
    const { id } = useParams();
    const { currentAnalysis, fetchAnalysis, isLoading } = useAnalysisStore();

    useEffect(() => {
        if (id) fetchAnalysis(parseInt(id));
    }, [id, fetchAnalysis]);

    if (isLoading || !currentAnalysis) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
        );
    }

    const a = currentAnalysis;
    const skills = (() => {
        try { return typeof a.extracted_skills === 'string' ? JSON.parse(a.extracted_skills) : a.extracted_skills || []; }
        catch { return []; }
    })();
    const gaps = (() => {
        try { return typeof a.skill_gaps === 'string' ? JSON.parse(a.skill_gaps) : a.skill_gaps || []; }
        catch { return []; }
    })();
    const atsIssues = (() => {
        try { return typeof a.ats_issues === 'string' ? JSON.parse(a.ats_issues) : a.ats_issues || []; }
        catch { return []; }
    })();

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Analysis #{a.id}</h1>
                    <div className="flex items-center gap-2 mt-1">
                        {statusIcons[a.status] || statusIcons.pending}
                        <span className="text-sm text-dark-400 capitalize">{a.status}</span>
                        {a.processing_time_ms && (
                            <span className="text-xs text-dark-500">
                                • {(a.processing_time_ms / 1000).toFixed(1)}s
                            </span>
                        )}
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-4xl font-bold gradient-text">{a.overall_score}</p>
                    <p className="text-xs text-dark-400">Overall Score</p>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ScoreBreakdownChart
                    overall={a.overall_score}
                    ats={a.ats_score}
                    skillMatch={a.skill_match_score}
                />
                <SkillsGapChart skills={skills} gaps={gaps} />
            </div>

            {/* Skills */}
            {skills.length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">Extracted Skills</h3>
                    <div className="flex flex-wrap gap-2">
                        {skills.map((skill, i) => (
                            <SkillChip
                                key={i}
                                name={skill.name}
                                category={skill.category}
                                proficiency={skill.proficiency}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* ATS Issues */}
            {atsIssues.length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">ATS Issues</h3>
                    <div className="space-y-3">
                        {atsIssues.map((issue, i) => (
                            <div
                                key={i}
                                className={`p-4 rounded-lg border ${issue.severity === 'high'
                                        ? 'bg-red-500/5 border-red-500/20'
                                        : issue.severity === 'medium'
                                            ? 'bg-amber-500/5 border-amber-500/20'
                                            : 'bg-dark-800/50 border-dark-700'
                                    }`}
                            >
                                <p className="text-sm font-medium">{issue.issue}</p>
                                <p className="text-xs text-dark-400 mt-1">{issue.suggestion}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Feedback */}
            {a.feedback && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold mb-4">AI Feedback</h3>
                    <div className="prose prose-invert max-w-none text-sm text-dark-300 leading-relaxed whitespace-pre-wrap">
                        {a.feedback}
                    </div>
                </div>
            )}
        </div>
    );
}
