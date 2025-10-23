import axios from 'axios';
import {ChatRequest, ChatResponse, Trip} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';


const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  health: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/api/chat/message', data);
    return response.data;
  },

  createTrip: async (tripData: Partial<Trip>): Promise<Trip> => {
    const response = await apiClient.post('/api/trips/', tripData);
    return response.data;
  },

  getTrip: async (tripId: number): Promise<Trip> => {
    const response = await apiClient.get(`/api/trips/${tripId}`);
    return response.data;
  },

  getAllTrips: async (): Promise<Trip[]> => {
    const response = await apiClient.get('/api/trips/');
    return response.data;
  },
};
