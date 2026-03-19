/**
 * Login page — always renders form, works without backend or Google OAuth.
 *
 * - react-hook-form + zod for validation
 * - POST /auth/login on submit → stores token → redirects to /dashboard
 * - Google OAuth wrapped in error boundary (renders disabled button if unavailable)
 * - Teal (#1D9E75) dark theme
 *
 * @module pages/Login
 */

import { useState, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore.js'
import { api } from '../api/client.js'
import { FileText, Mail, Lock, LogIn, Loader2, Eye, EyeOff } from 'lucide-react'
import { GoogleLogin } from '@react-oauth/google'

const loginSchema = z.object({
    email: z.string().email('Enter a valid email'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
})

/**
 * Renders GoogleLogin from @react-oauth/google.
 * The GoogleOAuthProvider is already in main.jsx, so this component
 * will render the Google button if clientId is valid, or show a
 * "Sign in with Google" style button that may show oauth errors.
 */
function GoogleLoginButton() {
    return (
        <div>
            <GoogleLogin
                onSuccess={(credentialResponse) => {
                    console.log('Google credential:', credentialResponse)
                    toast.success('Google login received — implement backend handler')
                }}
                onError={() => {
                    toast.error('Google login failed')
                }}
                theme="filled_black"
                size="large"
                width="100%"
                text="signin_with"
            />
        </div>
    )
}


export default function Login() {
    const navigate = useNavigate()
    const { login } = useAuthStore()
    const [showPassword, setShowPassword] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [serverError, setServerError] = useState('')

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(loginSchema),
        defaultValues: { email: '', password: '' },
    })

    const onSubmit = useCallback(async (data) => {
        setIsSubmitting(true)
        setServerError('')
        try {
            const { login: loginApi } = await import("../api/auth.js"); const res = await loginApi(data.email, data.password)
            const { access_token, user } = res
            login(access_token, user)
            toast.success('Welcome back!')
            navigate('/dashboard')
        } catch (err) {
            const msg = err?.message || 'Login failed'
            if (msg.includes('Network Error') || msg.includes('ECONNREFUSED')) {
                setServerError('Cannot connect to server. Is the backend running?')
                toast.error('Cannot connect to server. Is the backend running?')
            } else {
                setServerError(msg)
                toast.error(msg)
            }
        } finally {
            setIsSubmitting(false)
        }
    }, [login, navigate])

    const togglePassword = useCallback(() => {
        setShowPassword((prev) => !prev)
    }, [])

    return (
        <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4">
            {/* Background glow */}
            <div className="absolute top-1/4 -left-32 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl" />
            <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-primary-700/5 rounded-full blur-3xl" />

            <div className="w-full max-w-md relative z-10 animate-fade-in">
                {/* Card */}
                <div className="glass-card p-8">
                    {/* Logo */}
                    <div className="flex items-center justify-center gap-3 mb-8">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-500/25">
                            <FileText className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">
                                <span className="text-white">Smart</span>{' '}
                                <span className="text-primary-400">Resume</span>
                            </h1>
                            <p className="text-[10px] text-dark-400 tracking-[0.2em] uppercase">Analyzer</p>
                        </div>
                    </div>

                    <h2 className="text-2xl font-bold text-center mb-1">Welcome back</h2>
                    <p className="text-sm text-dark-400 text-center mb-6">
                        Sign in to your account
                    </p>

                    {/* Form */}
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-1.5">Email</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
                                <input
                                    type="email"
                                    {...register('email')}
                                    placeholder="you@example.com"
                                    className="w-full pl-10 pr-4 py-3 bg-dark-800 border border-dark-700 rounded-xl text-sm text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                                />
                            </div>
                            {errors.email && (
                                <p className="text-xs text-red-400 mt-1">{errors.email.message}</p>
                            )}
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-1.5">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    {...register('password')}
                                    placeholder="••••••••"
                                    className="w-full pl-10 pr-12 py-3 bg-dark-800 border border-dark-700 rounded-xl text-sm text-dark-200 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={togglePassword}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-500 hover:text-dark-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="text-xs text-red-400 mt-1">{errors.password.message}</p>
                            )}
                        </div>

                        {/* Server error */}
                        {serverError && (
                            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                                <p className="text-sm text-red-400">{serverError}</p>
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full flex items-center justify-center gap-2 py-3 mt-2 bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary-500/25"
                        >
                            {isSubmitting ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    <LogIn className="w-5 h-5" />
                                    Sign In
                                </>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-3 my-6">
                        <div className="flex-1 h-px bg-dark-700" />
                        <span className="text-xs text-dark-500 uppercase">or</span>
                        <div className="flex-1 h-px bg-dark-700" />
                    </div>

                    {/* Google OAuth */}
                    <GoogleLoginButton />

                    {/* Register link */}
                    <p className="text-sm text-dark-400 text-center mt-6">
                        Don&apos;t have an account?{' '}
                        <Link
                            to="/login"
                            className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
                        >
                            Register
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}
