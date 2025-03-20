import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { apiClient } from './client';

// Generic type for API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Generic GET hook
export function useApiQuery<T>(
  endpoint: string,
  queryKey: string[],
  options?: Omit<UseQueryOptions<T, AxiosError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey,
    queryFn: async () => {
      const response = await apiClient.get<ApiResponse<T>>(endpoint);
      return response.data.data;
    },
    ...options,
  });
}

// Generic POST hook
export function useApiMutation<T, V>(
  endpoint: string,
  options?: Omit<UseMutationOptions<T, AxiosError, V>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: async (variables: V) => {
      const response = await apiClient.post<ApiResponse<T>>(endpoint, variables);
      return response.data.data;
    },
    ...options,
  });
}

// Generic PUT hook
export function useApiPut<T, V>(
  endpoint: string,
  options?: Omit<UseMutationOptions<T, AxiosError, V>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: async (variables: V) => {
      const response = await apiClient.put<ApiResponse<T>>(endpoint, variables);
      return response.data.data;
    },
    ...options,
  });
}

// Generic DELETE hook
export function useApiDelete<T>(
  endpoint: string,
  options?: Omit<UseMutationOptions<T, AxiosError, void>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.delete<ApiResponse<T>>(endpoint);
      return response.data.data;
    },
    ...options,
  });
}
