/**
 * Zustand analysis store — manages resume upload, AI analysis orchestration,
 * polling, and derived selectors.
 *
 * State: currentAnalysis, analyses[], resumes[], isAnalyzing, analysisProgress, error
 * Actions: uploadAndAnalyze, fetchAnalysis, fetchMyAnalyses, pollAnalysis
 * Derived: hasAnalysis, latestScore, latestCareer
 *
 * @module store/analysisStore
 */

import { create } from 'zustand';
import { uploadResume, getMyResumes, deleteResume } from '../api/resume';
import { runAnalysis, getAnalysisResult, getMyAnalyses } from '../api/analysis';

export const useAnalysisStore = create((set, get) => ({
    // ─── State ──────────────────────────────────────────────────────────
    currentAnalysis: null,
    analyses: [],
    resumes: [],
    isLoading: false,
    isAnalyzing: false,
    analysisProgress: '',
    error: null,

    // ─── Derived ────────────────────────────────────────────────────────
    /** @returns {boolean} */
    get hasAnalysis() {
        return get().analyses.length > 0;
    },
    /** @returns {number} */
    get latestScore() {
        const a = get().analyses[0];
        return a?.resume_score ?? 0;
    },
    /** @returns {string} */
    get latestCareer() {
        const a = get().analyses[0];
        const preds = a?.career_predictions?.predictions;
        return preds?.[0]?.role ?? '';
    },

    // ─── Resume Actions ─────────────────────────────────────────────────

    /**
     * Fetch all user resumes.
     * @async
     */
    fetchResumes: async () => {
        set({ isLoading: true });
        try {
            const { data } = await getMyResumes();
            set({ resumes: Array.isArray(data) ? data : [], isLoading: false });
        } catch (err) {
            set({ error: err.message, isLoading: false });
        }
    },

    /**
     * Delete a resume by ID.
     * @async
     * @param {string} id - Resume UUID.
     */
    removeResume: async (id) => {
        try {
            await deleteResume(id);
            set((s) => ({ resumes: s.resumes.filter((r) => r.id !== id) }));
        } catch (err) {
            set({ error: err.message });
        }
    },

    // ─── Analysis Actions ───────────────────────────────────────────────

    /**
     * Upload a resume file and immediately run AI analysis.
     *
     * @async
     * @param {File} file - PDF file.
     * @param {string|null} [jobId=null] - Optional job description UUID.
     * @returns {object} The analysis result.
     */
    uploadAndAnalyze: async (file, jobId = null) => {
        set({ isAnalyzing: true, analysisProgress: 'Uploading resume...', error: null });
        try {
            // 1. Upload
            const { data: resume } = await uploadResume(file);
            set({ analysisProgress: 'Running AI pipeline...' });

            // 2. Trigger analysis
            const { data: analysis } = await runAnalysis(resume.id, jobId);
            set({
                currentAnalysis: analysis,
                isAnalyzing: false,
                analysisProgress: 'Complete',
            });

            // Refresh lists
            get().fetchResumes();
            get().fetchMyAnalyses();

            return analysis;
        } catch (err) {
            set({
                error: err.message || 'Analysis failed',
                isAnalyzing: false,
                analysisProgress: '',
            });
            throw err;
        }
    },

    /**
     * Fetch a single analysis result by ID.
     * @async
     * @param {string} id - Analysis UUID.
     */
    fetchAnalysis: async (id) => {
        set({ isLoading: true });
        try {
            const { data } = await getAnalysisResult(id);
            set({ currentAnalysis: data, isLoading: false });
        } catch (err) {
            set({ error: err.message, isLoading: false });
        }
    },

    /**
     * Fetch all analyses for the current user.
     * @async
     */
    fetchMyAnalyses: async () => {
        set({ isLoading: true });
        try {
            const { data } = await getMyAnalyses();
            set({ analyses: Array.isArray(data) ? data : [], isLoading: false });
        } catch (err) {
            set({ error: err.message, isLoading: false });
        }
    },

    /**
     * Poll an analysis result every 2 seconds until it resolves.
     *
     * @param {string} id - Analysis UUID.
     * @returns {() => void} Cleanup function to stop polling.
     */
    pollAnalysis: (id) => {
        const intervalId = setInterval(async () => {
            try {
                const { data } = await getAnalysisResult(id);
                set({ currentAnalysis: data });

                // Stop polling if completed or has a score
                if (data.resume_score > 0) {
                    clearInterval(intervalId);
                    set({ isAnalyzing: false, analysisProgress: 'Complete' });
                    get().fetchMyAnalyses();
                }
            } catch {
                clearInterval(intervalId);
                set({ isAnalyzing: false, error: 'Polling failed' });
            }
        }, 2000);

        return () => clearInterval(intervalId);
    },

    clearError: () => set({ error: null }),
}));
