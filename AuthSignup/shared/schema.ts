import { pgTable, text, serial } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  businessName: text("business_name").notNull(),
  businessEmail: text("business_email").notNull(),
  businessDetails: text("business_details").notNull(),
  businessType: text("business_type").notNull(),
  businessWebsite: text("business_website"),
  targetAudience: text("target_audience").notNull(),
});

export const businessTypes = [
  "Retail",
  "Technology",
  "Healthcare",
  "Education",
  "Finance",
  "Entertainment",
  "Other"
] as const;

export const podcastLanguages = [
  "English",
  "Spanish",
  "French",
  "German",
  "Mandarin",
  "Hindi",
  "Other"
] as const;

export const podcastCategories = [
  "Business",
  "Technology",
  "Education",
  "Entertainment",
  "Health",
  "News",
  "Sports",
  "Other"
] as const;

export const podcastAudienceTypes = [
  "General",
  "Business",
  "Niche"
] as const;

export const voiceAccents = [
  "US",
  "UK",
  "Indian",
  "Australian",
  "Canadian",
  "Irish",
  "Scottish",
  "Other"
] as const;

export const videoStyles = [
  "Background Video",
  "Static Image",
  "Animated Background",
  "Split Screen",
  "Picture-in-Picture"
] as const;

export const conversationMoods = [
  "Friendly",
  "Professional",
  "Excited",
  "Calm",
  "Casual",
  "Serious",
  "Humorous"
] as const;

export const episodeDurations = [
  "5 minutes",
  "10 minutes",
  "15 minutes",
  "30 minutes",
  "45 minutes",
  "60 minutes"
] as const;

export const voiceOptions = [
  {
    id: "voice1",
    name: "John (Male)",
    preview: "/voices/john-preview.mp3"
  },
  {
    id: "voice2",
    name: "Sarah (Female)",
    preview: "/voices/sarah-preview.mp3"
  },
  {
    id: "voice3",
    name: "David (Male)",
    preview: "/voices/david-preview.mp3"
  },
  {
    id: "voice4",
    name: "Emma (Female)",
    preview: "/voices/emma-preview.mp3"
  }
] as const;

export const insertUserSchema = createInsertSchema(users)
  .omit({ id: true })
  .extend({
    email: z.string().email("Invalid email address"),
    businessEmail: z.string().email("Invalid business email address"),
    name: z.string().min(2, "Name must be at least 2 characters"),
    businessName: z.string().min(2, "Business name must be at least 2 characters"),
    businessDetails: z.string().min(10, "Please provide more business details"),
    businessType: z.enum(businessTypes, {
      required_error: "Please select a business type",
    }),
    businessWebsite: z.string().url("Invalid website URL").optional(),
    targetAudience: z.string().min(10, "Please describe your target audience"),
  });

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export const podcastSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(50, "Description must be at least 50 characters"),
  coverImage: z.string().url("Invalid cover image URL").optional(),
  categories: z.array(z.enum(podcastCategories)).min(1, "Select at least one category"),
  keywords: z.array(z.string()).min(1, "Add at least one keyword"),
  language: z.enum(podcastLanguages, {
    required_error: "Please select a language",
  }),
  audienceType: z.enum(podcastAudienceTypes, {
    required_error: "Please select target audience type",
  }),
  website: z.string().url("Invalid website URL").optional(),
  email: z.string().email("Invalid email address").optional(),
  contactNumber: z.string().optional(),
  // Speaker profiles
  speaker1: z.object({
    name: z.string().min(2, "Speaker name must be at least 2 characters"),
    profileType: z.enum(["image", "video"]),
    profileFile: z.any(),
    bio: z.string().min(10, "Bio must be at least 10 characters"),
    voice: z.string().min(1, "Please select speaker voice"),
    accent: z.enum(voiceAccents, {
      required_error: "Please select speaker accent",
    }),
  }),
  speaker2: z.object({
    name: z.string().min(2, "Speaker name must be at least 2 characters"),
    profileType: z.enum(["image", "video"]),
    profileFile: z.any(),
    bio: z.string().min(10, "Bio must be at least 10 characters"),
    voice: z.string().min(1, "Please select speaker voice"),
    accent: z.enum(voiceAccents, {
      required_error: "Please select speaker accent",
    }),
  }).optional(),
  videoStyle: z.enum(videoStyles, {
    required_error: "Please select video style",
  }),
  conversationMood: z.enum(conversationMoods, {
    required_error: "Please select conversation mood",
  }),
});

export type PodcastFormData = z.infer<typeof podcastSchema>;

export const episodeSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(50, "Description must be at least 50 characters"),
  keywords: z.array(z.string()).min(1, "Add at least one keyword"),
  duration: z.enum(episodeDurations, {
    required_error: "Please select episode duration",
  }),
  voice1: z.string().min(1, "Please select primary voice"),
  voice2: z.string().optional(),
  voiceAccent: z.enum(voiceAccents, {
    required_error: "Please select voice accent",
  }),
  language: z.enum(podcastLanguages, {
    required_error: "Please select language",
  }),
  videoStyle: z.enum(videoStyles, {
    required_error: "Please select video style",
  }),
  conversationMood: z.enum(conversationMoods, {
    required_error: "Please select conversation mood",
  }),
  coverImage: z.string().url("Invalid cover image URL").optional(),
  guest1: z.object({
    name: z.string().min(2, "Guest name must be at least 2 characters"),
    profileType: z.enum(["image", "video"]),
    profileFile: z.any(),
    bio: z.string().min(10, "Bio must be at least 10 characters"),
    voice: z.string().min(1, "Please select guest voice"),
    accent: z.enum(voiceAccents, {
      required_error: "Please select guest accent",
    }),
  }).optional(),
  guest2: z.object({
    name: z.string().min(2, "Guest name must be at least 2 characters"),
    profileType: z.enum(["image", "video"]),
    profileFile: z.any(),
    bio: z.string().min(10, "Bio must be at least 10 characters"),
    voice: z.string().min(1, "Please select guest voice"),
    accent: z.enum(voiceAccents, {
      required_error: "Please select guest accent",
    }),
  }).optional(),
  backgroundMusic: z.string().optional(),
  publishDate: z.string().optional(),
  status: z.enum(["draft", "published"]).default("draft"),
});

export type EpisodeFormData = z.infer<typeof episodeSchema>;