import { clsx } from 'clsx';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function ScoreCard({ title, value, subtitle, icon: Icon, trend, color = 'primary' }) {
    const colorMap = {
        primary: 'from-primary-600/20 to-primary-800/10 border-primary-500/20',
        success: 'from-emerald-600/20 to-emerald-800/10 border-emerald-500/20',
        warning: 'from-amber-600/20 to-amber-800/10 border-amber-500/20',
        danger: 'from-red-600/20 to-red-800/10 border-red-500/20',
    };

    const iconColorMap = {
        primary: 'text-primary-400 bg-primary-500/10',
        success: 'text-emerald-400 bg-emerald-500/10',
        warning: 'text-amber-400 bg-amber-500/10',
        danger: 'text-red-400 bg-red-500/10',
    };

    return (
        <div
            className={clsx(
                'glass-card p-6 bg-gradient-to-br border transition-all duration-300 hover:scale-[1.02]',
                colorMap[color],
            )}
        >
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-dark-400 font-medium">{title}</p>
                    <p className="text-3xl font-bold mt-2">{value}</p>
                    {subtitle && (
                        <p className="text-xs text-dark-400 mt-1">{subtitle}</p>
                    )}
                </div>
                {Icon && (
                    <div className={clsx('p-3 rounded-xl', iconColorMap[color])}>
                        <Icon className="w-6 h-6" />
                    </div>
                )}
            </div>
            {trend !== undefined && (
                <div className="flex items-center gap-1 mt-3">
                    {trend >= 0 ? (
                        <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                        <TrendingDown className="w-3.5 h-3.5 text-red-400" />
                    )}
                    <span
                        className={clsx(
                            'text-xs font-medium',
                            trend >= 0 ? 'text-emerald-400' : 'text-red-400',
                        )}
                    >
                        {Math.abs(trend)}%
                    </span>
                    <span className="text-xs text-dark-500">vs last month</span>
                </div>
            )}
        </div>
    );
}
