import { useState } from "react";
import { useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  episodeSchema,
  type EpisodeFormData,
  podcastLanguages,
  voiceAccents,
  videoStyles,
  conversationMoods,
  episodeDurations,
  voiceOptions,
} from "@shared/schema";
import { useToast } from "@/hooks/use-toast";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ArrowLeft,
  ArrowRight,
  Mic,
  Video,
  Settings,
  User,
} from "lucide-react";

const steps = [
  "Basic Details",
  "Guest Details",
  "Media & Style",
  "Advanced Options",
];

export default function EpisodeForm() {
  const [step, setStep] = useState(0);
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const form = useForm<EpisodeFormData>({
    resolver: zodResolver(episodeSchema),
    defaultValues: {
      title: "Introduction to AI Technology",
      description: "In this episode, we dive deep into the fundamentals of AI technology and its impact on modern business. Join us as we explore machine learning, neural networks, and practical applications.",
      keywords: ["AI", "technology", "machine learning"],
      duration: "30 minutes",
      voice1: "AI Assistant 1",
      voice2: "AI Assistant 2",
      voiceAccent: "US",
      language: "English",
      videoStyle: "Background Video",
      conversationMood: "Professional",
      coverImage: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
      guest1: {
        name: "John Smith",
        profileType: "video",
        profileUrl: "https://example.com/videos/john-smith-intro.mp4",
        bio: "AI Research Director at Tech Corp with over 15 years of experience in machine learning and neural networks. Leading groundbreaking projects in artificial intelligence.",
        voice: "Guest Voice 1",
        accent: "US",
        social: {
          twitter: "@johnsmith",
          linkedin: "https://linkedin.com/in/johnsmith",
          website: "https://johnsmith.com",
        },
      },
      guest2: {
        name: "Sarah Johnson",
        profileType: "video",
        profileUrl: "https://example.com/videos/sarah-johnson-intro.mp4",
        bio: "Innovation Lead at Future Technologies, specializing in AI ethics and responsible AI development. Regular speaker at tech conferences.",
        voice: "Guest Voice 2",
        accent: "UK",
        social: {
          twitter: "@sarahjohnson",
          linkedin: "https://linkedin.com/in/sarahjohnson",
          website: "https://sarahjohnson.com",
        },
      },
      status: "draft",
    },
  });

  const nextStep = async () => {
    let fields: (keyof EpisodeFormData)[] = [];

    if (step === 0) {
      fields = ["title", "description", "keywords", "duration", "voice1", "voiceAccent", "language"];
    } else if (step === 1) {
      // Guest Details validation
      fields = ["guest1", "guest2"];
    } else if (step === 2) {
      fields = ["videoStyle", "conversationMood", "coverImage"];
    } else if (step === 3) {
      fields = ["publishDate", "status"];
    }

    const result = await form.trigger(fields);
    if (result) {
      if (step === steps.length - 1) {
        console.log(form.getValues());
        toast({
          title: "Success",
          description: "Episode saved successfully",
        });
        setLocation("/podcast/1");
      } else {
        setStep(step + 1);
      }
    }
  };

  const GuestSection = ({ guestNumber }: { guestNumber: 1 | 2 }) => {
    const guestField = `guest${guestNumber}` as const;
    const [audioPreview, setAudioPreview] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        // Handle file upload here
        form.setValue(`${guestField}.profileFile`, file);
      }
    };

    return (
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Guest {guestNumber} Details</h3>
        <FormField
          control={form.control}
          name={`${guestField}.name`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="Guest name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name={`${guestField}.profileType`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Profile Type</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select profile type" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="image">Image</SelectItem>
                  <SelectItem value="video">Video</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name={`${guestField}.profileFile`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Upload {form.watch(`${guestField}.profileType`) || 'Media'}</FormLabel>
              <FormControl>
                <Input
                  type="file"
                  accept={form.watch(`${guestField}.profileType`) === 'image' ? 'image/*' : 'video/*'}
                  onChange={handleFileChange}
                  className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name={`${guestField}.voice`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Voice</FormLabel>
              <Select
                onValueChange={(value) => {
                  field.onChange(value);
                  const voice = voiceOptions.find(v => v.id === value);
                  if (voice) {
                    setAudioPreview(voice.preview);
                  }
                }}
                defaultValue={field.value}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select voice" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {voiceOptions.map((voice) => (
                    <SelectItem key={voice.id} value={voice.id}>
                      {voice.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {audioPreview && (
                <div className="mt-2">
                  <audio controls src={audioPreview} className="w-full">
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name={`${guestField}.accent`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Accent</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select accent" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {voiceAccents.map((accent) => (
                    <SelectItem key={accent} value={accent}>
                      {accent}
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
          name={`${guestField}.bio`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Guest bio..."
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="space-y-4">
          <h4 className="font-medium">Social Links</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormField
              control={form.control}
              name={`${guestField}.social.twitter`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Twitter</FormLabel>
                  <FormControl>
                    <Input placeholder="@handle" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`${guestField}.social.linkedin`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>LinkedIn</FormLabel>
                  <FormControl>
                    <Input placeholder="Profile URL" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`${guestField}.social.website`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Website</FormLabel>
                  <FormControl>
                    <Input placeholder="Website URL" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 py-8">
      <div className="absolute inset-0 bg-cover bg-center opacity-10 -z-10"
           style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1590069261209-f8e9b8642343")' }} />

      <Card className="w-full max-w-2xl mx-4 shadow-xl relative z-10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            {step === 0 ? <Mic className="w-6 h-6" /> :
              step === 1 ? <User className="w-6 h-6" /> :
              step === 2 ? <Video className="w-6 h-6" /> :
              <Settings className="w-6 h-6" />}
            {steps[step]}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form className="space-y-6">
              {step === 0 ? (
                <>
                  <FormField
                    control={form.control}
                    name="title"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Episode Title</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter episode title" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Episode Description</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Describe your episode..."
                            className="min-h-[150px]"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="duration"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Duration</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select duration" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {episodeDurations.map((duration) => (
                                <SelectItem key={duration} value={duration}>
                                  {duration}
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
                      name="language"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Language</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select language" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {podcastLanguages.map((lang) => (
                                <SelectItem key={lang} value={lang}>
                                  {lang}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="voice1"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Primary Voice</FormLabel>
                          <FormControl>
                            <Input placeholder="Select voice" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="voiceAccent"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Voice Accent</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select accent" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {voiceAccents.map((accent) => (
                                <SelectItem key={accent} value={accent}>
                                  {accent}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </>
              ) : step === 1 ? (
                <div className="space-y-8">
                  <GuestSection guestNumber={1} />
                  <div className="border-t pt-8">
                    <GuestSection guestNumber={2} />
                  </div>
                </div>
              ) : step === 2 ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="videoStyle"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Video Style</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select style" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {videoStyles.map((style) => (
                                <SelectItem key={style} value={style}>
                                  {style}
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
                      name="conversationMood"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Conversation Mood</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select mood" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {conversationMoods.map((mood) => (
                                <SelectItem key={mood} value={mood}>
                                  {mood}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  <FormField
                    control={form.control}
                    name="coverImage"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Cover Image URL</FormLabel>
                        <FormControl>
                          <Input placeholder="https://example.com/image.jpg" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              ) : (
                <>
                  <FormField
                    control={form.control}
                    name="publishDate"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Publish Date</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="status"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Status</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select status" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="draft">Draft</SelectItem>
                            <SelectItem value="published">Published</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}

              <div className="flex justify-between pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep(step - 1)}
                  disabled={step === 0}
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
                <Button
                  type="button"
                  onClick={nextStep}
                >
                  {step === steps.length - 1 ? (
                    "Save Episode"
                  ) : (
                    <>
                      Next
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}