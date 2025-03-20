import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Youtube } from "lucide-react";

// Sample YouTube channels data
const mockChannels = [
  { id: "1", name: "Tech Podcast Channel" },
  { id: "2", name: "Business Insights" },
  { id: "3", name: "Personal Brand" },
];

// Sample playlists data
const mockPlaylists = [
  { id: "1", name: "Tech Talks Weekly Episodes" },
  { id: "2", name: "Business Podcast Series" },
  { id: "3", name: "Featured Content" },
];

const youtubeSettingsSchema = z.object({
  channelId: z.string().min(1, "Please select a channel"),
  playlistId: z.string().optional(),
  autoPublish: z.boolean().optional(),
  defaultTitle: z.string().optional(),
  defaultDescription: z.string().optional(),
});

type YoutubeSettingsFormData = z.infer<typeof youtubeSettingsSchema>;

export default function YouTube() {
  const [connected, setConnected] = useState(false);

  const form = useForm<YoutubeSettingsFormData>({
    resolver: zodResolver(youtubeSettingsSchema),
    defaultValues: {
      channelId: "",
      playlistId: "",
      autoPublish: false,
      defaultTitle: "Tech Talks Weekly - Latest Episode",
      defaultDescription: "Watch the latest episode of Tech Talks Weekly!\n\nIn this episode, we explore fascinating topics in technology and innovation.\n\nSubscribe for more content!",
    },
  });

  const handleConnect = () => {
    // TODO: Implement actual YouTube OAuth flow
    setConnected(true);
  };

  const onSubmit = (data: YoutubeSettingsFormData) => {
    console.log("YouTube settings:", data);
    // TODO: Save settings to backend
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <Youtube className="w-8 h-8 text-red-500" />
          <h1 className="text-3xl font-bold">YouTube Management</h1>
        </div>

        <div className="space-y-6">
          {!connected ? (
            <Card>
              <CardHeader>
                <CardTitle>Connect Your YouTube Channel</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  Connect your YouTube channel to automatically publish podcast episodes as videos.
                </p>
                <Button onClick={handleConnect} className="bg-red-500 hover:bg-red-600">
                  <Youtube className="mr-2 h-4 w-4" />
                  Connect YouTube Channel
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>YouTube Publishing Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <FormField
                      control={form.control}
                      name="channelId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Select Channel</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Choose a channel" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {mockChannels.map((channel) => (
                                <SelectItem key={channel.id} value={channel.id}>
                                  {channel.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="playlistId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Default Playlist (Optional)</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Choose a playlist" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {mockPlaylists.map((playlist) => (
                                <SelectItem key={playlist.id} value={playlist.id}>
                                  {playlist.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="defaultTitle"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Default Video Title Template</FormLabel>
                          <FormControl>
                            <Input {...field} />
                          </FormControl>
                          <p className="text-sm text-muted-foreground">
                            Example: "Tech Talks Weekly - Latest Episode"
                          </p>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="defaultDescription"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Default Video Description Template</FormLabel>
                          <FormControl>
                            <Input {...field} />
                          </FormControl>
                          <p className="text-sm text-muted-foreground">
                            Example: "Watch the latest episode of our podcast! Subscribe for more content."
                          </p>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <Button type="submit" className="w-full">
                      Save YouTube Settings
                    </Button>
                  </CardContent>
                </Card>
              </form>
            </Form>
          )}
        </div>
      </div>
    </div>
  );
}