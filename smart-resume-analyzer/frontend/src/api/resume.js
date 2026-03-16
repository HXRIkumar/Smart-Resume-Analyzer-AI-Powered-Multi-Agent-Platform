import client from './client';

export const resumeAPI = {
    upload: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return client.post('/resume/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    list: (skip = 0, limit = 20) =>
        client.get('/resume/', { params: { skip, limit } }),

    getById: (id) =>
        client.get(`/resume/${id}`),

    delete: (id) =>
        client.delete(`/resume/${id}`),
};
