import client from './client';

export const authAPI = {
    login: (email, password) =>
        client.post('/auth/login', { email, password }),

    register: (email, fullName, password) =>
        client.post('/auth/register', { email, full_name: fullName, password }),

    googleAuth: (token) =>
        client.post('/auth/google', { token }),

    getMe: () =>
        client.get('/auth/me'),
};
