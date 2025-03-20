# AuthSignup Technical Guide

## Development Setup

### Local Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AuthSignup
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   PORT=3001
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   ```
   http://localhost:3001
   ```

## Architecture Overview

The AuthSignup project follows a modern web application architecture:

- **Frontend**: React with TypeScript
- **Backend**: Express.js with TypeScript
- **Data Storage**: In-memory storage (development) / PostgreSQL (production)
- **API**: RESTful API endpoints
- **Styling**: Tailwind CSS
- **Bundling**: Vite

## Frontend Implementation

### Component Structure

The frontend is organized into reusable components:

```
client/src/components/
├── layout.tsx        # Main layout with sidebar
├── Dashboard.js      # Dashboard component
├── ui/               # UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   └── ...
└── ...
```

### Routing Implementation

The application uses client-side routing:

```typescript
// Example routing implementation
export function App() {
  return (
    <Router>
      <Layout>
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/podcasts" component={PodcastList} />
        <Route path="/settings" component={Settings} />
        {/* Other routes */}
      </Layout>
    </Router>
  );
}
```

### State Management

The application uses React hooks for state management:

```typescript
// Example state management
function PodcastList() {
  const [podcasts, setPodcasts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Fetch podcasts from API
    async function fetchPodcasts() {
      try {
        const response = await apiClient.get('/api/podcasts');
        setPodcasts(response.data);
      } catch (error) {
        console.error('Failed to fetch podcasts:', error);
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchPodcasts();
  }, []);
  
  // Component rendering
}
```

## Backend Implementation

### Server Setup

The Express server is configured in `server/index.ts`:

```typescript
import express from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic } from "./vite";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Register API routes
(async () => {
  const server = await registerRoutes(app);
  
  // Setup Vite in development
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }
  
  // Start server
  const port = process.env.PORT ? parseInt(process.env.PORT) : 3001;
  server.listen(port, () => {
    console.log(`Server running on port ${port}`);
  });
})();
```

### API Routes

API routes are defined in `server/routes.ts`:

```typescript
import type { Express } from "express";
import { createServer } from "http";
import { storage } from "./storage";
import { insertUserSchema } from "@shared/schema";

export async function registerRoutes(app: Express) {
  // User creation endpoint
  app.post("/api/users", async (req, res) => {
    try {
      const userData = insertUserSchema.parse(req.body);
      const existingUser = await storage.getUserByEmail(userData.email);
      
      if (existingUser) {
        return res.status(400).json({ message: "Email already registered" });
      }

      const user = await storage.createUser(userData);
      res.status(201).json(user);
    } catch (error) {
      res.status(400).json({ 
        message: error instanceof Error ? error.message : "Invalid request" 
      });
    }
  });

  // Additional API endpoints would be defined here
  
  return createServer(app);
}
```

### Data Storage

The application uses a memory-based storage implementation in `server/storage.ts`:

```typescript
import { users, type User, type InsertUser } from "@shared/schema";

export interface IStorage {
  createUser(user: InsertUser): Promise<User>;
  getUserByEmail(email: string): Promise<User | undefined>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private currentId: number;

  constructor() {
    this.users = new Map();
    this.currentId = 1;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentId++;
    const user = { id, ...insertUser };
    this.users.set(id, user);
    return user;
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.email === email
    );
  }
}

export const storage = new MemStorage();
```

## Data Schema

The application uses Zod for schema validation and TypeScript for type safety:

```typescript
// Example schema definition in shared/schema.ts
import { pgTable, text, serial } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  // Other fields...
});

export const insertUserSchema = createInsertSchema(users)
  .omit({ id: true })
  .extend({
    email: z.string().email("Invalid email address"),
    // Additional validation...
  });

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
```

## Available Pages

### Dashboard

The Dashboard page (`components/Dashboard.js`) serves as the main landing page after authentication:

- Displays summary of user's podcasts
- Shows recent activity
- Provides quick access to common actions

### My Podcasts

The My Podcasts page allows users to:

- View a list of their podcasts
- Create new podcasts
- Edit existing podcasts
- Delete podcasts
- View podcast analytics

### Settings

The Settings page allows users to configure application preferences:

- Account settings
- Notification preferences
- API integrations
- Theme settings

## API Integration Details

### Available Endpoints

The current implementation includes the following API endpoints:

1. **User Management**
   - `POST /api/users` - Create a new user

### Planned Endpoints

The following endpoints are planned for future implementation:

1. **Podcast Management**
   - `GET /api/podcasts` - List all podcasts
   - `GET /api/podcasts/:id` - Get podcast details
   - `POST /api/podcasts` - Create a new podcast
   - `PUT /api/podcasts/:id` - Update podcast details
   - `DELETE /api/podcasts/:id` - Delete a podcast

2. **Episode Management**
   - `GET /api/podcasts/:id/episodes` - List all episodes for a podcast
   - `POST /api/podcasts/:id/episodes` - Create a new episode
   - `PUT /api/podcasts/:id/episodes/:episodeId` - Update episode details
   - `DELETE /api/podcasts/:id/episodes/:episodeId` - Delete an episode

## Deployment

### Production Build

To build the application for production:

```bash
npm run build
```

This will:
1. Bundle the React frontend with Vite
2. Compile the TypeScript server code with esbuild
3. Output the production-ready files to the `dist` directory

### Starting the Production Server

```bash
npm start
```

This runs the application in production mode using the compiled files in the `dist` directory.

## Testing

Currently, the application does not have automated tests implemented. Future development should include:

- Unit tests for components and utility functions
- Integration tests for API endpoints
- End-to-end tests for critical user flows

## Future Development

### Planned Features

1. **Authentication System**
   - User registration and login
   - OAuth integration (Google, Facebook, etc.)
   - Password reset functionality

2. **Podcast Analytics**
   - Listener statistics
   - Episode performance metrics
   - Audience demographics

3. **Content Distribution**
   - Integration with podcast platforms (Spotify, Apple Podcasts, etc.)
   - RSS feed generation
   - Social media sharing

4. **Advanced Editing Tools**
   - Audio editing capabilities
   - Transcript generation and editing
   - Cover art creation tools

## Troubleshooting

### Common Issues and Solutions

1. **Port Conflicts**
   - Error: `EADDRINUSE: address already in use`
   - Solution: Change the port in the `.env` file

2. **Dependency Issues**
   - Error: Module not found
   - Solution: Run `npm install` to ensure all dependencies are installed

3. **TypeScript Errors**
   - Solution: Run `npm run tsc` to check for type errors
