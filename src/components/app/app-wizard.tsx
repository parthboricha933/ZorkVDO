"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Film,
  Wand2,
  Scissors,
  Download,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ArrowRight,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { api, ApiError } from "@/lib/api";
import type {
  VideoPublic,
  JobPublic,
  BlueprintPublic,
  ProjectPublic,
} from "@/lib/api";

type Step = "upload" | "analyzing" | "blueprint" | "clips" | "rendering" | "done";

const STEPS: Array<{ id: Step; label: string; icon: typeof Upload }> = [
  { id: "upload", label: "Upload viral video", icon: Upload },
  { id: "analyzing", label: "AI analyzing", icon: Wand2 },
  { id: "blueprint", label: "View blueprint", icon: Film },
  { id: "clips", label: "Upload your clips", icon: Scissors },
  { id: "rendering", label: "Rendering", icon: Loader2 },
  { id: "done", label: "Download", icon: Download },
];

export function AppWizard() {
  const [step, setStep] = useState<Step>("upload");
  const [project, setProject] = useState<ProjectPublic | null>(null);
  const [sourceVideo, setSourceVideo] = useState<VideoPublic | null>(null);
  const [analysisJob, setAnalysisJob] = useState<JobPublic | null>(null);
  const [blueprint, setBlueprint] = useState<BlueprintPublic | null>(null);
  const [userClips, setUserClips] = useState<VideoPublic[]>([]);
  const [renderJob, setRenderJob] = useState<JobPublic | null>(null);
  const [outputVideo, setOutputVideo] = useState<VideoPublic | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<
    "unknown" | "online" | "offline"
  >("unknown");

  // Check backend on mount — retries 3 times before showing "offline"
  useEffect(() => {
    let cancelled = false;
    const checkHealth = async (attempt: number) => {
      try {
        await api.health();
        if (!cancelled) setBackendStatus("online");
      } catch (e) {
        if (cancelled) return;
        if (attempt < 3) {
          // Retry after 2s
          setTimeout(() => checkHealth(attempt + 1), 2000);
        } else {
          setBackendStatus("offline");
        }
      }
    };
    checkHealth(0);
    return () => {
      cancelled = true;
    };
  }, []);

  const stepIndex = STEPS.findIndex((s) => s.id === step);

  const handleUploadSource = useCallback(async (file: File) => {
    setError(null);
    try {
      const proj = await api.createProject(
        `Viral analysis — ${file.name}`,
        "Auto-created by ZorkVDO"
      );
      setProject(proj);

      const video = await api.uploadVideo(file, "source");
      setSourceVideo(video);

      setStep("analyzing");
      // Analysis is sync (blocking) — goes directly to Railway, no Vercel timeout
      const job = await api.startAnalysis(
        video.id,
        `Blueprint from ${file.name}`,
        true
      );
      setAnalysisJob(job);

      // Sync mode returns the completed job immediately
      if (job.status === "succeeded" && job.result?.blueprint_id) {
        const bp = await api.getBlueprint(
          job.result.blueprint_id as string
        );
        setBlueprint(bp);
        setStep("blueprint");
      } else if (job.status === "failed") {
        throw new Error(job.error || "Analysis failed");
      }
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? `${e.message}: ${JSON.stringify(e.details).slice(0, 200)}`
          : e instanceof Error
          ? e.message
          : "Unknown error";
      setError(msg);
      setStep("upload");
    }
  }, []);

  const [clipUploadProgress, setClipUploadProgress] = useState<{
    current: number;
    total: number;
    fileName: string;
  } | null>(null);

  const handleUploadClips = useCallback(async (files: File[]) => {
    setError(null);
    setClipUploadProgress({ current: 0, total: files.length, fileName: files[0]?.name || "" });
    try {
      const uploaded: VideoPublic[] = [];
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setClipUploadProgress({ current: i + 1, total: files.length, fileName: file.name });
        const video = await api.uploadVideo(file, "user_clip");
        uploaded.push(video);
      }
      setUserClips((prev) => [...prev, ...uploaded]);
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? `${e.message}: ${JSON.stringify(e.details).slice(0, 200)}`
          : e instanceof Error
          ? e.message
          : "Upload failed";
      setError(msg);
    } finally {
      setClipUploadProgress(null);
    }
  }, []);

  const handleRender = useCallback(async () => {
    if (!blueprint || userClips.length === 0) return;
    setError(null);
    setStep("rendering");
    try {
      // Create a fresh project right before rendering (in-memory DB may
      // have been wiped between steps on Railway)
      const freshProject = await api.createProject(
        `Render — ${blueprint.name}`,
        "Auto-created for render"
      );
      setProject(freshProject);

      const clipMapping = blueprint.scenes.map((scene, i) => ({
        scene_index: scene.index,
        clip_id: userClips[i % userClips.length].id,
        suggested_start: 0.0,
        suggested_end: scene.duration,
      }));

      const job = await api.startRender(
        freshProject.id,
        blueprint.id,
        clipMapping,
        "high",
        "9:16"
      );
      setRenderJob(job);

      // Render is sync (blocking) — the result comes back in the same request
      if (job.status === "succeeded" && job.result?.output_video_id) {
        const out = await api.getVideo(
          job.result.output_video_id as string
        );
        setOutputVideo(out);
        setStep("done");
      } else if (job.status === "failed") {
        throw new Error(job.error || "Render failed");
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Render failed";
      setError(msg);
      setStep("blueprint");
    }
  }, [project, blueprint, userClips]);

  const handleReset = useCallback(() => {
    setStep("upload");
    setProject(null);
    setSourceVideo(null);
    setAnalysisJob(null);
    setBlueprint(null);
    setUserClips([]);
    setRenderJob(null);
    setOutputVideo(null);
    setError(null);
  }, []);

  return (
    <section id="top" className="relative pt-24 pb-20 min-h-screen">
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -left-40 h-[40rem] w-[40rem] rounded-full bg-fuchsia-600/20 blur-3xl" />
        <div className="absolute top-20 -right-40 h-[35rem] w-[35rem] rounded-full bg-purple-700/20 blur-3xl" />
      </div>

      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-5xl font-bold text-white mb-3">
            Zork<span className="text-fuchsia-400">VDO</span>
          </h1>
          <p className="text-zinc-400 text-sm sm:text-base">
            Upload a viral video → AI reverse-engineers the editing style →
            drop in your clips → get a brand-new video with the same energy.
          </p>
        </div>

        {backendStatus === "offline" && (
          <div className="mb-6 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-medium">Backend is taking longer than usual to respond</p>
                <p className="text-xs text-amber-200/80 mt-1">
                  The backend at <code className="font-mono break-all">{api.url}</code> might be
                  cold-starting on Railway (free tier spins down after inactivity).
                  The first request can take 30-60s. Try again in a moment.
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  className="mt-3 border-amber-500/30 text-amber-200 hover:bg-amber-500/20"
                  onClick={() => {
                    setBackendStatus("unknown");
                    api.health()
                      .then(() => setBackendStatus("online"))
                      .catch(() => setBackendStatus("offline"));
                  }}
                >
                  <RefreshCw className="mr-1.5 h-3 w-3" />
                  Retry connection
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="mb-10 flex items-center justify-center gap-1 sm:gap-2 overflow-x-auto pb-2">
          {STEPS.map((s, i) => {
            const Icon = s.icon;
            const isDone = i < stepIndex;
            const isActive = i === stepIndex;
            return (
              <div key={s.id} className="flex items-center">
                <div
                  className={cn(
                    "flex items-center gap-2 px-2 sm:px-3 py-1.5 rounded-full border text-xs font-medium transition-all flex-shrink-0",
                    isActive
                      ? "border-fuchsia-500/40 bg-fuchsia-500/15 text-white"
                      : isDone
                      ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                      : "border-white/10 bg-white/5 text-zinc-500"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-3.5 w-3.5",
                      isActive && s.id === "analyzing" && "animate-spin",
                      isActive && s.id === "rendering" && "animate-spin"
                    )}
                  />
                  <span className="hidden sm:inline">{s.label}</span>
                </div>
                {i < STEPS.length - 1 && (
                  <ArrowRight className="h-3 w-3 mx-1 text-zinc-700 flex-shrink-0" />
                )}
              </div>
            );
          })}
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-medium">Something went wrong</p>
                <p className="text-xs text-rose-200/80 mt-1 font-mono break-all">
                  {error}
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  className="mt-3 border-rose-500/30 text-rose-200 hover:bg-rose-500/20"
                  onClick={() => setError(null)}
                >
                  Dismiss
                </Button>
              </div>
            </div>
          </div>
        )}

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3 }}
          >
            {step === "upload" && (
              <UploadStep
                onUpload={handleUploadSource}
                backendOnline={backendStatus === "online"}
              />
            )}
            {step === "analyzing" && (
              <AnalyzingStep job={analysisJob} video={sourceVideo} />
            )}
            {step === "blueprint" && blueprint && (
              <BlueprintStep
                blueprint={blueprint}
                userClips={userClips}
                onUploadClips={handleUploadClips}
                onRender={handleRender}
                clipUploadProgress={clipUploadProgress}
              />
            )}
            {step === "rendering" && <RenderingStep job={renderJob} />}
            {step === "done" && outputVideo && (
              <DoneStep
                video={outputVideo}
                blueprint={blueprint}
                onReset={handleReset}
              />
            )}
          </motion.div>
        </AnimatePresence>

        {step !== "upload" && step !== "done" && (
          <div className="mt-8 text-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="text-zinc-500 hover:text-zinc-300"
            >
              <ArrowLeft className="mr-1 h-3 w-3" />
              Start over
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}

function UploadStep({
  onUpload,
  backendOnline,
}: {
  onUpload: (file: File) => void;
  backendOnline: boolean;
}) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File | undefined) => {
    if (!file) return;
    if (!file.type.startsWith("video/")) {
      alert("Please upload a video file");
      return;
    }
    onUpload(file);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFile(e.dataTransfer.files[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "relative rounded-2xl border-2 border-dashed p-12 text-center cursor-pointer transition-all",
          dragging
            ? "border-fuchsia-500 bg-fuchsia-500/10"
            : "border-white/15 bg-zinc-900/40 hover:border-fuchsia-500/50 hover:bg-zinc-900/60"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-fuchsia-500 to-rose-500 flex items-center justify-center shadow-lg shadow-fuchsia-500/30">
            <Upload className="h-8 w-8 text-white" />
          </div>
          <div>
            <p className="text-lg font-semibold text-white">
              Drop a viral video here
            </p>
            <p className="text-sm text-zinc-400 mt-1">
              or click to browse — MP4, MOV, WebM up to 500MB
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2 text-xs text-zinc-500">
            <span>The AI will analyze:</span>
            <Badge variant="outline" className="border-white/10 text-zinc-400">
              scene cuts
            </Badge>
            <Badge variant="outline" className="border-white/10 text-zinc-400">
              beats
            </Badge>
            <Badge variant="outline" className="border-white/10 text-zinc-400">
              captions
            </Badge>
            <Badge variant="outline" className="border-white/10 text-zinc-400">
              color grade
            </Badge>
            <Badge variant="outline" className="border-white/10 text-zinc-400">
              camera motion
            </Badge>
          </div>
        </div>
      </div>
      <p className="mt-4 text-center text-xs text-zinc-600">
        Demo mode is on — no sign-in required. Videos are processed locally and
        not stored permanently.
      </p>
    </div>
  );
}

function AnalyzingStep({
  job,
  video,
}: {
  job: JobPublic | null;
  video: VideoPublic | null;
}) {
  const passes = [
    "Probing container (ffmpeg)",
    "Detecting scene cuts (OpenCV)",
    "Extracting camera motion (optical flow)",
    "Detecting beats (librosa)",
    "Reading captions (EasyOCR)",
    "Clustering dominant colors",
    "Detecting objects (YOLOv11)",
    "Building blueprint JSON",
  ];
  const currentPass =
    job?.progress !== undefined
      ? Math.min(
          Math.floor((job.progress || 0) * passes.length),
          passes.length - 1
        )
      : 0;

  return (
    <div className="max-w-2xl mx-auto text-center">
      <div className="relative h-24 w-24 mx-auto mb-6">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 rounded-full border-4 border-fuchsia-500/20 border-t-fuchsia-500"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <Wand2 className="h-10 w-10 text-fuchsia-400" />
        </div>
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">
        Analyzing your video
      </h2>
      <p className="text-zinc-400 text-sm mb-6">{video?.filename}</p>
      <div className="space-y-2 max-w-md mx-auto text-left">
        {passes.map((pass, i) => (
          <div
            key={pass}
            className={cn(
              "flex items-center gap-2 text-sm",
              i < currentPass
                ? "text-emerald-300"
                : i === currentPass
                ? "text-white"
                : "text-zinc-600"
            )}
          >
            {i < currentPass ? (
              <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
            ) : i === currentPass ? (
              <Loader2 className="h-4 w-4 flex-shrink-0 animate-spin" />
            ) : (
              <div className="h-4 w-4 rounded-full border border-zinc-700 flex-shrink-0" />
            )}
            {pass}
          </div>
        ))}
      </div>
      <p className="mt-6 text-xs text-zinc-600">
        Status: {job?.status || "starting"} · This may take 30-60 seconds
      </p>
    </div>
  );
}

function BlueprintStep({
  blueprint,
  userClips,
  onUploadClips,
  onRender,
  clipUploadProgress,
}: {
  blueprint: BlueprintPublic;
  userClips: VideoPublic[];
  onUploadClips: (files: File[]) => void;
  onRender: () => void;
  clipUploadProgress: { current: number; total: number; fileName: string } | null;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    // Accept files that are either:
    // 1. Typed as video/* by the browser, OR
    // 2. Have a video file extension (some browsers/OSes report empty type)
    const videoExtensions = [".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"];
    const valid = Array.from(files).filter((f) => {
      if (f.type.startsWith("video/")) return true;
      const name = f.name.toLowerCase();
      return videoExtensions.some((ext) => name.endsWith(ext));
    });
    if (valid.length > 0) {
      onUploadClips(valid);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-zinc-900/40 backdrop-blur-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white">{blueprint.name}</h2>
            <p className="text-sm text-zinc-400">
              {blueprint.scenes.length} scenes ·{" "}
              {blueprint.overall_duration.toFixed(1)}s · pace: {blueprint.pace}
            </p>
          </div>
          <Badge
            variant="outline"
            className="border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
          >
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Ready
          </Badge>
        </div>

        <div className="space-y-1.5">
          {blueprint.scenes.map((scene) => (
            <div
              key={scene.index}
              className="flex items-center gap-3 rounded-lg border border-white/5 bg-white/[0.02] p-2"
            >
              <div className="text-xs font-mono text-zinc-500 w-8">
                {String(scene.index + 1).padStart(2, "0")}
              </div>
              <div
                className="h-8 rounded flex items-center justify-center text-[10px] font-mono text-white/80"
                style={{
                  width: `${Math.max(40, scene.duration * 30)}px`,
                  background: `linear-gradient(135deg, ${
                    scene.dominant_colors_hex[0] || "#a855f7"
                  }, ${scene.dominant_colors_hex[1] || "#ec4899"})`,
                }}
              >
                {scene.duration.toFixed(1)}s
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs text-zinc-300 truncate">
                  {scene.shot_type} · {scene.camera_motion}
                </div>
                <div className="text-[10px] text-zinc-500 truncate">
                  {scene.clip_suggestion.description}
                </div>
              </div>
              {scene.captions.length > 0 && (
                <Badge
                  variant="outline"
                  className="border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-200 text-[10px]"
                >
                  caption
                </Badge>
              )}
            </div>
          ))}
        </div>

        {blueprint.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1">
            {blueprint.tags.map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="border-white/10 text-zinc-500 text-[10px] font-mono"
              >
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-white/10 bg-zinc-900/40 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-white">
              Upload your own clips
            </h3>
            <p className="text-sm text-zinc-400">
              The AI will map your clips into the blueprint's scene slots.
            </p>
          </div>
          {userClips.length > 0 && (
            <Badge
              variant="outline"
              className="border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
            >
              {userClips.length} uploaded
            </Badge>
          )}
        </div>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            handleFiles(e.dataTransfer.files);
          }}
          onClick={() => inputRef.current?.click()}
          className={cn(
            "rounded-xl border-2 border-dashed p-6 text-center cursor-pointer transition-all",
            dragging
              ? "border-fuchsia-500 bg-fuchsia-500/10"
              : "border-white/15 hover:border-fuchsia-500/50"
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept="video/*,.mp4,.mov,.webm,.mkv,.avi,.m4v"
            multiple
            className="hidden"
            onChange={(e) => {
              handleFiles(e.target.files);
              // Reset input so the same file can be selected again
              e.target.value = "";
            }}
          />
          {clipUploadProgress ? (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="h-6 w-6 text-fuchsia-400 animate-spin" />
              <p className="text-sm text-zinc-300">
                Uploading {clipUploadProgress.current}/{clipUploadProgress.total}:{" "}
                <span className="text-zinc-400">{clipUploadProgress.fileName}</span>
              </p>
            </div>
          ) : (
            <>
              <Upload className="h-6 w-6 text-zinc-400 mx-auto mb-2" />
              <p className="text-sm text-zinc-300">
                Drop clips here or click to browse (multiple OK)
              </p>
            </>
          )}
        </div>

        {userClips.length > 0 && (
          <div className="mt-4 space-y-1.5 max-h-48 overflow-y-auto">
            {userClips.map((clip) => (
              <div
                key={clip.id}
                className="flex items-center gap-2 rounded-lg border border-white/5 bg-white/[0.02] p-2 text-xs"
              >
                <Film className="h-3.5 w-3.5 text-fuchsia-400 flex-shrink-0" />
                <span className="flex-1 truncate text-zinc-300">
                  {clip.filename}
                </span>
                <span className="text-zinc-600 font-mono">
                  {(clip.size_bytes / 1024 / 1024).toFixed(1)} MB
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="text-center">
        <Button
          size="lg"
          disabled={userClips.length === 0}
          onClick={onRender}
          className="bg-gradient-to-r from-fuchsia-500 to-rose-500 hover:from-fuchsia-400 hover:to-rose-400 text-white border-0 shadow-xl shadow-fuchsia-500/30 px-8 h-12 text-base disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Wand2 className="mr-2 h-4 w-4" />
          Render new video
          {userClips.length === 0
            ? " (upload clips first)"
            : ` from ${userClips.length} clip${
                userClips.length > 1 ? "s" : ""
              }`}
        </Button>
      </div>
    </div>
  );
}

function RenderingStep({ job }: { job: JobPublic | null }) {
  const phases = [
    "Downloading clips",
    "Trimming + scaling per scene",
    "Concatenating segments",
    "Burning in captions",
    "Uploading output",
  ];
  const currentPhase =
    job?.progress !== undefined
      ? Math.min(
          Math.floor((job.progress || 0) * phases.length),
          phases.length - 1
        )
      : 0;

  return (
    <div className="max-w-2xl mx-auto text-center">
      <div className="relative h-24 w-24 mx-auto mb-6">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 rounded-full border-4 border-rose-500/20 border-t-rose-500"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <Film className="h-10 w-10 text-rose-400" />
        </div>
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">
        Rendering your video
      </h2>
      <p className="text-zinc-400 text-sm mb-6">
        FFmpeg is assembling your new video using the blueprint's style.
      </p>
      <div className="space-y-2 max-w-md mx-auto text-left">
        {phases.map((phase, i) => (
          <div
            key={phase}
            className={cn(
              "flex items-center gap-2 text-sm",
              i < currentPhase
                ? "text-emerald-300"
                : i === currentPhase
                ? "text-white"
                : "text-zinc-600"
            )}
          >
            {i < currentPhase ? (
              <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
            ) : i === currentPhase ? (
              <Loader2 className="h-4 w-4 flex-shrink-0 animate-spin" />
            ) : (
              <div className="h-4 w-4 rounded-full border border-zinc-700 flex-shrink-0" />
            )}
            {phase}
          </div>
        ))}
      </div>
      <p className="mt-6 text-xs text-zinc-600">
        Status: {job?.status || "starting"}
      </p>
    </div>
  );
}

function DoneStep({
  video,
  blueprint,
  onReset,
}: {
  video: VideoPublic;
  blueprint: BlueprintPublic | null;
  onReset: () => void;
}) {
  return (
    <div className="max-w-2xl mx-auto text-center">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200 }}
        className="h-20 w-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-xl shadow-emerald-500/30"
      >
        <CheckCircle2 className="h-12 w-12 text-white" />
      </motion.div>
      <h2 className="text-3xl font-bold text-white mb-2">
        Your video is ready!
      </h2>
      <p className="text-zinc-400 text-sm mb-8">
        Generated from {blueprint?.scenes.length || 0} blueprint scenes.
        Download it below.
      </p>

      <div className="rounded-2xl border border-white/10 bg-zinc-900/60 overflow-hidden mb-6">
        <div className="aspect-[9/16] max-h-[500px] bg-black flex items-center justify-center">
          <video
            src={api.downloadUrl(video.id)}
            controls
            className="max-h-full max-w-full"
          />
        </div>
        <div className="p-4 flex items-center justify-between">
          <div className="text-left">
            <p className="text-sm font-medium text-white">{video.filename}</p>
            <p className="text-xs text-zinc-500">
              {video.width}×{video.height} ·{" "}
              {video.duration_seconds?.toFixed(1)}s ·{" "}
              {(video.size_bytes / 1024 / 1024).toFixed(1)} MB
            </p>
          </div>
          <a href={api.downloadUrl(video.id)} download>
            <Button className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white border-0">
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
          </a>
        </div>
      </div>

      <Button
        variant="outline"
        onClick={onReset}
        className="border-white/10 bg-white/5 text-zinc-300 hover:bg-white/10"
      >
        <RefreshCw className="mr-2 h-4 w-4" />
        Make another video
      </Button>
    </div>
  );
}
