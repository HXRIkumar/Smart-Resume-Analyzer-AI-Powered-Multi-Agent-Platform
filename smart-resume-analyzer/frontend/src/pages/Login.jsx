/**
 * Login / Register page with Google OAuth support.
 *
 * Features:
 * - Email + password form with client-side validation
 * - Toggle between Sign In and Sign Up modes
 * - "Sign in with Google" button (uses @react-oauth/google)
 * - Form validation via react-hook-form + zod
 * - Error states with animated feedback
 * - Redirect to /dashboard on success
 * - Dark teal theme matching the application design system
 *
 * @module pages/Login
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { GoogleLogin } from '@react-oauth/google';
import { useAuthStore } from '../store/authStore';
import { FileText, Sparkles, ArrowRight, Mail, Lock, User, AlertCircle, Eye, EyeOff } from 'lucide-react';

// ─── Zod Validation Schemas ────────────────────────────────────────────────

const loginSchema = z.object({
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(1, 'Password is required'),
});

const registerSchema = z.object({
    full_name: z
        .string()
        .min(2, 'Name must be at least 2 characters')
        .max(255, 'Name is too long'),
    email: z.string().email('Please enter a valid email address'),
    password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .max(128, 'Password is too long')
        .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
        .regex(/[0-9]/, 'Must contain at least one number'),
});

/**
 * Login/Register page component.
 *
 * @returns {JSX.Element} The rendered login page.
 */
