"use client";

import { motion } from "framer-motion";
import {
  Scissors,
  Move,
  ZoomIn,
  Music,
  Type,
  Sparkles,
  Palette,
  User,
  Gauge,
} from "lucide-react";
import { analysisFeatures } from "@/lib/sample-data";
import { cn } from "@/lib/utils";

const iconMap: Record<string, React.ElementType> = {
  Scissors,
  Move,
  ZoomIn,
  Music,
  Type,
  Sparkles,
  Palette,
  User,
  Gauge,
};

const categoryStyles: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  video: {
    label: "Video",
    color: "text-fuchsia-300",
    bg: "bg-fuchsia-500/10 border-fuchsia-500/20",
  },
  audio: {
    label: "Audio",
    color: "text-purple-300",
    bg: "bg-purple-500/10 border-purple-500/20",
  },
  caption: {
    label: "Caption",
    color: "text-rose-300",
    bg: "bg-rose-500/10 border-rose-500/20",
  },
  visual: {
    label: "Visual",
    color: "text-amber-300",
    bg: "bg-amber-500/10 border-amber-500/20",
  },
};

export function Features() {
  return (
    <section id="features" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl sm:text-4xl font-bold text-white"
          >
            7 parallel analysis passes.
            <br />
            One coherent blueprint.
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.05 }}
            className="mt-4 text-zinc-400 text-lg"
          >
            Built on OpenCV, librosa, EasyOCR, YOLO, MediaPipe, and FFmpeg.
            Every pass degrades gracefully — if a heavy dep is missing, the
            pipeline still produces useful output.
          </motion.p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {analysisFeatures.map((feature, i) => {
            const Icon = iconMap[feature.icon] || Sparkles;
            const style = categoryStyles[feature.category];
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: (i % 3) * 0.05 }}
                className="group relative rounded-xl border border-white/10 bg-zinc-900/40 backdrop-blur-sm p-5 hover:border-white/20 hover:bg-zinc-900/60 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="h-10 w-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <span
                    className={cn(
                      "text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border",
                      style.bg,
                      style.color
                    )}
                  >
                    {style.label}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}

          {/* Bonus cell: link to docs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
            className="relative rounded-xl border border-fuchsia-500/20 bg-gradient-to-br from-fuchsia-500/10 via-purple-600/10 to-rose-500/10 p-5 flex flex-col justify-between"
          >
            <div>
              <div className="text-4xl font-bold text-white mb-1">79%</div>
              <p className="text-sm text-zinc-300">
                Backend test coverage. 161 tests. Production-grade from day one.
              </p>
            </div>
            <a
              href="#top"
              className="mt-4 inline-flex items-center text-sm font-medium text-fuchsia-300 hover:text-fuchsia-200"
            >
              Read the architecture →
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
