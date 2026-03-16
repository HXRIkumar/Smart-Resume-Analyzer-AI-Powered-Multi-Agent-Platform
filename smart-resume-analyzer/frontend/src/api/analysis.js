import client from './client';

export const analysisAPI = {
    run: (resumeId, jobDescriptionId = null) =>
        client.post('/analysis/run', {
            resume_id: resumeId,
            job_description_id: jobDescriptionId,
        }),

    list: (skip = 0, limit = 20) =>
        client.get('/analysis/', { params: { skip, limit } }),

    getById: (id) =>
        client.get(`/analysis/${id}`),

    getSummary: () =>
        client.get('/analysis/summary'),
};
