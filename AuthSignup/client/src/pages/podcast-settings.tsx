import { useState, useEffect } from "react";
import { useForm, type UseFormReturn } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { podcastSchema, type PodcastFormData, podcastCategories, podcastLanguages, podcastAudienceTypes, voiceOptions, voiceAccents, videoStyles, conversationMoods } from "@shared/schema";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";
import { useQuery } from "@tanstack/react-query";
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
import { ArrowLeft, ArrowRight, Mic, Video, Settings, Globe } from "lucide-react";
import { usePodcast, useCreatePodcast, useUpdatePodcast } from '@/lib/api/services/podcast';

const steps = ["Basic Information", "Media & Style", "Contact & Social"];

interface SpeakerSectionProps {
  speakerNumber: 1 | 2;
  form: UseFormReturn<PodcastFormData>;
}

const SpeakerSection = ({ speakerNumber, form }: SpeakerSectionProps) => {
  const speakerField = `speaker${speakerNumber}` as const;
  const [audioPreview, setAudioPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      form.setValue(`${speakerField}.profileFile`, file);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-lg">Speaker {speakerNumber} Details</h3>
      <FormField
        control={form.control}
        name={`${speakerField}.name`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Name</FormLabel>
            <FormControl>
              <Input placeholder="Speaker name" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name={`${speakerField}.profileType`}
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
        name={`${speakerField}.profileFile`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Upload {form.watch(`${speakerField}.profileType`) || 'Media'}</FormLabel>
            <FormControl>
              <Input
                type="file"
                accept={form.watch(`${speakerField}.profileType`) === 'image' ? 'image/*' : 'video/*'}
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
        name={`${speakerField}.bio`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Bio</FormLabel>
            <FormControl>
              <Textarea
                placeholder="Speaker bio..."
                className="resize-none"
                {...field}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name={`${speakerField}.voice`}
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
        name={`${speakerField}.accent`}
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
  );
};

export default function PodcastSettings() {
  const [step, setStep] = useState(0);
  const { toast } = useToast();
  const [location, setLocation] = useLocation();
  const [audioPreview, setAudioPreview] = useState<string | null>(null);

  // Get podcast ID from URL if it exists
  const searchParams = new URLSearchParams(location.split('?')[1]);
  const podcastId = searchParams.get('id');
  const isEditMode = Boolean(podcastId);

  // Use the new API hooks
  const { data: podcastData, isLoading } = usePodcast(podcastId || '');
  const createPodcast = useCreatePodcast();
  const updatePodcast = useUpdatePodcast(podcastId || '');

  const form = useForm<PodcastFormData>({
    resolver: zodResolver(podcastSchema),
    defaultValues: podcastData || {
      title: "Tech Talks Weekly",
      description: "A podcast about technology, innovation, and the future of business. We interview industry leaders and discuss the latest trends.",
      coverImage: "https://images.unsplash.com/photo-1590069261209-f8e9b8642343",
      categories: ["Technology", "Business"],
      keywords: ["technology", "innovation", "business", "future"],
      language: "English",
      audienceType: "Business",
      website: "https://example.com/podcast",
      email: "podcast@example.com",
      contactNumber: "+1 234 567 8900",
      videoStyle: "Background Video",
      conversationMood: "Professional",
      speaker1: {
        name: 'Alex Thompson',
        profileType: 'video',
        profileFile: null,
        bio: 'Tech journalist and AI enthusiast with over a decade of experience. Host of multiple award-winning tech podcasts and regular contributor to leading tech publications.',
        voice: voiceOptions[0].id,
        accent: 'US'
      },
      speaker2: {
        name: 'Maria Chen',
        profileType: 'video',
        profileFile: null,
        bio: 'Research scientist in Machine Learning and former Silicon Valley executive. Specializes in explaining complex tech concepts in simple terms.',
        voice: voiceOptions[1].id,
        accent: 'US'
      }
    },
  });

  // Update form values when podcast data is fetched
  useEffect(() => {
    if (podcastData) {
      Object.entries(podcastData).forEach(([key, value]) => {
        form.setValue(key as keyof PodcastFormData, value);
      });
    }
  }, [podcastData, form]);

  const handleSubmit = async () => {
    const formData = form.getValues();

    try {
      if (isEditMode) {
        await updatePodcast.mutateAsync(formData);
        toast({
          title: "Success",
          description: "Podcast updated successfully",
        });
      } else {
        await createPodcast.mutateAsync(formData);
        toast({
          title: "Success",
          description: "Podcast created successfully",
        });
      }
      setLocation("/dashboard");
    } catch (error) {
      // Error handling is now managed by the API client
      console.error('Failed to save podcast:', error);
      toast({
        title: "Error",
        description: "Failed to save podcast settings",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 py-8">
      <div className="absolute inset-0 bg-cover bg-center opacity-10 -z-10"
           style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1590069261209-f8e9b8642343")' }} />

      <Card className="w-full max-w-2xl mx-4 shadow-xl relative z-10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            {step === 0 ? <Mic className="w-6 h-6" /> :
             step === 1 ? <Video className="w-6 h-6" /> :
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
                        <FormLabel>Podcast Title</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter your podcast title" {...field} />
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
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Describe your podcast..."
                            className="min-h-[100px]"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="categories"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Categories</FormLabel>
                        <FormControl>
                          <Select multiple onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select categories" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {podcastCategories.map((category) => (
                                <SelectItem key={category} value={category}>
                                  {category}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="keywords"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Keywords</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter keywords separated by commas" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="language"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Language</FormLabel>
                          <FormControl>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select language" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {podcastLanguages.map((language) => (
                                  <SelectItem key={language} value={language}>
                                    {language}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="audienceType"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Audience Type</FormLabel>
                          <FormControl>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select audience type" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {podcastAudienceTypes.map((audienceType) => (
                                  <SelectItem key={audienceType} value={audienceType}>
                                    {audienceType}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  {/* Add other basic info fields */}
                </>
              ) : step === 1 ? (
                <>
                  <div className="space-y-8">
                    <SpeakerSection speakerNumber={1} form={form} />
                    <div className="border-t pt-8">
                      <SpeakerSection speakerNumber={2} form={form} />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
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
                        <FormLabel>Cover Image</FormLabel>
                        <FormControl>
                          <Input type="url" placeholder="Enter cover image URL" {...field} />
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
                    name="website"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Website URL</FormLabel>
                        <FormControl>
                          <Input placeholder="https://www.example.com" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input type="email" placeholder="contact@example.com" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="contactNumber"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Contact Number</FormLabel>
                          <FormControl>
                            <Input placeholder="+1 234 567 8900" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
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
                  onClick={handleSubmit}
                  disabled={isLoading}
                >
                  {step === steps.length - 1 ? (
                    isEditMode ? "Save Changes" : "Create Podcast"
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