/**
 * Analysis API endpoints.
 *
 * @module api/analysis
 */

import api from './client';

/**
 * Run AI analysis on a resume.
 *
 * @param {string} resumeId - Resume UUID.
 * @param {string|null} [jobId=null] - Optional job description UUID.
 * @returns {Promise<import('axios').AxiosResponse>} 202 with AnalysisResponse.
 */
export function runAnalysis(resumeId, jobId = null) {
    return api.post('/analysis/run', {
        resume_id: resumeId,
        job_id: jobId,
    });
}

/**
 * Get a single analysis result.
 *
 * @param {string} id - Analysis UUID.
 * @returns {Promise<import('axios').AxiosResponse>} Response with AnalysisResponse.
 */
export function getAnalysisResult(id) {
    return api.get(`/analysis/result/${id}`);
}

/**
 * Get all analyses for the current user.
 *
 * @returns {Promise<import('axios').AxiosResponse>} Response with AnalysisSummary[].
 */
export function getMyAnalyses() {
    return api.get('/analysis/my');
}
