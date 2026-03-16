import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAnalysisStore } from '../store/analysisStore';
import { Upload, FileText, Trash2, Zap, Loader2 } from 'lucide-react';

export default function AILab() {
    const navigate = useNavigate();
    const {
        resumes, fetchResumes, uploadResume, deleteResume,
        runAnalysis, isLoading, isAnalyzing,
    } = useAnalysisStore();
    const [selectedResume, setSelectedResume] = useState(null);

    useState(() => {
        fetchResumes();
    }, []);

    const onDrop = useCallback(
        async (acceptedFiles) => {
            const file = acceptedFiles[0];
            if (!file) return;
            if (file.type !== 'application/pdf') {
                toast.error('Only PDF files are accepted');
                return;
            }
            try {
                const data = await uploadResume(file);
                toast.success(`Uploaded: ${data.filename}`);
            } catch {
                toast.error('Upload failed');
            }
        },
        [uploadResume],
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
    });

    const handleAnalyze = async () => {
        if (!selectedResume) {
            toast.error('Select a resume first');
            return;
        }
        try {
            const result = await runAnalysis(selectedResume);
            toast.success('Analysis started!');
            navigate(`/analysis/${result.id}`);
        } catch {
            toast.error('Analysis failed');
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">AI Lab</h1>
                <p className="text-dark-400 mt-1">Upload resumes and run AI-powered analysis</p>
            </div>

            {/* Upload zone */}
            <div
                {...getRootProps()}
                className={`glass-card p-10 border-2 border-dashed cursor-pointer transition-all duration-300 text-center ${isDragActive
                        ? 'border-primary-500 bg-primary-500/5'
                        : 'border-dark-600 hover:border-primary-500/50'
                    }`}
            >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-dark-400 mx-auto mb-4" />
                <p className="text-lg font-medium">
                    {isDragActive ? 'Drop your PDF here' : 'Drag & drop a resume PDF'}
                </p>
                <p className="text-sm text-dark-400 mt-2">
                    or click to browse • Max 10MB • PDF only
                </p>
            </div>

            {/* Resume list */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4">Your Resumes</h3>
                {resumes.length === 0 ? (
                    <p className="text-sm text-dark-400 text-center py-6">
                        No resumes uploaded yet. Upload one above to get started!
                    </p>
                ) : (
                    <div className="space-y-3">
                        {resumes.map((resume) => (
                            <div
                                key={resume.id}
                                onClick={() => setSelectedResume(resume.id)}
                                className={`flex items-center justify-between p-4 rounded-lg cursor-pointer transition-all duration-200 ${selectedResume === resume.id
                                        ? 'bg-primary-600/10 border border-primary-500/30'
                                        : 'bg-dark-800/50 border border-transparent hover:bg-dark-800'
                                    }`}
                            >
                                <div className="flex items-center gap-3">
                                    <FileText className="w-5 h-5 text-primary-400" />
                                    <div>
                                        <p className="text-sm font-medium">{resume.filename}</p>
                                        <p className="text-xs text-dark-400">
                                            {(resume.file_size_bytes / 1024).toFixed(1)} KB •{' '}
                                            {new Date(resume.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        deleteResume(resume.id);
                                        toast.success('Deleted');
                                    }}
                                    className="p-2 text-dark-400 hover:text-red-400 transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Analyze button */}
            <button
                onClick={handleAnalyze}
                disabled={!selectedResume || isAnalyzing}
                className="w-full flex items-center justify-center gap-2 py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-purple-500 transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-primary-500/25 animate-pulse-glow"
            >
                {isAnalyzing ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Running AI Pipeline...
                    </>
                ) : (
                    <>
                        <Zap className="w-5 h-5" />
                        Analyze with AI Agents
                    </>
                )}
            </button>
        </div>
    );
}
