import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { toast } from '@/hooks/use-toast';

// API Client configuration
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

// API Error types
export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}

// Create API Client instance
export const createApiClient = (config: ApiClientConfig): AxiosInstance => {
  const client = axios.create({
    baseURL: config.baseURL,
    timeout: config.timeout || 30000,
    headers: {
      'Content-Type': 'application/json',
      ...config.headers,
    },
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add auth token if available
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const apiError: ApiError = {
        message: error.response?.data?.message || 'An unexpected error occurred',
        status: error.response?.status,
        code: error.code,
      };

      // Handle different error scenarios
      switch (apiError.status) {
        case 401:
          toast({
            title: 'Authentication Error',
            description: 'Please log in again',
            variant: 'destructive',
          });
          // Redirect to login
          window.location.href = '/';
          break;
        case 403:
          toast({
            title: 'Permission Denied',
            description: 'You do not have permission to perform this action',
            variant: 'destructive',
          });
          break;
        case 404:
          toast({
            title: 'Not Found',
            description: 'The requested resource was not found',
            variant: 'destructive',
          });
          break;
        default:
          toast({
            title: 'Error',
            description: apiError.message,
            variant: 'destructive',
          });
      }

      return Promise.reject(apiError);
    }
  );

  return client;
};

// Default API client instance
export const apiClient = createApiClient({
  baseURL: import.meta.env.VITE_API_URL || '/api',
});
