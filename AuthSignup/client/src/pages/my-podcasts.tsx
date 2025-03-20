import { useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Plus,
  LayoutGrid,
  List,
  ArrowUpDown,
  Filter,
  MoreVertical,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Extended mock data
const mockPodcasts = [
  {
    id: 1,
    title: "Tech Talks Weekly",
    description: "Your weekly dose of tech insights and innovations",
    coverImage: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
    episodes: 15,
    categories: ["Technology", "Business"],
    keywords: ["tech", "innovation", "startups"],
    stats: {
      totalListeners: 12500,
      averageRating: 4.8,
      totalDuration: "23 hours"
    },
    lastUpdated: "2024-03-01",
    status: "active"
  },
  {
    id: 2,
    title: "Business Insights",
    description: "Expert analysis of business trends and strategies",
    coverImage: "https://images.unsplash.com/photo-1434626881859-194d67b2b86f",
    episodes: 8,
    categories: ["Business", "Education"],
    keywords: ["entrepreneurship", "leadership"],
    stats: {
      totalListeners: 8300,
      averageRating: 4.6,
      totalDuration: "12 hours"
    },
    lastUpdated: "2024-02-28",
    status: "active"
  },
  {
    id: 3,
    title: "AI Revolution",
    description: "Exploring the future of artificial intelligence",
    coverImage: "https://images.unsplash.com/photo-1677442136019-21780ecad995",
    episodes: 12,
    categories: ["Technology", "Science"],
    keywords: ["AI", "machine learning", "future tech"],
    stats: {
      totalListeners: 15700,
      averageRating: 4.9,
      totalDuration: "18 hours"
    },
    lastUpdated: "2024-03-04",
    status: "active"
  },
  {
    id: 4,
    title: "Health & Wellness Today",
    description: "Your guide to a healthier lifestyle",
    coverImage: "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
    episodes: 20,
    categories: ["Health", "Lifestyle"],
    keywords: ["health", "wellness", "fitness"],
    stats: {
      totalListeners: 9800,
      averageRating: 4.7,
      totalDuration: "25 hours"
    },
    lastUpdated: "2024-03-02",
    status: "draft"
  },
  {
    id: 5,
    title: "Creative Corner",
    description: "Unleashing creativity in the digital age",
    coverImage: "https://images.unsplash.com/photo-1513364776144-60967b0f800f",
    episodes: 6,
    categories: ["Art", "Technology"],
    keywords: ["creativity", "digital art", "design"],
    stats: {
      totalListeners: 6200,
      averageRating: 4.5,
      totalDuration: "9 hours"
    },
    lastUpdated: "2024-02-25",
    status: "active"
  }
];

function PodcastCard({ podcast, viewMode }: { podcast: typeof mockPodcasts[0], viewMode: 'grid' | 'list' }) {
  const [, setLocation] = useLocation();

  if (viewMode === 'list') {
    return (
      <Card className="mb-4">
        <CardContent className="flex items-center p-4">
          <img
            src={podcast.coverImage}
            alt={podcast.title}
            className="w-24 h-24 object-cover rounded-md mr-4"
          />
          <div className="flex-1">
            <h3 className="text-lg font-semibold">{podcast.title}</h3>
            <p className="text-sm text-muted-foreground mb-2">{podcast.description}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>{podcast.episodes} Episodes</span>
              <span>•</span>
              <span>{podcast.stats.totalListeners.toLocaleString()} Listeners</span>
              <span>•</span>
              <span>Rating: {podcast.stats.averageRating}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setLocation(`/podcast/${podcast.id}`)}>
              Manage
            </Button>
            <Button variant="ghost" size="icon">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <div className="h-48 relative">
        <img
          src={podcast.coverImage}
          alt={podcast.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-2 right-2">
          <Button variant="ghost" size="icon" className="bg-black/20 hover:bg-black/40 text-white">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
          <div className="text-white">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${podcast.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'}`} />
              <span className="text-sm capitalize">{podcast.status}</span>
            </div>
          </div>
        </div>
      </div>
      <CardHeader>
        <CardTitle className="line-clamp-1">{podcast.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{podcast.description}</p>
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>{podcast.episodes} Episodes</span>
            <span>{podcast.stats.totalDuration}</span>
          </div>
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>{podcast.stats.totalListeners.toLocaleString()} Listeners</span>
            <span>★ {podcast.stats.averageRating}</span>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
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

export default function MyPodcasts() {
  const [, setLocation] = useLocation();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState("recent");
  const [filterStatus, setFilterStatus] = useState("all");

  const filteredPodcasts = mockPodcasts
    .filter(podcast => filterStatus === "all" || podcast.status === filterStatus)
    .sort((a, b) => {
      switch (sortBy) {
        case "listeners":
          return b.stats.totalListeners - a.stats.totalListeners;
        case "episodes":
          return b.episodes - a.episodes;
        case "rating":
          return b.stats.averageRating - a.stats.averageRating;
        default:
          return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
      }
    });

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">My Podcasts</h1>
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

        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[180px]">
              <ArrowUpDown className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Most Recent</SelectItem>
              <SelectItem value="listeners">Most Listeners</SelectItem>
              <SelectItem value="episodes">Most Episodes</SelectItem>
              <SelectItem value="rating">Highest Rated</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[180px]">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className={viewMode === 'grid' ? 
          "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : 
          "space-y-4"
        }>
          {filteredPodcasts.map((podcast) => (
            <PodcastCard key={podcast.id} podcast={podcast} viewMode={viewMode} />
          ))}
        </div>
      </div>
    </div>
  );
}
