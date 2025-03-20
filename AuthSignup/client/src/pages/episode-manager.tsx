import { useState } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Edit2, MoreVertical, Trash2, Globe, Settings } from "lucide-react";

// Mock data for demonstration
const podcastDetails = {
  id: 1,
  title: "Tech Talks Weekly",
  coverImage: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
  description: "A podcast about technology, innovation, and the future of business. We interview industry leaders and discuss the latest trends.",
  targetAudience: "Tech professionals and enthusiasts",
  language: "English",
  totalPlays: 15000,
  totalListeners: 5000,
  website: "https://example.com/podcast",
  social: {
    twitter: "@techtalks",
    instagram: "@techtalkspodcast",
    linkedin: "https://linkedin.com/techtalks"
  }
};

const episodes = [
  {
    id: 1,
    title: "Intro to AI",
    description: "AI basics explained",
    duration: "15 min",
    date: "Mar 2, 2025",
    status: "published",
  },
  {
    id: 2,
    title: "AI in Business",
    description: "Interview with experts",
    duration: "30 min",
    date: "Mar 5, 2025",
    status: "draft",
  },
];

function PodcastInfo() {
  const [, setLocation] = useLocation();
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex gap-6">
          <div className="w-48 h-48 relative rounded-lg overflow-hidden">
            <img
              src={podcastDetails.coverImage}
              alt={podcastDetails.title}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1">
            <div className="flex justify-between items-start">
              <h1 className="text-2xl font-bold">{podcastDetails.title}</h1>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setLocation(`/podcast-settings?id=${podcastDetails.id}`)}
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-muted-foreground mt-2">{podcastDetails.description}</p>
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <h3 className="font-semibold">Target Audience</h3>
                <p className="text-sm text-muted-foreground">{podcastDetails.targetAudience}</p>
              </div>
              <div>
                <h3 className="font-semibold">Language</h3>
                <p className="text-sm text-muted-foreground">{podcastDetails.language}</p>
              </div>
              <div>
                <h3 className="font-semibold">Total Plays</h3>
                <p className="text-sm text-muted-foreground">{podcastDetails.totalPlays.toLocaleString()}</p>
              </div>
              <div>
                <h3 className="font-semibold">Total Listeners</h3>
                <p className="text-sm text-muted-foreground">{podcastDetails.totalListeners.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button variant="outline" size="sm">
                <Globe className="h-4 w-4 mr-2" />
                Website
              </Button>
              {Object.entries(podcastDetails.social).map(([platform, link]) => (
                <Button key={platform} variant="outline" size="sm">
                  {platform}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function EpisodeList() {
  const [, setLocation] = useLocation();

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Episodes</CardTitle>
          <Button onClick={() => setLocation(`/podcast/${podcastDetails.id}/episode/new`)}>
            Create New Episode
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Episode Title</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {episodes.map((episode) => (
              <TableRow key={episode.id}>
                <TableCell className="font-medium">{episode.title}</TableCell>
                <TableCell>{episode.description}</TableCell>
                <TableCell>{episode.duration}</TableCell>
                <TableCell>{episode.date}</TableCell>
                <TableCell>
                  <Badge variant={episode.status === "published" ? "default" : "secondary"}>
                    {episode.status === "published" ? "Published" : "Draft"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => setLocation(`/podcast/${podcastDetails.id}/episode/${episode.id}`)}>
                        <Edit2 className="h-4 w-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export default function EpisodeManager() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 space-y-8">
        <PodcastInfo />
        <EpisodeList />
      </div>
    </div>
  );
}