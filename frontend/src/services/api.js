/**
 * ThreatFusion API Service
 * Handles all API calls to the FastAPI backend
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getConfig = async () => {
    const response = await api.get('/api/config');
    return response.data;
};

export const enrichIndicator = async (indicator, timeout = 30) => {
    const response = await api.post('/api/enrich', {
        indicator,
        timeout,
    });
    return response.data;
};

export const checkHealth = async () => {
    const response = await api.get('/');
    return response.data;
};

export default api;
