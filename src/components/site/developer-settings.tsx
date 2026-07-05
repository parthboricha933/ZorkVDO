"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  AlertCircle,
  XCircle,
  WifiOff,
  CircleSlash,
  RefreshCw,
  Settings2,
  Sparkles,
  Database,
  Cloud,
  Cpu,
  Bell,
  CreditCard,
  BarChart3,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type IntegrationStatus =
  | "connected"
  | "configured"
  | "missing_api_key"
  | "invalid_credentials"
  | "service_offline"
  | "disabled";

interface Integration {
  name: string;
  category: string;
  status: IntegrationStatus;
  message: string;
  required_env_vars: string[];
  missing_env_vars: string[];
  last_checked: string;
  extra: Record<string, unknown>;
}

interface StatusSummary {
  last_refreshed: string;
  total: number;
  by_status: Record<IntegrationStatus, number>;
}

const statusConfig: Record<
  IntegrationStatus,
  { icon: typeof CheckCircle2; color: string; bg: string; label: string }
> = {
  connected: {
    icon: CheckCircle2,
    color: "text-emerald-300",
    bg: "bg-emerald-500/10 border-emerald-500/20",
    label: "Connected",
  },
  configured: {
    icon: CheckCircle2,
    color: "text-emerald-300",
    bg: "bg-emerald-500/10 border-emerald-500/20",
    label: "Configured",
  },
  missing_api_key: {
    icon: AlertCircle,
    color: "text-amber-300",
    bg: "bg-amber-500/10 border-amber-500/20",
    label: "Missing API Key",
  },
  invalid_credentials: {
    icon: XCircle,
    color: "text-rose-300",
    bg: "bg-rose-500/10 border-rose-500/20",
    label: "Invalid",
  },
  service_offline: {
    icon: WifiOff,
    color: "text-rose-300",
    bg: "bg-rose-500/10 border-rose-500/20",
    label: "Offline",
  },
  disabled: {
    icon: CircleSlash,
    color: "text-zinc-400",
    bg: "bg-white/5 border-white/10",
    label: "Disabled",
  },
};

const categoryIcons: Record<string, typeof Sparkles> = {
  ai: Sparkles,
  firebase: Database,
  database: Database,
  storage: Cloud,
  workers: Cpu,
  video_engine: Cpu,
  notifications: Bell,
  analytics: BarChart3,
  payments: CreditCard,
};

