import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Settings,
  Bell,
  Mic,
  Bot,
  Share2,
  LineChart,
  Wrench,
  Youtube,
} from "lucide-react";

// Mock data for dropdowns
const voiceOptions = [
  { id: "voice1", name: "Alex (Male)" },
  { id: "voice2", name: "Sarah (Female)" },
  { id: "voice3", name: "James (Male)" },
  { id: "voice4", name: "Emma (Female)" },
];

const accentOptions = ["US", "UK", "Australian", "Indian", "Canadian"];
const videoStyles = ["Dynamic", "Static", "Minimal", "Professional"];
const durations = ["5 mins", "10 mins", "15 mins", "30 mins", "45 mins", "60 mins"];
const conversationMoods = ["Professional", "Friendly", "Casual", "Formal", "Enthusiastic"];

export default function SettingsPage() {
  const [isAutopilot, setIsAutopilot] = useState(false);

  return (
    <div className="p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <Tabs defaultValue="podcast" className="space-y-6">
          <TabsList className="grid grid-cols-3 lg:grid-cols-6 gap-4">
            <TabsTrigger value="podcast" className="flex items-center gap-2">
              <Mic className="w-4 h-4" />
              Podcast
            </TabsTrigger>
            <TabsTrigger value="automation" className="flex items-center gap-2">
              <Bot className="w-4 h-4" />
              Automation
            </TabsTrigger>
            <TabsTrigger value="distribution" className="flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Distribution
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <LineChart className="w-4 h-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="w-4 h-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2">
              <Wrench className="w-4 h-4" />
              Advanced
            </TabsTrigger>
          </TabsList>

          <TabsContent value="podcast">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Default Podcast Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Default Language</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select language" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Primary Voice</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select voice" />
                      </SelectTrigger>
                      <SelectContent>
                        {voiceOptions.map((voice) => (
                          <SelectItem key={voice.id} value={voice.id}>
                            {voice.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Secondary Voice</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select voice" />
                      </SelectTrigger>
                      <SelectContent>
                        {voiceOptions.map((voice) => (
                          <SelectItem key={voice.id} value={voice.id}>
                            {voice.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Voice Accent</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select accent" />
                      </SelectTrigger>
                      <SelectContent>
                        {accentOptions.map((accent) => (
                          <SelectItem key={accent} value={accent}>
                            {accent}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Video Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Default Video Style</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select style" />
                      </SelectTrigger>
                      <SelectContent>
                        {videoStyles.map((style) => (
                          <SelectItem key={style} value={style}>
                            {style}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Background Video</Label>
                    <Input type="file" accept="video/*" />
                  </div>

                  <div className="space-y-2">
                    <Label>Static Background Image</Label>
                    <Input type="file" accept="image/*" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Episode Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Default Episode Duration</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select duration" />
                      </SelectTrigger>
                      <SelectContent>
                        {durations.map((duration) => (
                          <SelectItem key={duration} value={duration}>
                            {duration}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Default Conversation Mood</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select mood" />
                      </SelectTrigger>
                      <SelectContent>
                        {conversationMoods.map((mood) => (
                          <SelectItem key={mood} value={mood}>
                            {mood}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="automation">
            <Card>
              <CardHeader>
                <CardTitle>Automation Mode</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold mb-1">
                      {isAutopilot ? "Autopilot Mode" : "Co-Pilot Mode"}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {isAutopilot
                        ? "Fully automated: No manual approvals needed"
                        : "Manual approval required for publishing"}
                    </p>
                  </div>
                  <Switch
                    checked={isAutopilot}
                    onCheckedChange={setIsAutopilot}
                  />
                </div>

                <div className="border rounded-lg p-4 space-y-4">
                  <h4 className="font-medium">Current Mode Features:</h4>
                  {isAutopilot ? (
                    <ul className="space-y-2">
                      <li className="flex items-center text-sm">
                        ✅ Automatic podcast transcript generation
                      </li>
                      <li className="flex items-center text-sm">
                        ✅ Automatic YouTube video creation
                      </li>
                      <li className="flex items-center text-sm">
                        ✅ Automatic podcast audio generation
                      </li>
                      <li className="flex items-center text-sm">
                        ✅ Auto-publishing enabled
                      </li>
                    </ul>
                  ) : (
                    <ul className="space-y-2">
                      <li className="flex items-center text-sm">
                        👉 Manual approval for podcast transcripts
                      </li>
                      <li className="flex items-center text-sm">
                        👉 Manual approval for YouTube videos
                      </li>
                      <li className="flex items-center text-sm">
                        👉 Manual approval for podcast audio
                      </li>
                      <li className="flex items-center text-sm">
                        👉 Publishing requires confirmation
                      </li>
                    </ul>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="distribution">
            <Card>
              <CardHeader>
                <CardTitle>Distribution & Integrations</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Configure your content distribution channels and third-party integrations.
                </p>
                <div className="space-y-4">
                  <Button className="w-full justify-start">
                    <Youtube className="mr-2 h-4 w-4" />
                    Configure YouTube Settings
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    Add New Integration
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>Analytics & Monetization</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  View your analytics and manage monetization settings.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive updates about your content via email
                    </p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Publishing Alerts</Label>
                    <p className="text-sm text-muted-foreground">
                      Get notified when content is published
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="advanced">
            <Card>
              <CardHeader>
                <CardTitle>Advanced Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>API Key</Label>
                  <div className="flex gap-2">
                    <Input type="password" value="************************" readOnly />
                    <Button variant="outline">Reset</Button>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Use this key to access the API programmatically
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}