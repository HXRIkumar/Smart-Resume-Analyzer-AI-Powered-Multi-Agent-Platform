import { FileText, Zap, CheckCircle, Clock } from 'lucide-react';

const iconMap = {
    upload: FileText,
    analysis: Zap,
    completed: CheckCircle,
    default: Clock,
};

const colorMap = {
    upload: 'text-blue-400 bg-blue-500/10',
    analysis: 'text-purple-400 bg-purple-500/10',
    completed: 'text-emerald-400 bg-emerald-500/10',
    default: 'text-dark-400 bg-dark-700/50',
};

export default function ActivityFeed({ activities = [] }) {
    if (activities.length === 0) {
        return (
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                <p className="text-sm text-dark-400 text-center py-8">
                    No recent activity. Upload a resume to get started!
                </p>
            </div>
        );
    }

    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-4">
                {activities.map((activity, index) => {
                    const Icon = iconMap[activity.type] || iconMap.default;
                    const colorClass = colorMap[activity.type] || colorMap.default;

                    return (
                        <div
                            key={index}
                            className="flex items-start gap-3 animate-fade-in"
                            style={{ animationDelay: `${index * 100}ms` }}
                        >
                            <div className={`p-2 rounded-lg ${colorClass}`}>
                                <Icon className="w-4 h-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium">{activity.title}</p>
                                <p className="text-xs text-dark-400 mt-0.5">{activity.description}</p>
                            </div>
                            <span className="text-xs text-dark-500 whitespace-nowrap">
                                {activity.time}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
