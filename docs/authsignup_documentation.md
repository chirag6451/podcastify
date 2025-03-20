# AuthSignup Project Documentation

## Overview

The AuthSignup project is a React-based web application with a Node.js/Express backend that provides user authentication, podcast management, and content creation functionality. It features a modern UI with a sidebar navigation component and various pages for managing podcasts and user settings.

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Project Structure](#project-structure)
3. [Pages and Components](#pages-and-components)
4. [API Integration](#api-integration)
5. [Database Schema](#database-schema)
6. [Navigation Structure](#navigation-structure)
7. [Troubleshooting](#troubleshooting)

## Setup Instructions

### Prerequisites

- Node.js (v16+)
- npm or yarn

### Installation Steps

1. **Clone the repository** (if not already done)

2. **Install dependencies**
   ```bash
   cd /path/to/AuthSignup
   npm install
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory with the following variables:
   ```
   PORT=3001
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:3001
   ```

### Production Deployment

To build the application for production:

```bash
npm run build
npm start
```

## Project Structure

```
AuthSignup/
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── layout.tsx  # Main layout with sidebar navigation
│   │   │   └── ui/         # UI components
│   │   ├── lib/            # Utility functions and API clients
│   │   │   └── api/        # API integration
│   │   └── pages/          # Application pages
│   └── index.html          # HTML entry point
├── server/                 # Backend Express application
│   ├── index.ts            # Server entry point
│   ├── routes.ts           # API route definitions
│   ├── storage.ts          # Data storage implementation
│   └── vite.ts             # Vite configuration for development
├── shared/                 # Shared code between client and server
│   └── schema.ts           # Data schemas and types
├── package.json            # Project dependencies and scripts
└── README.md               # Project documentation
```

## Pages and Components

### Main Pages

The application includes the following pages:

1. **Dashboard** - Main landing page after authentication
2. **My Podcasts** - List of user's podcasts with management options
3. **YouTube Management** - Integration with YouTube for publishing
4. **Drafts** - Manage podcast drafts
5. **Notifications** - User notifications
6. **Settings** - Application settings
7. **Profile** - User profile management
8. **Subscription** - Manage subscription plans

### Key Components

#### Layout Component (`layout.tsx`)

The main layout component includes:
- Fixed sidebar navigation
- Main content area
- Responsive design

```tsx
export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen">
        {children}
      </main>
    </div>
  );
}
```

#### Sidebar Component

The sidebar navigation component includes:
- Project title/logo
- Navigation links with icons
- Active state highlighting
- Profile section

```tsx
function Sidebar() {
  const [location, setLocation] = useLocation();

  const isActive = (path: string) => {
    return location.startsWith(path);
  };

  return (
    <div className="w-64 h-screen bg-sidebar border-r border-border flex flex-col fixed">
      <div className="p-4">
        <Link href="/dashboard">
          <a className="text-xl font-bold text-primary">Podcast Studio</a>
        </Link>
      </div>
      <nav className="flex-1 px-2 py-4 space-y-1">
        <Button 
          variant={isActive("/dashboard") ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => setLocation("/dashboard")}
        >
          <Home className="mr-2 h-4 w-4" />
          Dashboard
        </Button>
        {/* Other navigation items */}
      </nav>
    </div>
  );
}
```

## API Integration

The application uses a custom API client built with Axios for communicating with the backend. The API integration is structured as follows:

### API Client Setup

Located in `client/src/lib/api/client.ts`, the API client provides:
- Automatic error handling
- Authentication token management
- Response interceptors

### API Endpoints

The backend provides the following API endpoints:

1. **User Management**
   - `POST /api/users` - Create a new user

### API Hooks

The application uses custom hooks for API interactions:

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

## Database Schema

The application uses a memory-based storage in development but is designed to work with PostgreSQL in production. The database schema includes:

### Users Table

```typescript
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  businessName: text("business_name").notNull(),
  businessEmail: text("business_email").notNull(),
  businessDetails: text("business_details").notNull(),
  businessType: text("business_type").notNull(),
  businessWebsite: text("business_website"),
  targetAudience: text("target_audience").notNull(),
});
```

### Podcast Schema

The application includes schemas for podcasts and episodes:

```typescript
export const podcastSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(50, "Description must be at least 50 characters"),
  coverImage: z.string().url("Invalid cover image URL").optional(),
  categories: z.array(z.enum(podcastCategories)).min(1, "Select at least one category"),
  // Additional fields...
});
```

## Navigation Structure

The application uses the Wouter library for routing with the following structure:

```
/                   - Landing page/Login
/dashboard          - Main dashboard
/podcasts           - Podcast management
/youtube            - YouTube integration
/drafts             - Draft management
/notifications      - User notifications
/settings           - Application settings
/profile            - User profile
/profile?tab=subscription - Subscription management
```

## Troubleshooting

### Common Issues

1. **Port Binding Issues**
   - If you encounter `ENOTSUP` or `EADDRINUSE` errors, try changing the port in the `.env` file.

2. **Database Connection Issues**
   - The application uses in-memory storage by default. For production, configure a PostgreSQL connection.

3. **API Request Failures**
   - Check browser console for detailed error messages
   - Verify that the server is running
   - Check authentication status

### Debugging

The server includes logging for API requests:

```typescript
res.on("finish", () => {
  const duration = Date.now() - start;
  if (path.startsWith("/api")) {
    let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
    if (capturedJsonResponse) {
      logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
    }
    log(logLine);
  }
});
```

## Conclusion

The AuthSignup project provides a solid foundation for building a podcast management application with user authentication and content creation capabilities. The modern UI with sidebar navigation offers an intuitive user experience, while the API integration allows for seamless communication with the backend.
