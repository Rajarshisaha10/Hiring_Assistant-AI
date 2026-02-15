import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const authAPI = {
    adminLogin: (credentials) => api.post('/auth/admin', credentials),
};

export const applicantAPI = {
    submitApplication: (formData) => api.post('/applicant/submit', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    getApplicant: (id) => api.get(`/applicant/${id}`),
    getCodingQuestions: (id) => api.get(`/applicant/${id}/coding`),
    submitCodingAnswers: (id, answers) => api.post(`/applicant/${id}/coding`, { answers }),
    getHRQuestions: (id) => api.get(`/applicant/${id}/hr`),
    submitHRAnswers: (id, answers) => api.post(`/applicant/${id}/hr`, { answers }),
};

export const dashboardAPI = {
    getStats: () => api.get('/dashboard/stats'),
    getCandidates: () => api.get('/candidates'),
    getCandidate: (id) => api.get(`/candidate/${id}`),
    getAssessments: () => api.get('/assessments'),
    getJobs: () => api.get('/jobs'),
};

export default api;
