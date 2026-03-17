/**
 * Authentication API module.
 *
 * Provides async functions for all auth-related HTTP calls:
 * register, login, Google OAuth login, profile fetch, and token refresh.
 *
 * @module api/auth
 */

import client from './client';

/**
 * Register a new user account.
 *
 * @async
 * @param {{ email: string, password: string, full_name: string }} data - Registration payload.
 * @returns {Promise<import('axios').AxiosResponse>} Response with TokenResponse (access_token, user).
 * @throws {Error} 409 if email is already registered, 422 on validation failure.
 */
export async function register(data) {
    try {
        const response = await client.post('/auth/register', data);
        return response;
    } catch (error) {
        const message = error.response?.data?.detail || 'Registration failed. Please try again.';
        throw new Error(message);
    }
}

/**
 * Login with email and password.
 *
 * @async
 * @param {string} email - User's email address.
 * @param {string} password - User's plaintext password.
 * @returns {Promise<import('axios').AxiosResponse>} Response with TokenResponse (access_token, refresh_token, user).
 * @throws {Error} 401 if credentials are invalid.
 */
export async function login(email, password) {
    try {
        const response = await client.post('/auth/login/json', { email, password });
        return response;
    } catch (error) {
        const message = error.response?.data?.detail || 'Invalid email or password.';
        throw new Error(message);
    }
}

/**
 * Authenticate via Google OAuth authorization code.
 *
 * @async
 * @param {string} code - Authorization code from Google OAuth flow.
 * @param {string} [redirectUri=window.location.origin] - OAuth redirect URI.
 * @returns {Promise<import('axios').AxiosResponse>} Response with TokenResponse.
 * @throws {Error} 401 if Google authentication fails.
 */
export async function googleLogin(code, redirectUri = window.location.origin) {
    try {
        const response = await client.post('/auth/google-login', {
            code,
            redirect_uri: redirectUri,
        });
        return response;
    } catch (error) {
        const message = error.response?.data?.detail || 'Google authentication failed.';
        throw new Error(message);
    }
}

/**
 * Get the currently authenticated user's profile.
 *
 * @async
 * @returns {Promise<import('axios').AxiosResponse>} Response with UserResponse.
 * @throws {Error} 401 if not authenticated.
 */
export async function getMe() {
    try {
        const response = await client.get('/auth/me');
        return response;
    } catch (error) {
        const message = error.response?.data?.detail || 'Failed to fetch user profile.';
        throw new Error(message);
    }
}

/**
 * Refresh the access token using a valid refresh token.
 *
 * @async
 * @param {string} refreshToken - The JWT refresh token.
 * @returns {Promise<import('axios').AxiosResponse>} Response with new TokenResponse.
 * @throws {Error} 401 if refresh token is expired or invalid.
 */
export async function refreshToken(refreshToken) {
    try {
        const response = await client.post('/auth/refresh', {
            refresh_token: refreshToken,
        });
        return response;
    } catch (error) {
        const message = error.response?.data?.detail || 'Token refresh failed. Please login again.';
        throw new Error(message);
    }
}

/**
 * Grouped auth API object for convenience imports.
 */
export const authAPI = {
    register,
    login,
    googleLogin,
    getMe,
    refreshToken,
};

export default authAPI;
