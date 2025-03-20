import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Youtube, Mic2, Play, CheckCircle, XCircle, FileText, RefreshCw } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Mock data for drafts
const mockYouTubeDrafts = [
  {
    id: "1",
    title: "AI in Business - Episode 1",
    thumbnail: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
    duration: "32:15",
    createdAt: "2024-03-05",
  },
  {
    id: "2",
    title: "Future of Technology - Special Episode",
    thumbnail: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
    duration: "45:20",
    createdAt: "2024-03-04",
  },
];

const mockPodcastDrafts = [
  {
    id: "1",
    title: "Startup Success Stories - Episode 3",
    audioUrl: "https://example.com/podcast1.mp3",
    duration: "28:45",
    createdAt: "2024-03-05",
  },
  {
    id: "2",
    title: "Tech Innovation Today - Episode 5",
    audioUrl: "https://example.com/podcast2.mp3",
    duration: "36:10",
    createdAt: "2024-03-04",
  },
];

// Mock data for transcripts
const mockTranscripts = [
  {
    id: "1",
    title: "AI in Business - Episode 1 Transcript",
    createdAt: "2024-03-05",
    segments: [
      {
        speaker: "Alex Thompson",
        content: "Welcome to Tech Talks Weekly. Today we're discussing the impact of AI on modern business practices."
      },
      {
        speaker: "Maria Chen",
        content: "Thanks for having me, Alex. It's a fascinating topic that's transforming industries."
      },
      {
        speaker: "Alex Thompson",
        content: "Let's start with the basics. How are businesses implementing AI today?"
      },
      {
        speaker: "Maria Chen",
        content: "Well, we're seeing AI adoption across various sectors. From customer service chatbots to predictive analytics..."
      }
    ]
  },
  {
    id: "2",
    title: "Startup Success Stories - Episode 3 Transcript",
    createdAt: "2024-03-04",
    segments: [
      {
        speaker: "Alex Thompson",
        content: "Welcome back to another exciting episode of Tech Talks Weekly."
      },
      {
        speaker: "Maria Chen",
        content: "Today we're exploring the journey of successful tech startups."
      },
      {
        speaker: "Alex Thompson",
        content: "We'll be looking at some fascinating case studies..."
      }
    ]
  }
];

// Sample YouTube channels and playlists
const mockChannels = [
  { id: "1", name: "Tech Podcast Channel" },
  { id: "2", name: "Business Insights" },
  { id: "3", name: "Personal Brand" },
];

const mockPlaylists = [
  { id: "1", name: "Tech Talks Weekly Episodes" },
  { id: "2", name: "Business Podcast Series" },
  { id: "3", name: "Featured Content" },
];

