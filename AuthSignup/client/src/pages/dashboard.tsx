import { Link, useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Plus,
  BarChart,
  Search,
  Headphones,
  ChevronRight,
  MoreVertical,
} from "lucide-react";

// Mock data for demonstration
const mockPodcasts = [
  {
    id: 1,
    title: "Tech Talks Weekly",
    coverImage: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
    episodes: 15,
    categories: ["Technology", "Business"],
    keywords: ["tech", "innovation", "startups"],
  },
  {
    id: 2,
    title: "Business Insights",
    coverImage: "https://images.unsplash.com/photo-1434626881859-194d67b2b86f",
    episodes: 8,
    categories: ["Business", "Education"],
    keywords: ["entrepreneurship", "leadership"],
  },
];

function QuickActions() {
  const [, setLocation] = useLocation();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <Card 
        className="cursor-pointer hover:bg-accent/10 transition-colors"
        onClick={() => setLocation("/podcast-settings")}
      >
        <CardContent className="p-4 flex items-center justify-between">
          <div className="flex items-center">
            <Plus className="h-5 w-5 text-primary mr-2" />
            <span>New Podcast</span>
          </div>
          <ChevronRight className="h-4 w-4" />
        </CardContent>
      </Card>
      <Card 
        className="cursor-pointer hover:bg-accent/10 transition-colors"
        onClick={() => setLocation("/episode-form")}
      >
        <CardContent className="p-4 flex items-center justify-between">
          <div className="flex items-center">
            <Headphones className="h-5 w-5 text-primary mr-2" />
            <span>New Episode</span>
          </div>
          <ChevronRight className="h-4 w-4" />
        </CardContent>
      </Card>
      <Card 
        className="cursor-pointer hover:bg-accent/10 transition-colors"
        onClick={() => setLocation("/analytics")}
      >
        <CardContent className="p-4 flex items-center justify-between">
          <div className="flex items-center">
            <BarChart className="h-5 w-5 text-primary mr-2" />
            <span>Analytics</span>
          </div>
          <ChevronRight className="h-4 w-4" />
        </CardContent>
      </Card>
      <Card 
        className="cursor-pointer hover:bg-accent/10 transition-colors"
        onClick={() => setLocation("/search")}
      >
        <CardContent className="p-4 flex items-center justify-between">
          <div className="flex items-center">
            <Search className="h-5 w-5 text-primary mr-2" />
            <span>Search</span>
          </div>
          <ChevronRight className="h-4 w-4" />
        </CardContent>
      </Card>
    </div>
  );
}

function PodcastCard({ podcast }: { podcast: typeof mockPodcasts[0] }) {
  const [, setLocation] = useLocation();
  return (
    <Card className="overflow-hidden">
      <div className="h-48 relative">
        <img
          src={podcast.coverImage}
          alt={podcast.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-2 right-2">
          <Button variant="ghost" size="icon">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <CardHeader>
        <CardTitle>{podcast.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground">
            {podcast.episodes} Episodes
          </div>
          <div className="flex flex-wrap gap-2">
            {podcast.categories.map((category) => (
              <span key={category} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                {category}
              </span>
            ))}
          </div>
        </div>
      </CardContent>
      <CardContent>
        <Button className="w-full" onClick={() => setLocation(`/podcast/${podcast.id}`)}>
          Manage Episodes
        </Button>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [, setLocation] = useLocation();

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <div className="flex gap-4">
            <Input
              type="search"
              placeholder="Search podcasts..."
              className="w-64"
            />
            <Button onClick={() => setLocation("/podcast-settings")}>
              <Plus className="mr-2 h-4 w-4" />
              Create New Podcast
            </Button>
          </div>
        </div>

        <section>
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <QuickActions />
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-4">My Podcasts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockPodcasts.map((podcast) => (
              <PodcastCard key={podcast.id} podcast={podcast} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}