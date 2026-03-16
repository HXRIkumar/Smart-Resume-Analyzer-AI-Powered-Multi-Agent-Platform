import { create } from 'zustand';
import { analysisAPI } from '../api/analysis';
import { resumeAPI } from '../api/resume';

export const useAnalysisStore = create((set, get) => ({
    analyses: [],
    currentAnalysis: null,
    summary: null,
    resumes: [],
    isLoading: false,
    isAnalyzing: false,
    error: null,

    // ─── Resumes ───
    fetchResumes: async () => {
        set({ isLoading: true });
        try {
            const { data } = await resumeAPI.list();
            set({ resumes: data.resumes, isLoading: false });
        } catch (err) {
            set({ error: err.message, isLoading: false });
        }
    },

    uploadResume: async (file) => {
        set({ isLoading: true });
        try {
            const { data } = await resumeAPI.upload(file);
            await get().fetchResumes();
            return data;
        } catch (err) {
            set({ error: err.message, isLoading: false });
            throw err;
        }
    },

    deleteResume: async (id) => {
        try {
            await resumeAPI.delete(id);
            set((state) => ({
                resumes: state.resumes.filter((r) => r.id !== id),
            }));
        } catch (err) {
            set({ error: err.message });
        }
    },

    // ─── Analyses ───
    fetchAnalyses: async () => {
        set({ isLoading: true });
        try {
            const { data } = await analysisAPI.list();
            set({ analyses: data.analyses, isLoading: false });
        } catch (err) {
            set({ error: err.message, isLoading: false });
        }
    },

    runAnalysis: async (resumeId, jobDescriptionId = null) => {
        set({ isAnalyzing: true });
        try {
            const { data } = await analysisAPI.run(resumeId, jobDescriptionId);
            set({ currentAnalysis: data, isAnalyzing: false });
            return data;
        } catch (err) {
            set({ error: err.message, isAnalyzing: false });
            throw err;
        }
    },

    fetchAnalysis: async (id) => {
        set({ isLoading: true });
        try {
            const { data } = await analysisAPI.getById(id);
            set({ currentAnalysis: data, isLoading: false });
        } catch (err) {
            set({ error: err.message, isLoading: false });
        }
    },

    fetchSummary: async () => {
        try {
            const { data } = await analysisAPI.getSummary();
            set({ summary: data });
        } catch (err) {
            set({ error: err.message });
        }
    },

    clearError: () => set({ error: null }),
}));