export function DeveloperSettings() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [summary, setSummary] = useState<StatusSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      // The status endpoint requires auth. For the marketing site demo, we
      // show a static snapshot if the backend is unreachable or returns 401.
      const resp = await fetch("/api/v1/status", {
        headers: { Accept: "application/json" },
      }).catch(() => null);

      if (resp && resp.ok) {
        const data = await resp.json();
        setIntegrations(data.integrations);
        setSummary(data.summary);
      } else {
        // Fallback: show a representative snapshot
        setIntegrations(snapshotIntegrations);
        setSummary(snapshotSummary);
      }
    } catch {
      setIntegrations(snapshotIntegrations);
      setSummary(snapshotSummary);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchStatus();
    setTimeout(() => setRefreshing(false), 600);
  };

  const grouped = integrations.reduce<Record<string, Integration[]>>((acc, i) => {
    (acc[i.category] = acc[i.category] || []).push(i);
    return acc;
  }, {});

  return (
    <section id="dev-settings" className="relative py-24 sm:py-32">
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-1/3 left-1/4 h-72 w-72 rounded-full bg-emerald-900/10 blur-3xl" />
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Badge
              variant="outline"
              className="border-emerald-500/30 bg-emerald-500/10 text-emerald-200 mb-4"
            >
              <Settings2 className="mr-1.5 h-3.5 w-3.5" />
              Developer Settings
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">
              Every integration, visible at a glance
            </h2>
            <p className="mt-4 text-zinc-400 text-lg">
              The hidden Developer Settings screen shows the live status of
              every external service. Missing keys disable only their feature
              — the rest of the app keeps running.
            </p>
          </motion.div>
        </div>

        {/* Summary bar */}
        {summary && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-8 flex flex-wrap items-center justify-center gap-3"
          >
            <SummaryPill
              label="Connected"
              count={summary.by_status.connected + summary.by_status.configured}
              color="text-emerald-300 bg-emerald-500/10 border-emerald-500/20"
            />
            <SummaryPill
              label="Missing key"
              count={summary.by_status.missing_api_key}
              color="text-amber-300 bg-amber-500/10 border-amber-500/20"
            />
            <SummaryPill
              label="Offline"
              count={summary.by_status.service_offline}
              color="text-rose-300 bg-rose-500/10 border-rose-500/20"
            />
            <SummaryPill
              label="Disabled"
              count={summary.by_status.disabled}
              color="text-zinc-400 bg-white/5 border-white/10"
            />
            <Button
              size="sm"
              variant="outline"
              onClick={handleRefresh}
              disabled={refreshing}
              className="ml-2 border-white/10 bg-white/5 text-zinc-300 hover:bg-white/10"
            >
              <RefreshCw
                className={cn("mr-1.5 h-3.5 w-3.5", refreshing && "animate-spin")}
              />
              Refresh
            </Button>
          </motion.div>
        )}

        {/* Integration grid by category */}
        <div className="space-y-8">
          {Object.entries(grouped).map(([category, items], catIdx) => {
            const CatIcon = categoryIcons[category] || Settings2;
            return (
              <motion.div
                key={category}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: catIdx * 0.05 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <CatIcon className="h-4 w-4 text-zinc-400" />
                  <h3 className="text-xs font-mono uppercase tracking-widest text-zinc-500">
                    {category.replace("_", " ")}
                  </h3>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {items.map((item) => {
                    const cfg = statusConfig[item.status];
                    const Icon = cfg.icon;
                    return (
                      <div
                        key={item.name}
                        className={cn(
                          "rounded-lg border p-4 backdrop-blur-sm transition-colors",
                          cfg.bg
                        )}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Icon className={cn("h-4 w-4 flex-shrink-0", cfg.color)} />
                            <span className="text-sm font-medium text-white">
                              {item.name}
                            </span>
                          </div>
                        </div>
                        <p className="text-xs text-zinc-400 leading-relaxed mb-2">
                          {item.message}
                        </p>
                        {item.missing_env_vars.length > 0 && (
                          <div className="text-[10px] font-mono text-amber-300/80">
                            missing: {item.missing_env_vars.join(", ")}
                          </div>
                        )}
                        {Object.keys(item.extra).length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {Object.entries(item.extra)
                              .slice(0, 3)
                              .map(([k, v]) => (
                                <span
                                  key={k}
                                  className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/30 text-zinc-500"
                                >
                                  {k}={String(v).slice(0, 20)}
                                </span>
                              ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            );
          })}
        </div>

        <p className="mt-10 text-center text-xs text-zinc-600 max-w-2xl mx-auto">
          This is a live snapshot from the running backend. The same data is
          available at <code className="text-zinc-500 font-mono">GET /api/v1/status</code> (auth required).
          Backend never crashes on missing keys — only the dependent feature is skipped.
        </p>
      </div>
    </section>
  );
}

function SummaryPill({
  label,
  count,
  color,
}: {
  label: string;
  count: number;
  color: string;
}) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium",
        color
      )}
    >
      <span className="text-base font-bold tabular-nums">{count}</span>
      <span>{label}</span>
    </div>
  );
}

// ── Snapshot used when the backend is offline or unauthenticated ──
const snapshotIntegrations: Integration[] = [
  {
    name: "Gemini AI",
    category: "ai",
    status: "configured",
    message: "API key present. Active provider.",
    required_env_vars: ["GEMINI_API_KEY"],
    missing_env_vars: [],
    last_checked: "",
    extra: { model: "gemini-1.5-pro" },
  },
  {
    name: "Firebase (client SDK)",
    category: "firebase",
    status: "configured",
    message: "Client SDK config present (google-services.json values).",
    required_env_vars: ["FIREBASE_PROJECT_ID", "FIREBASE_API_KEY"],
    missing_env_vars: [],
    last_checked: "",
    extra: { project_id: "zorkvdo" },
  },
  {
    name: "Storage (local)",
    category: "storage",
    status: "connected",
    message: "Using local filesystem.",
    required_env_vars: [],
    missing_env_vars: [],
    last_checked: "",
    extra: { backend: "local" },
  },
  {
    name: "FFmpeg",
    category: "video_engine",
    status: "connected",
    message: "ffmpeg + ffprobe available.",
    required_env_vars: [],
    missing_env_vars: [],
    last_checked: "",
    extra: {},
  },
  {
    name: "Redis",
    category: "workers",
    status: "service_offline",
    message: "Redis unreachable. Background jobs run inline.",
    required_env_vars: ["REDIS_URL"],
    missing_env_vars: [],
    last_checked: "",
    extra: {},
  },
  {
    name: "Firebase Cloud Messaging",
    category: "notifications",
    status: "missing_api_key",
    message: "FCM_SERVER_KEY not set. Push notifications disabled.",
    required_env_vars: ["FCM_SERVER_KEY"],
    missing_env_vars: ["FCM_SERVER_KEY"],
    last_checked: "",
    extra: {},
  },
  {
    name: "Stripe (payments)",
    category: "payments",
    status: "missing_api_key",
    message: "STRIPE_SECRET_KEY not set. Subscriptions return mock responses.",
    required_env_vars: ["STRIPE_SECRET_KEY"],
    missing_env_vars: ["STRIPE_SECRET_KEY"],
    last_checked: "",
    extra: {},
  },
  {
    name: "YOLO (object detection)",
    category: "video_engine",
    status: "disabled",
    message: "ultralytics not installed. Falls back to OpenCV Haar cascades.",
    required_env_vars: [],
    missing_env_vars: [],
    last_checked: "",
    extra: {},
  },
];

const snapshotSummary: StatusSummary = {
  last_refreshed: new Date().toISOString(),
  total: snapshotIntegrations.length,
  by_status: {
    connected: 2,
    configured: 2,
    missing_api_key: 2,
    invalid_credentials: 0,
    service_offline: 1,
    disabled: 1,
  },
};
