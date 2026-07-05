// Sample data mirroring the ZorkVDO backend's seeded catalog.
// This keeps the marketing site self-contained — when the Flutter app
// ships, it will consume these same shapes from the live API.

export type Template = {
  id: string;
  name: string;
  description: string;
  category: string;
  isPremium: boolean;
  tags: string[];
  pace: "slow" | "medium" | "fast" | "hyper";
  scenes: number;
  duration: string;
};

export const templates: Template[] = [
  {
    id: "tpl_hook_punchline",
    name: "Hook → Punchline",
    description:
      "Open with a 0.8s hook, build with three 1.5s b-roll beats, finish on a punchline close-up. Great for product reveals.",
    category: "product",
    isPremium: false,
    tags: ["pace:fast", "product", "hook"],
    pace: "fast",
    scenes: 5,
    duration: "5.3s",
  },
  {
    id: "tpl_talking_head",
    name: "Talking Head + B-roll",
    description:
      "3s talking-head intro, alternating b-roll cuts every 1.2s synced to a beat. Best for explainer content.",
    category: "education",
    isPremium: false,
    tags: ["pace:medium", "education", "talking_head"],
    pace: "medium",
    scenes: 8,
    duration: "12.6s",
  },
  {
    id: "tpl_hype_reel",
    name: "Hype Reel",
    description:
      "Sub-second cuts on every beat with flash transitions. For sports, fashion, action.",
    category: "action",
    isPremium: true,
    tags: ["pace:hyper", "action", "flash"],
    pace: "hyper",
    scenes: 14,
    duration: "9.8s",
  },
  {
    id: "tpl_chill_vlog",
    name: "Chill Vlog",
    description:
      "Long 4s shots with slow dissolves and ambient color grade. Calm, narrative pacing.",
    category: "lifestyle",
    isPremium: false,
    tags: ["pace:slow", "lifestyle", "dissolve"],
    pace: "slow",
    scenes: 4,
    duration: "16.0s",
  },
];

export type Plan = {
  code: string;
  name: string;
  priceMonthly: number;
  priceYearly: number;
  features: string[];
  highlight?: boolean;
  cta: string;
};

export const plans: Plan[] = [
  {
    code: "free",
    name: "Free",
    priceMonthly: 0,
    priceYearly: 0,
    cta: "Start free",
    features: [
      "3 projects",
      "720p rendering",
      "Watermark on export",
      "Community templates",
    ],
  },
  {
    code: "creator",
    name: "Creator",
    priceMonthly: 12,
    priceYearly: 120,
    highlight: true,
    cta: "Go Creator",
    features: [
      "Unlimited projects",
      "1080p rendering",
      "No watermark",
      "Premium templates",
      "Priority queue",
      "10 GB storage",
    ],
  },
  {
    code: "pro",
    name: "Pro",
    priceMonthly: 29,
    priceYearly: 290,
    cta: "Go Pro",
    features: [
      "Everything in Creator",
      "4K rendering",
      "Cloud rendering (2x GPU)",
      "Team workspace (5 seats)",
      "100 GB storage",
      "Early access features",
    ],
  },
];

// A sample blueprint scene timeline shown in the live visualizer.
export type ScenePreview = {
  index: number;
  duration: number;
  shotType: string;
  motion: string;
  caption?: string;
  color: string; // tailwind gradient classes
  transition: "cut" | "flash" | "dissolve";
};

export const sampleScenes: ScenePreview[] = [
  {
    index: 0,
    duration: 0.8,
    shotType: "Wide",
    motion: "Zoom in",
    caption: "WAIT FOR IT",
    color: "from-fuchsia-500 to-purple-600",
    transition: "cut",
  },
  {
    index: 1,
    duration: 1.4,
    shotType: "Close-up",
    motion: "Static",
    caption: "this changes everything",
    color: "from-rose-500 to-orange-500",
    transition: "flash",
  },
  {
    index: 2,
    duration: 1.2,
    shotType: "B-roll",
    motion: "Pan right",
    color: "from-amber-500 to-pink-600",
    transition: "cut",
  },
  {
    index: 3,
    duration: 0.6,
    shotType: "Close-up",
    motion: "Handheld",
    caption: "MIND BLOWN",
    color: "from-purple-600 to-fuchsia-500",
    transition: "flash",
  },
  {
    index: 4,
    duration: 1.8,
    shotType: "Product",
    motion: "Orbit",
    caption: "available now",
    color: "from-pink-600 to-rose-500",
    transition: "dissolve",
  },
];

export type AnalysisFeature = {
  icon: string;
  title: string;
  description: string;
  category: "video" | "audio" | "caption" | "visual";
};

export const analysisFeatures: AnalysisFeature[] = [
  {
    icon: "Scissors",
    title: "Scene Cuts",
    description:
      "Frame-accurate scene-boundary detection via HSV histogram analysis. Knows exactly where every cut lands.",
    category: "video",
  },
  {
    icon: "Move",
    title: "Camera Motion",
    description:
      "Lucas-Kanade optical flow classifies pan, tilt, zoom, handheld, dolly, orbit — for every sampled frame.",
    category: "video",
  },
  {
    icon: "ZoomIn",
    title: "Zoom & Shake",
    description:
      "Radial-flow divergence isolates zoom factor; high-frequency variance flags handheld shake intensity.",
    category: "video",
  },
  {
    icon: "Music",
    title: "Beat Detection",
    description:
      "librosa extracts BPM, beat times, and onset envelopes — your cuts can land exactly on the beat.",
    category: "audio",
  },
  {
    icon: "Type",
    title: "Caption OCR",
    description:
      "EasyOCR reads on-screen text, groups frames into caption blocks, and recovers font size + color.",
    category: "caption",
  },
  {
    icon: "Sparkles",
    title: "Caption Style",
    description:
      "Position, animation, font weight, uppercase, stroke width — every visual choice reverse-engineered.",
    category: "caption",
  },
  {
    icon: "Palette",
    title: "Color Grading",
    description:
      "K-means clustering over sampled frames recovers the dominant palette, brightness, and saturation profile.",
    category: "visual",
  },
  {
    icon: "User",
    title: "Faces & Pose",
    description:
      "YOLO + Haar cascades + MediaPipe pose detect subjects, count faces, and trace skeletal motion.",
    category: "visual",
  },
  {
    icon: "Gauge",
    title: "Editing Pace",
    description:
      "Average shot duration classifies the edit as slow / medium / fast / hyper — the soul of the viral style.",
    category: "video",
  },
];

export const stats = [
  { label: "API endpoints", value: "46" },
  { label: "Analysis passes", value: "7" },
  { label: "Test coverage", value: "79%" },
  { label: "AI providers", value: "4" },
];
