import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { FileText, Sparkles, ArrowRight } from 'lucide-react';

export default function Login() {
    const [isRegister, setIsRegister] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const { login, register, isLoading, error, clearError } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (isRegister) {
                await register(email, fullName, password);
            } else {
                await login(email, password);
            }
            navigate('/');
        } catch {
            // error is set in store
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left — Branding */}
            <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-dark-900 via-primary-950 to-dark-900 items-center justify-center p-12">
                <div className="max-w-md animate-fade-in">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-lg shadow-primary-500/25">
                            <FileText className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">Smart Resume</h1>
                            <span className="text-primary-400 text-sm font-medium">Analyzer</span>
                        </div>
                    </div>
                    <h2 className="text-4xl font-bold leading-tight mb-4">
                        AI-Powered Resume
                        <br />
                        <span className="gradient-text">Analysis Platform</span>
                    </h2>
                    <p className="text-dark-400 text-lg mb-8">
                        Multi-agent AI pipeline that extracts skills, scores ATS compatibility,
                        and predicts career paths — all in seconds.
                    </p>
                    <div className="space-y-4">
                        {[
                            'PDF parsing & text extraction',
                            'NLP skill categorization',
                            'ATS compatibility scoring',
                            'LLM-powered feedback',
                            'ML career path prediction',
                        ].map((feature, i) => (
                            <div key={i} className="flex items-center gap-3 text-dark-300">
                                <Sparkles className="w-4 h-4 text-primary-400 flex-shrink-0" />
                                <span className="text-sm">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Right — Form */}
            <div className="flex-1 flex items-center justify-center p-8 bg-dark-950">
                <div className="w-full max-w-md animate-fade-in">
                    <h2 className="text-3xl font-bold mb-2">
                        {isRegister ? 'Create account' : 'Welcome back'}
                    </h2>
                    <p className="text-dark-400 mb-8">
                        {isRegister
                            ? 'Start analyzing resumes with AI'
                            : 'Sign in to your account'}
                    </p>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {isRegister && (
                            <div>
                                <label className="block text-sm text-dark-400 mb-1.5">Full Name</label>
                                <input
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-dark-200 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                                    placeholder="John Doe"
                                    required
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm text-dark-400 mb-1.5">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-dark-200 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                                placeholder="you@example.com"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-dark-400 mb-1.5">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-dark-200 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                                placeholder="••••••••"
                                required
                                minLength={6}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white font-medium rounded-lg hover:from-primary-500 hover:to-purple-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary-500/25"
                        >
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    {isRegister ? 'Create Account' : 'Sign In'}
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </button>
                    </form>

                    <p className="text-center text-sm text-dark-400 mt-6">
                        {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                        <button
                            onClick={() => {
                                setIsRegister(!isRegister);
                                clearError();
                            }}
                            className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
                        >
                            {isRegister ? 'Sign in' : 'Sign up'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
}
