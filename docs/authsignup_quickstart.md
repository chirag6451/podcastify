# AuthSignup Quick Start Guide

This guide provides the essential information needed to get started with the AuthSignup project quickly.

## Setup in 5 Minutes

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AuthSignup
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment**
   Create a `.env` file in the root directory:
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

## Project Structure at a Glance

```
AuthSignup/
├── client/                 # Frontend React application
├── server/                 # Backend Express application
├── shared/                 # Shared code and types
├── package.json            # Project dependencies
└── README.md               # Project documentation
```

## Available Pages

- **Dashboard** (`/dashboard`) - Main landing page
- **My Podcasts** (`/podcasts`) - Podcast management
- **YouTube Management** (`/youtube`) - YouTube integration
- **Drafts** (`/drafts`) - Draft management
- **Settings** (`/settings`) - Application settings
- **Profile** (`/profile`) - User profile

## Key Technologies

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: Express.js, TypeScript
- **Bundling**: Vite
- **Form Validation**: Zod
- **Database**: In-memory (dev) / PostgreSQL (prod)

## API Endpoints

Currently implemented:
- `POST /api/users` - Create a new user

## Development Workflow

1. **Make changes** to the frontend or backend code
2. **Test your changes** locally with the development server
3. **Build for production** using `npm run build`
4. **Deploy** the application using `npm start`

## Need More Information?

For more detailed information, refer to:
- [Complete Documentation](./authsignup_documentation.md)
- [Technical Guide](./authsignup_technical_guide.md)
- Project README.md