export default function Login() {
    const [isRegister, setIsRegister] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const { login, register: registerUser, googleLogin, isLoading, error, clearError } = useAuthStore();
    const navigate = useNavigate();

    // Choose schema based on mode
    const schema = isRegister ? registerSchema : loginSchema;

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
    } = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
    });

    /**
     * Handle form submission for login or registration.
     *
     * @async
     * @param {object} data - Validated form data.
     */
    const onSubmit = async (data) => {
        try {
            if (isRegister) {
                await registerUser({
                    email: data.email,
                    password: data.password,
                    full_name: data.full_name,
                });
            } else {
                await login({
                    email: data.email,
                    password: data.password,
                });
            }
            navigate('/dashboard');
        } catch {
            // Error is set in the store
        }
    };

    /**
     * Handle successful Google OAuth login.
     *
     * @async
     * @param {{ credential: string }} credentialResponse - Google credential response.
     */
    const handleGoogleSuccess = async (credentialResponse) => {
        try {
            await googleLogin(credentialResponse.credential);
            navigate('/dashboard');
        } catch {
            // Error is set in the store
        }
    };

    /**
     * Handle Google OAuth login failure.
     */
    const handleGoogleError = () => {
        useAuthStore.setState({ error: 'Google sign-in failed. Please try again.' });
    };

    /**
     * Toggle between login and register modes.
     */
    const toggleMode = () => {
        setIsRegister(!isRegister);
        clearError();
        reset();
    };

    return (
        <div className="min-h-screen flex">
            {/* ─── Left Panel — Branding ──────────────────────────────────── */}
            <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-dark-900 via-primary-950 to-dark-900 items-center justify-center p-12 relative overflow-hidden">
                {/* Background decorative elements */}
                <div className="absolute top-20 -left-20 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl" />
                <div className="absolute bottom-20 -right-20 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />

                <div className="max-w-md relative z-10 animate-fade-in">
                    {/* Logo */}
                    <div className="flex items-center gap-3 mb-10">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-lg shadow-primary-500/25">
                            <FileText className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">Smart Resume</h1>
                            <span className="text-primary-400 text-sm font-medium tracking-wider">ANALYZER</span>
                        </div>
                    </div>

                    {/* Headline */}
                    <h2 className="text-4xl font-bold leading-tight mb-4 text-white">
                        AI-Powered Resume
                        <br />
                        <span className="bg-gradient-to-r from-primary-400 to-purple-400 bg-clip-text text-transparent">
                            Analysis Platform
                        </span>
                    </h2>
                    <p className="text-dark-400 text-lg mb-10 leading-relaxed">
                        Multi-agent AI pipeline that extracts skills, scores ATS compatibility,
                        and predicts career paths — all in seconds.
                    </p>

                    {/* Features */}
                    <div className="space-y-4">
                        {[
                            'PDF parsing & intelligent text extraction',
                            'NLP-powered skill categorization',
                            'ATS compatibility scoring (0–100)',
                            'GPT-4o-powered actionable feedback',
                            'ML career path prediction',
                        ].map((feature, i) => (
                            <div
                                key={i}
                                className="flex items-center gap-3 text-dark-300 group"
                                style={{ animationDelay: `${i * 100}ms` }}
                            >
                                <div className="w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center flex-shrink-0 group-hover:bg-primary-500/30 transition-colors">
                                    <Sparkles className="w-3.5 h-3.5 text-primary-400" />
                                </div>
                                <span className="text-sm">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* ─── Right Panel — Auth Form ────────────────────────────────── */}
            <div className="flex-1 flex items-center justify-center p-8 bg-dark-950">
                <div className="w-full max-w-md animate-fade-in">
                    {/* Mobile logo */}
                    <div className="lg:hidden flex items-center gap-3 mb-8">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold text-white">Smart Resume Analyzer</span>
                    </div>

                    {/* Header */}
                    <h2 className="text-3xl font-bold mb-2 text-white">
                        {isRegister ? 'Create your account' : 'Welcome back'}
                    </h2>
                    <p className="text-dark-400 mb-8">
                        {isRegister
                            ? 'Start analyzing resumes with AI intelligence'
                            : 'Sign in to continue to your dashboard'}
                    </p>

                    {/* Google OAuth Button */}
                    <div className="mb-6">
                        <GoogleLogin
                            onSuccess={handleGoogleSuccess}
                            onError={handleGoogleError}
                            theme="filled_black"
                            size="large"
                            width="100%"
                            text={isRegister ? 'signup_with' : 'signin_with'}
                            shape="pill"
                        />
                    </div>

                    {/* Divider */}
                    <div className="relative mb-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-dark-700" />
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-4 bg-dark-950 text-dark-500">or continue with email</span>
                        </div>
                    </div>

                    {/* Error Alert */}
                    {error && (
                        <div className="mb-5 p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3 animate-shake">
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {/* Full Name (register only) */}
                        {isRegister && (
                            <div>
                                <label className="block text-sm text-dark-400 mb-1.5 font-medium">
                                    Full Name
                                </label>
                                <div className="relative">
                                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-dark-500" />
                                    <input
                                        {...register('full_name')}
                                        type="text"
                                        className="w-full pl-11 pr-4 py-3 bg-dark-800/50 border border-dark-700 rounded-xl text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                                        placeholder="John Doe"
                                    />
                                </div>
                                {errors.full_name && (
                                    <p className="mt-1.5 text-xs text-red-400">{errors.full_name.message}</p>
                                )}
                            </div>
                        )}

                        {/* Email */}
                        <div>
                            <label className="block text-sm text-dark-400 mb-1.5 font-medium">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-dark-500" />
                                <input
                                    {...register('email')}
                                    type="email"
                                    className="w-full pl-11 pr-4 py-3 bg-dark-800/50 border border-dark-700 rounded-xl text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                                    placeholder="you@example.com"
                                />
                            </div>
                            {errors.email && (
                                <p className="mt-1.5 text-xs text-red-400">{errors.email.message}</p>
                            )}
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm text-dark-400 mb-1.5 font-medium">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-dark-500" />
                                <input
                                    {...register('password')}
                                    type={showPassword ? 'text' : 'password'}
                                    className="w-full pl-11 pr-12 py-3 bg-dark-800/50 border border-dark-700 rounded-xl text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                                    placeholder="••••••••"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-dark-500 hover:text-dark-300 transition-colors"
                                >
                                    {showPassword ? (
                                        <EyeOff className="w-4.5 h-4.5" />
                                    ) : (
                                        <Eye className="w-4.5 h-4.5" />
                                    )}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="mt-1.5 text-xs text-red-400">{errors.password.message}</p>
                            )}
                            {isRegister && !errors.password && (
                                <p className="mt-1.5 text-xs text-dark-500">
                                    Min 8 characters, 1 uppercase letter, 1 number
                                </p>
                            )}
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex items-center justify-center gap-2 py-3.5 mt-2 bg-gradient-to-r from-primary-600 to-purple-600 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5 active:translate-y-0"
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

                    {/* Toggle Auth Mode */}
                    <p className="text-center text-sm text-dark-400 mt-8">
                        {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                        <button
                            onClick={toggleMode}
                            className="text-primary-400 hover:text-primary-300 font-semibold transition-colors hover:underline underline-offset-2"
                        >
                            {isRegister ? 'Sign in' : 'Create one'}
                        </button>
                    </p>

                    {/* Footer */}
                    <p className="text-center text-xs text-dark-600 mt-6">
                        By continuing, you agree to our{' '}
                        <a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">
                            Terms of Service
                        </a>{' '}
                        and{' '}
                        <a href="#" className="text-dark-400 hover:text-primary-400 transition-colors">
                            Privacy Policy
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
}
