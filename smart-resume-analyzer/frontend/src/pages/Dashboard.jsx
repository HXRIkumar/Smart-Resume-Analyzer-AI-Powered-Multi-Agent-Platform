import { useEffect } from 'react';
import { useAnalysisStore } from '../store/analysisStore';
import ScoreCard from '../components/UI/ScoreCard';
import ActivityFeed from '../components/UI/ActivityFeed';
import ScoreBreakdownChart from '../components/Charts/ScoreBreakdownChart';
import { FileText, Zap, TrendingUp, Target } from 'lucide-react';

export default function Dashboard() {
    const { summary, analyses, fetchSummary, fetchAnalyses } = useAnalysisStore();

    useEffect(() => {
        fetchSummary();
        fetchAnalyses();
    }, [fetchSummary, fetchAnalyses]);

    const latestAnalysis = analyses?.[0];

    const recentActivities = analyses.slice(0, 5).map((a) => ({
        type: a.status === 'completed' ? 'completed' : 'analysis',
        title: `Analysis #${a.id}`,
        description: `Score: ${a.overall_score} — ${a.status}`,
        time: new Date(a.created_at).toLocaleDateString(),
    }));

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <p className="text-dark-400 mt-1">Overview of your resume analysis activity</p>
            </div>

            {/* Score cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <ScoreCard
                    title="Total Analyses"
                    value={summary?.total_analyses ?? 0}
                    icon={Zap}
                    color="primary"
                    trend={12}
                />
                <ScoreCard
                    title="Avg Score"
                    value={summary?.average_score ?? 0}
                    subtitle="out of 100"
                    icon={TrendingUp}
                    color="success"
                    trend={5}
                />
                <ScoreCard
                    title="Resumes"
                    value={analyses.length}
                    icon={FileText}
                    color="warning"
                />
                <ScoreCard
                    title="Top Score"
                    value={
                        analyses.length > 0
                            ? Math.max(...analyses.map((a) => a.overall_score || 0))
                            : 0
                    }
                    icon={Target}
                    color="danger"
                />
            </div>

            {/* Charts & Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ScoreBreakdownChart
                    overall={latestAnalysis?.overall_score ?? 0}
                    ats={latestAnalysis?.ats_score ?? 0}
                    skillMatch={latestAnalysis?.skill_match_score ?? 0}
                />
                <ActivityFeed activities={recentActivities} />
            </div>
        </div>
    );
}