function YouTubePublishDialog({ isOpen, onClose, onPublish }: any) {
  const [channelId, setChannelId] = useState("");
  const [playlistId, setPlaylistId] = useState("");

  return (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Publish to YouTube</DialogTitle>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Select Channel</label>
          <Select onValueChange={setChannelId}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a channel" />
            </SelectTrigger>
            <SelectContent>
              {mockChannels.map((channel) => (
                <SelectItem key={channel.id} value={channel.id}>
                  {channel.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Select Playlist (Optional)</label>
          <Select onValueChange={setPlaylistId}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a playlist" />
            </SelectTrigger>
            <SelectContent>
              {mockPlaylists.map((playlist) => (
                <SelectItem key={playlist.id} value={playlist.id}>
                  {playlist.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => onPublish({ channelId, playlistId })}>
            Publish
          </Button>
        </div>
      </div>
    </DialogContent>
  );
}

function RejectDialog({ isOpen, onClose, onReject }: any) {
  const [reason, setReason] = useState("");

  return (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Reject Draft</DialogTitle>
      </DialogHeader>
      <div className="space-y-4 py-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Rejection Reason</label>
          <Textarea
            placeholder="Please provide a reason for rejection..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="min-h-[100px]"
          />
        </div>
        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={() => onReject(reason)} disabled={!reason.trim()}>
            Confirm Rejection
          </Button>
        </div>
      </div>
    </DialogContent>
  );
}

function DraftCard({ draft, type }: { draft: any; type: 'youtube' | 'podcast' }) {
  const [showPublishDialog, setShowPublishDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);

  const handlePublish = (publishData?: { channelId: string; playlistId: string }) => {
    console.log(`Publishing ${type} draft:`, draft.id, publishData);
    setShowPublishDialog(false);
    // TODO: Implement actual publish logic
  };

  const handleReject = (reason: string) => {
    console.log(`Rejecting ${type} draft:`, draft.id, "Reason:", reason);
    setShowRejectDialog(false);
    // TODO: Implement actual reject logic
  };

  return (
    <Card>
      <CardContent className="p-4">
        {type === 'youtube' ? (
          // YouTube video preview
          <div className="aspect-video relative mb-4 rounded-lg overflow-hidden bg-accent/10">
            <img
              src={draft.thumbnail}
              alt={draft.title}
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <Button size="icon" variant="secondary" className="w-12 h-12 rounded-full">
                <Play className="h-6 w-6" />
              </Button>
            </div>
            <div className="absolute bottom-2 right-2 bg-black/60 text-white px-2 py-1 rounded text-sm">
              {draft.duration}
            </div>
          </div>
        ) : (
          // Podcast audio player
          <div className="mb-4">
            <audio controls className="w-full" src={draft.audioUrl}>
              Your browser does not support the audio element.
            </audio>
            <div className="text-sm text-muted-foreground mt-2">
              Duration: {draft.duration}
            </div>
          </div>
        )}
        <h3 className="font-semibold mb-2">{draft.title}</h3>
        <div className="text-sm text-muted-foreground mb-4">
          Created on {new Date(draft.createdAt).toLocaleDateString()}
        </div>
        <div className="flex gap-2">
          {type === 'youtube' ? (
            <>
              <Dialog open={showPublishDialog} onOpenChange={setShowPublishDialog}>
                <DialogTrigger asChild>
                  <Button className="flex-1">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Publish
                  </Button>
                </DialogTrigger>
                <YouTubePublishDialog
                  isOpen={showPublishDialog}
                  onClose={() => setShowPublishDialog(false)}
                  onPublish={handlePublish}
                />
              </Dialog>
            </>
          ) : (
            <Button className="flex-1" onClick={() => handlePublish()}>
              <CheckCircle className="w-4 h-4 mr-2" />
              Publish
            </Button>
          )}
          <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" className="flex-1">
                <XCircle className="w-4 h-4 mr-2" />
                Reject
              </Button>
            </DialogTrigger>
            <RejectDialog
              isOpen={showRejectDialog}
              onClose={() => setShowRejectDialog(false)}
              onReject={handleReject}
            />
          </Dialog>
        </div>
      </CardContent>
    </Card>
  );
}

function TranscriptCard({ transcript }: { transcript: any }) {
  const [segments, setSegments] = useState(transcript.segments);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleContentChange = (index: number, newContent: string) => {
    const newSegments = [...segments];
    newSegments[index] = { ...newSegments[index], content: newContent };
    setSegments(newSegments);
  };

  const handleRegenerateTranscript = async () => {
    setIsRegenerating(true);
    // TODO: Implement AI regeneration logic
    setTimeout(() => {
      setIsRegenerating(false);
    }, 2000);
  };

  const handleApprove = () => {
    console.log('Approving transcript...', segments);
    // TODO: Implement approval logic
  };

  return (
    <Card>
      <CardContent className="p-4">
        <h3 className="font-semibold mb-2">{transcript.title}</h3>
        <div className="text-sm text-muted-foreground mb-4">
          Created on {new Date(transcript.createdAt).toLocaleDateString()}
        </div>

        <div className="space-y-4 mb-4">
          {segments.map((segment, index) => (
            <div key={index} className="space-y-2">
              <div className="font-medium text-sm px-3 py-1 bg-muted rounded-t-md">
                {segment.speaker}
              </div>
              <Textarea
                value={segment.content}
                onChange={(e) => handleContentChange(index, e.target.value)}
                className="min-h-[100px] font-mono text-sm"
                placeholder={`Enter ${segment.speaker}'s dialogue...`}
              />
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <Button className="flex-1" onClick={handleApprove}>
            <CheckCircle className="w-4 h-4 mr-2" />
            Approve
          </Button>
          <Button 
            variant="outline" 
            className="flex-1" 
            onClick={handleRegenerateTranscript}
            disabled={isRegenerating}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRegenerating ? 'animate-spin' : ''}`} />
            Regenerate with AI
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Drafts() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Content Drafts</h1>

        <Tabs defaultValue="youtube" className="space-y-6">
          <TabsList>
            <TabsTrigger value="youtube" className="flex items-center gap-2">
              <Youtube className="w-4 h-4" />
              YouTube Videos
            </TabsTrigger>
            <TabsTrigger value="podcast" className="flex items-center gap-2">
              <Mic2 className="w-4 h-4" />
              Podcast Episodes
            </TabsTrigger>
            <TabsTrigger value="transcripts" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Transcripts
            </TabsTrigger>
          </TabsList>

          <TabsContent value="youtube">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockYouTubeDrafts.map((draft) => (
                <DraftCard key={draft.id} draft={draft} type="youtube" />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="podcast">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockPodcastDrafts.map((draft) => (
                <DraftCard key={draft.id} draft={draft} type="podcast" />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="transcripts">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {mockTranscripts.map((transcript) => (
                <TranscriptCard key={transcript.id} transcript={transcript} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}