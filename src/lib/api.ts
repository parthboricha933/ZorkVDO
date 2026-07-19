/**
 * ZorkVDO API client.
 *
 * Two-mode operation:
 * - Small API calls (auth, projects, jobs, blueprints): go through the Vercel
 *   proxy at /api/v1/* (avoids DNS + CORS issues)
 * - File uploads: go DIRECTLY to the Railway backend (Vercel serverless
 *   functions have a 4.5MB body limit that rejects video files)
 *
 * The Railway URL for uploads is set via NEXT_PUBLIC_UPLOAD_URL env var.
 * For local dev, set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
 * to talk to the backend directly.
 */

// Proxy URL for small API calls (same-origin, no DNS/CORS issues)
const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

// Direct Railway URL for file uploads (bypasses Vercel's 4.5MB limit)
const UPLOAD_URL =
  process.env.NEXT_PUBLIC_UPLOAD_URL || "https://zorkvdo-production.up.railway.app/api/v1";

export interface VideoPublic {
  id: string;
  owner_id: string;
  kind: string; // source | user_clip | output
  filename: string;
  content_type: string;
  size_bytes: number;
  storage_key: string;
  storage_url: string;
  duration_seconds: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  analysis_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobPublic {
  id: string;
  user_id: string;
  project_id: string | null;
  job_type: string; // analyze | render
  status: string; // queued | running | succeeded | failed | cancelled
  progress: number;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  result: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface BlueprintScene {
  index: number;
  start: number;
  end: number;
  duration: number;
  shot_type: string;
  camera_motion: string;
  zoom_factor: number;
  captions: Array<{
    text: string;
    start: number;
    end: number;
    position: string;
    animation: string;
    font_size: number;
    color_hex: string;
  }>;
  clip_suggestion: {
    role: string;
    preferred_shot: string;
    duration_range: [number, number];
    motion: string;
    description: string;
    keywords: string[];
  };
  dominant_colors_hex: string[];
}

export interface BlueprintPublic {
  id: string;
  owner_id: string;
  name: string;
  source_video_id: string;
  pace: string;
  overall_duration: number;
  scenes: BlueprintScene[];
  music: { bpm: number | null; energy: number; beat_times: number[] } | null;
  color_grade: string;
  tags: string[];
  notes: string;
  schema_version: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectPublic {
  id: string;
  name: string;
  description: string;
  status: string;
  owner_id: string;
  source_video_id: string | null;
  blueprint_id: string | null;
  output_video_id: string | null;
  created_at: string;
  updated_at: string;
}

class ApiError extends Error {
  constructor(public status: number, message: string, public details?: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${path}`;

  // Timeout helper — aborts the fetch after `timeoutMs`
  const timeoutMs = (options.signal ? 120000 : 15000); // 15s default, 2min for uploads
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  // If caller provided their own signal, we respect it too
  if (options.signal) {
    options.signal.addEventListener("abort", () => controller.abort());
  }

  try {
    const resp = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
    clearTimeout(timeoutId);
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      let details: unknown;
      try {
        details = JSON.parse(text);
      } catch {
        details = text.slice(0, 200);
      }
      throw new ApiError(resp.status, `API ${resp.status}`, details);
    }
    if (resp.status === 204) return undefined as T;
    return (await resp.json()) as T;
  } catch (e: unknown) {
    clearTimeout(timeoutId);
    if (e instanceof ApiError) throw e;
    // Network error or timeout
    const isTimeout = e instanceof Error && e.name === "AbortError";
    throw new ApiError(0, isTimeout ? "Request timed out" : "Cannot reach backend", {
      hint: isTimeout
        ? "Backend is slow to respond. It may be cold-starting on Railway."
        : "Make sure the FastAPI backend is running",
      url,
    });
  }
}

export const api = {
  url: API_URL,

  async health() {
    // Retry up to 3 times with 2s delay — handles Railway cold starts
    let lastError: unknown;
    for (let i = 0; i < 3; i++) {
      try {
        return await request<{ status: string }>("/health");
      } catch (e) {
        lastError = e;
        if (i < 2) await new Promise((r) => setTimeout(r, 2000));
      }
    }
    throw lastError;
  },

  async getMe() {
    return request<{
      id: string;
      email: string;
      display_name: string;
      plan: string;
    }>("/auth/me");
  },

  async createProject(name: string, description = "") {
    return request<ProjectPublic>("/projects", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    });
  },

  async uploadVideo(file: File, kind: "source" | "user_clip" = "source") {
    const form = new FormData();
    form.append("file", file);
    form.append("kind", kind);

    // Try direct Railway first, fall back to Vercel proxy for small files
    try {
      const resp = await fetch(`${UPLOAD_URL}/videos/upload`, {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(120000),
      });
      if (resp.ok) return (await resp.json()) as VideoPublic;
      const text = await resp.text().catch(() => "");
      throw new ApiError(resp.status, `Upload failed ${resp.status}`, text);
    } catch (directErr) {
      if (directErr instanceof ApiError && directErr.status !== 0) throw directErr;
      // Network error — try via Vercel proxy (only works for files < 4.5MB)
    }

    // Fallback: Vercel proxy (may fail for large files)
    try {
      const form2 = new FormData();
      form2.append("file", file);
      form2.append("kind", kind);
      const resp = await fetch(`${API_URL}/videos/upload`, {
        method: "POST",
        body: form2,
        signal: AbortSignal.timeout(120000),
      });
      if (resp.ok) return (await resp.json()) as VideoPublic;
      const text = await resp.text().catch(() => "");
      throw new ApiError(resp.status, `Upload failed ${resp.status}`, text);
    } catch (e) {
      if (e instanceof ApiError) throw e;
      throw new ApiError(0, "Cannot reach backend for upload", {
        hint: "Your network may not be able to reach Railway. Try a different network or VPN.",
      });
    }
  },

  async listVideos(kind?: string) {
    const query = kind ? `?kind=${kind}` : "";
    return request<VideoPublic[]>(`/videos${query}`);
  },

  async getVideo(videoId: string) {
    // Try direct, fall back to proxy
    try {
      const r = await fetch(`${UPLOAD_URL}/videos/${videoId}`);
      if (r.ok) return await r.json() as VideoPublic;
    } catch {}
    return request<VideoPublic>(`/videos/${videoId}`);
  },

  async startAnalysis(
    videoId: string,
    blueprintName: string,
    sync = false
  ) {
    const body = JSON.stringify({ blueprint_name: blueprintName });

    // Try direct Railway first
    try {
      const resp = await fetch(`${UPLOAD_URL}/jobs/analyze/${videoId}?sync=true`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: AbortSignal.timeout(180000), // 3 min for analysis
      });
      if (resp.ok) return (await resp.json()) as JobPublic;
      const text = await resp.text().catch(() => "");
      throw new ApiError(resp.status, `Analysis failed ${resp.status}`, text);
    } catch (directErr) {
      if (directErr instanceof ApiError && directErr.status !== 0) throw directErr;
    }

    // Fallback: Vercel proxy (may timeout for long analysis)
    try {
      const resp = await fetch(`${API_URL}/jobs/analyze/${videoId}?sync=true`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: AbortSignal.timeout(180000),
      });
      if (resp.ok) return (await resp.json()) as JobPublic;
      const text = await resp.text().catch(() => "");
      throw new ApiError(resp.status, `Analysis failed ${resp.status}`, text);
    } catch (e) {
      if (e instanceof ApiError) throw e;
      throw new ApiError(0, "Cannot reach backend for analysis", {
        hint: "Your network may not be able to reach Railway.",
      });
    }
  },

  async startRender(
    projectId: string,
    blueprintId: string,
    clipMapping: Array<{
      scene_index: number;
      clip_id: string;
      suggested_start: number;
      suggested_end: number | null;
    }>,
    quality = "high",
    aspectRatio: string | null = null
  ) {
    // Try direct Railway first, fall back to Vercel proxy
    const body = JSON.stringify({
      project_id: projectId,
      blueprint_id: blueprintId,
      clip_mapping: clipMapping,
      quality,
      aspect_ratio: aspectRatio,
    });

    // Attempt 1: Direct to Railway (fast, no proxy overhead)
    try {
      const resp = await fetch(`${UPLOAD_URL}/jobs/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: AbortSignal.timeout(120000), // 2 min timeout
      });
      if (resp.ok) return (await resp.json()) as JobPublic;
      const text = await resp.text().catch(() => "");
      throw new ApiError(resp.status, `Render failed ${resp.status}`, text);
    } catch (directErr) {
      // If it's a non-network error (like 404), don't retry via proxy
      if (directErr instanceof ApiError && directErr.status !== 0) {
        throw directErr;
      }
      // Network error — try via Vercel proxy as fallback
    }

    // Attempt 2: Via Vercel proxy (handles DNS issues, but has 10s timeout)
    try {
      const resp = await fetch(`${API_URL}/jobs/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        signal: AbortSignal.timeout(120000),
      });
      if (resp.ok) return (await resp.json()) as JobPublic;
      const text = await resp.text().catch(() => "");
      throw new ApiError(resp.status, `Render failed ${resp.status}`, text);
    } catch (proxyErr) {
      if (proxyErr instanceof ApiError) throw proxyErr;
      throw new ApiError(0, "Cannot reach backend for render (tried direct + proxy)", {
        hint: "Your network may not be able to reach Railway. Try a different network or VPN.",
      });
    }
  },

  async getJob(jobId: string) {
    // Try direct, fall back to proxy
    try {
      const r = await fetch(`${UPLOAD_URL}/jobs/${jobId}`);
      if (r.ok) return await r.json() as JobPublic;
    } catch {}
    // Fallback: proxy
    return request<JobPublic>(`/jobs/${jobId}`);
  },

  async getBlueprint(blueprintId: string) {
    // Try direct, fall back to proxy
    try {
      const r = await fetch(`${UPLOAD_URL}/blueprints/${blueprintId}`);
      if (r.ok) return await r.json() as BlueprintPublic;
    } catch {}
    // Fallback: proxy
    return request<BlueprintPublic>(`/blueprints/${blueprintId}`);
  },

  async pollJob(
    jobId: string,
    onUpdate: (job: JobPublic) => void,
    intervalMs = 1500,
    timeoutMs = 5 * 60 * 1000
  ): Promise<JobPublic> {
    const start = Date.now();
    return new Promise((resolve, reject) => {
      const tick = async () => {
        try {
          const job = await api.getJob(jobId);
          onUpdate(job);
          if (job.status === "succeeded") {
            resolve(job);
            return;
          }
          if (job.status === "failed") {
            reject(new Error(job.error || "Job failed"));
            return;
          }
          if (Date.now() - start > timeoutMs) {
            reject(new Error("Job timed out"));
            return;
          }
          setTimeout(tick, intervalMs);
        } catch (e) {
          reject(e);
        }
      };
      tick();
    });
  },

  downloadUrl(videoId: string) {
    // Downloads go directly to Railway (video files are too large for Vercel proxy)
    return `${UPLOAD_URL}/videos/${videoId}/download`;
  },
};

export { ApiError };
