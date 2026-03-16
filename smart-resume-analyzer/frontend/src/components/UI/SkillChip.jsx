import { clsx } from 'clsx';

const categoryColors = {
    programming: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    frameworks: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    cloud: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    data: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    databases: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    soft_skills: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
    default: 'bg-dark-700/50 text-dark-300 border-dark-600/30',
};

export default function SkillChip({ name, category, proficiency, onRemove }) {
    const colorClass = categoryColors[category] || categoryColors.default;

    return (
        <span
            className={clsx(
                'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200 hover:scale-105',
                colorClass,
            )}
        >
            {name}
            {proficiency && (
                <span className="opacity-60 text-[10px]">• {proficiency}</span>
            )}
            {onRemove && (
                <button
                    onClick={onRemove}
                    className="ml-1 hover:opacity-70 transition-opacity"
                >
                    ×
                </button>
            )}
        </span>
    );
}
