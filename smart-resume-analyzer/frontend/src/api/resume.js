/**
 * Resume API endpoints.
 *
 * @module api/resume
 */

import api from './client';

/**
 * Upload a resume PDF file.
 *
 * @param {File} file - The PDF file to upload.
 * @returns {Promise<import('axios').AxiosResponse>} Response with ResumeUploadResponse.
 */
export function uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
}

/**
 * Get all resumes for the current user.
 *
 * @returns {Promise<import('axios').AxiosResponse>} Response with ResumeResponse[].
 */
export function getMyResumes() {
    return api.get('/resume/');
}

/**
 * Delete a resume by ID.
 *
 * @param {string} id - Resume UUID.
 * @returns {Promise<import('axios').AxiosResponse>} 204 No Content.
 */
export function deleteResume(id) {
    return api.delete(`/resume/${id}`);
}
