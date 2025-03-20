import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "./lib/auth";
import { Layout } from "./components/layout";
import Auth from "./pages/auth";
import Register from "./pages/register";
import PodcastSettings from "./pages/podcast-settings";
import Dashboard from "./pages/dashboard";
import EpisodeManager from "./pages/episode-manager";
import EpisodeForm from "./pages/episode-form";
import MyPodcasts from "./pages/my-podcasts";
import YouTube from "./pages/youtube";
import Drafts from "./pages/drafts";
import NotFound from "./pages/not-found";
import SettingsPage from "./pages/settings";
import Profile from "./pages/profile";

function Router() {
  return (
    <Switch>
      {/* Auth pages without sidebar */}
      <Route path="/" component={Auth} />
      <Route path="/register" component={Register} />

      {/* Pages with sidebar */}
      <Route path="/dashboard">
        <Layout>
          <Dashboard />
        </Layout>
      </Route>
      <Route path="/podcasts">
        <Layout>
          <MyPodcasts />
        </Layout>
      </Route>
      <Route path="/youtube">
        <Layout>
          <YouTube />
        </Layout>
      </Route>
      <Route path="/drafts">
        <Layout>
          <Drafts />
        </Layout>
      </Route>
      <Route path="/podcast-settings">
        <Layout>
          <PodcastSettings />
        </Layout>
      </Route>
      <Route path="/podcast/:id">
        <Layout>
          <EpisodeManager />
        </Layout>
      </Route>
      <Route path="/podcast/:id/episode/new">
        <Layout>
          <EpisodeForm />
        </Layout>
      </Route>
      <Route path="/podcast/:id/episode/:episodeId">
        <Layout>
          <EpisodeForm />
        </Layout>
      </Route>
      <Route path="/notifications">
        <Layout>
          <div className="p-8">
            <h1 className="text-2xl font-bold">Notifications</h1>
            <p className="text-muted-foreground mt-2">Coming soon...</p>
          </div>
        </Layout>
      </Route>
      <Route path="/settings">
        <Layout>
          <SettingsPage />
        </Layout>
      </Route>
      <Route path="/profile">
        <Layout>
          <Profile />
        </Layout>
      </Route>

      {/* 404 page with sidebar */}
      <Route>
        <Layout>
          <NotFound />
        </Layout>
      </Route>
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router />
        <Toaster />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;