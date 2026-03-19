/**
 * Admin API endpoints.
 *
 * @module api/admin
 */

import api from './client';

/**
 * Get platform-wide analytics.
 *
 * @returns {Promise<import('axios').AxiosResponse>} AdminAnalyticsResponse.
 */
export function getAnalytics() {
    return api.get('/admin/analytics');
}

/**
 * Get paginated user list.
 *
 * @param {number} [skip=0] - Records to skip.
 * @param {number} [limit=50] - Max records.
 * @returns {Promise<import('axios').AxiosResponse>} UserResponse[].
 */
export function getUsers(skip = 0, limit = 50) {
    return api.get('/admin/users', { params: { skip, limit } });
}

/**
 * Get all analyses (admin view).
 *
 * @returns {Promise<import('axios').AxiosResponse>} AnalysisSummary[].
 */
export function getAnalyses() {
    return api.get('/admin/analyses');
}
