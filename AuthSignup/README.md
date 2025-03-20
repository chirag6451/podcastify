# Podcast Studio Documentation

## Project Structure

```
client/
  ├── src/
  │   ├── components/     # Reusable UI components
  │   ├── lib/
  │   │   └── api/       # Centralized API management
  │   │       ├── client.ts    # Base API client configuration
  │   │       ├── hooks.ts     # Generic API hooks
  │   │       └── services/    # Service-specific API hooks
  │   └── pages/         # Application pages/routes
```

## API Integration

### API Client Setup (`lib/api/client.ts`)

The API client is built using Axios with the following features:
- Automatic error handling
- Authentication token management
- Response interceptors for consistent error handling
- Toast notifications for API errors

```typescript
// Example API client usage
import { apiClient } from '@/lib/api/client';

// The client automatically handles:
// - Adding auth tokens
// - Error handling
// - Toast notifications
const response = await apiClient.get('/endpoint');
```

### Generic API Hooks (`lib/api/hooks.ts`)

We provide type-safe hooks for common API operations:

```typescript
// Query hook for GET requests
const { data, isLoading } = useApiQuery<ResponseType>(
  '/endpoint',
  ['queryKey']
);

// Mutation hook for POST requests
const { mutate } = useApiMutation<ResponseType, RequestType>(
  '/endpoint'
);
```

### Service-Specific Hooks

Example of podcast service implementation (`lib/api/services/podcast.ts`):

```typescript
// Fetch all podcasts
const { data: podcasts } = usePodcasts();

// Fetch single podcast
const { data: podcast } = usePodcast(id);

// Create new podcast
const createPodcast = useCreatePodcast();
createPodcast.mutate(podcastData);
```

## Page Components

### Profile Page (`pages/profile.tsx`)

The profile page implements:
- Personal details editing
- Password management
- Credit system management
- Subscription handling

Usage example:
```typescript
import Profile from '@/pages/profile';

// The component handles its own routing
<Route path="/profile">
  <Profile />
</Route>
```

### Podcast Settings (`pages/podcast-settings.tsx`)

Implements a multi-step form for podcast management:
1. Basic Information
2. Media & Style
3. Contact & Social

Features:
- Form validation with Zod
- API integration with React Query
- File upload handling
- Real-time preview

Usage:
```typescript
import PodcastSettings from '@/pages/podcast-settings';

// Create new podcast
<PodcastSettings />

// Edit existing podcast
<PodcastSettings podcastId="123" />
```

## Error Handling

The API client automatically handles common error scenarios:
- 401: Unauthorized - Redirects to login
- 403: Forbidden - Shows permission denied message
- 404: Not Found - Shows resource not found message
- Network errors: Shows connection error message

## Best Practices

1. **API Calls**
   - Always use the provided hooks instead of direct fetch/axios calls
   - Use proper type definitions for request/response data
   - Handle loading and error states

```typescript
// Good
const { data, isLoading } = useApiQuery<PodcastData>('/podcasts', ['podcasts']);
if (isLoading) return <Loading />;

// Avoid
const [data, setData] = useState();
useEffect(() => {
  fetch('/podcasts').then(res => setData(res.json()));
}, []);
```

2. **Form Handling**
   - Use react-hook-form with zod validation
   - Implement proper error handling
   - Show loading states during submission

```typescript
const form = useForm<FormData>({
  resolver: zodResolver(schema)
});

// Handle submission
const handleSubmit = async (data: FormData) => {
  try {
    await submitData(data);
    toast.success('Success');
  } catch (error) {
    toast.error('Failed to submit');
  }
};
```

3. **Component Organization**
   - Keep components focused and single-responsibility
   - Use proper TypeScript types
   - Implement proper prop validation
   - Use consistent naming conventions

## Adding New Features

1. Define types in `shared/schema.ts`
2. Create API service in `lib/api/services`
3. Implement UI components
4. Add routing in `App.tsx`
5. Test thoroughly with error cases

Example of adding a new feature:

```typescript
// 1. Define types
export interface NewFeatureData {
  id: string;
  name: string;
}

// 2. Create service
export function useNewFeature(id: string) {
  return useApiQuery<NewFeatureData>(
    `/feature/${id}`,
    ['features', id]
  );
}

// 3. Implement component
export function NewFeature({ id }: { id: string }) {
  const { data, isLoading } = useNewFeature(id);
  if (isLoading) return <Loading />;
  return <div>{data.name}</div>;
}
```
