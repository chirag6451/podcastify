import { useApiQuery, useApiMutation, useApiPut, useApiDelete } from '../hooks';
import type { PodcastFormData } from '@shared/schema';

// Query key factory
const podcastKeys = {
  all: ['podcasts'] as const,
  list: () => [...podcastKeys.all, 'list'] as const,
  detail: (id: string) => [...podcastKeys.all, 'detail', id] as const,
  episodes: (id: string) => [...podcastKeys.all, 'episodes', id] as const,
};

// Hook to fetch all podcasts
export function usePodcasts() {
  return useApiQuery<PodcastFormData[]>('/podcasts', podcastKeys.list());
}

// Hook to fetch a single podcast
export function usePodcast(id: string) {
  return useApiQuery<PodcastFormData>(
    `/podcasts/${id}`,
    podcastKeys.detail(id),
    {
      enabled: !!id,
    }
  );
}

// Hook to create a new podcast
export function useCreatePodcast() {
  return useApiMutation<PodcastFormData, PodcastFormData>(
    '/podcasts',
    {
      onSuccess: () => {
        // Invalidate the podcasts list query
        // queryClient.invalidateQueries(podcastKeys.list());
      },
    }
  );
}

// Hook to update a podcast
export function useUpdatePodcast(id: string) {
  return useApiPut<PodcastFormData, PodcastFormData>(
    `/podcasts/${id}`,
    {
      onSuccess: () => {
        // Invalidate both the list and the detail queries
        // queryClient.invalidateQueries(podcastKeys.list());
        // queryClient.invalidateQueries(podcastKeys.detail(id));
      },
    }
  );
}

// Hook to delete a podcast
export function useDeletePodcast(id: string) {
  return useApiDelete<void>(
    `/podcasts/${id}`,
    {
      onSuccess: () => {
        // Invalidate the podcasts list query
        // queryClient.invalidateQueries(podcastKeys.list());
      },
    }
  );
}
