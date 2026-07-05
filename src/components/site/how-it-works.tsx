"use client";

import { motion } from "framer-motion";
import { Upload, Wand2, Film, ArrowRight } from "lucide-react";

const steps = [
  {
    icon: Upload,
    title: "Upload a viral video",
    description:
      "Drop in any video that went viral — a TikTok, a Reel, a Short. ZorkVDO probes it with FFmpeg, then runs 7 parallel CV passes: scene cuts, motion, beats, captions, color, objects, faces.",
    accent: "from-fuchsia-500 to-purple-600",
    badge: "Step 01",
  },
  {
    icon: Wand2,
    title: "AI generates a blueprint",
    description:
      "Every signal — scene boundaries, BPM, caption text, color grade, camera motion — is assembled into a single reusable JSON blueprint. Stable, serializable, ready to remix.",
    accent: "from-purple-600 to-rose-500",
    badge: "Step 02",
  },
  {
    icon: Film,
    title: "Upload your clips, get a new video",
    description:
      "The clip matcher scores your footage against every scene slot. The renderer trims, scales, concatenates, and burns in captions via FFmpeg. You get a brand-new video with the same energy.",
    accent: "from-rose-500 to-amber-500",
    badge: "Step 03",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl sm:text-4xl font-bold tracking-tight text-white"
          >
            From viral video to original cut in three steps
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.05 }}
            className="mt-4 text-zinc-400 text-lg"
          >
            No copy-paste. No copyright claims. Just the editing style —
            reverse-engineered and reapplied to your own footage.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8 relative">
          {/* Connector line on desktop */}
          <div className="hidden md:block absolute top-12 left-[16.66%] right-[16.66%] h-px bg-gradient-to-r from-fuchsia-500/0 via-fuchsia-500/30 to-rose-500/0" />

          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="relative group"
            >
              <div className="relative h-full rounded-2xl border border-white/10 bg-zinc-900/40 backdrop-blur-sm p-6 hover:border-white/20 transition-colors">
                <div className="flex items-start justify-between mb-6">
                  <div
                    className={`relative h-12 w-12 rounded-xl bg-gradient-to-br ${step.accent} flex items-center justify-center shadow-lg`}
                  >
                    <step.icon className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xs font-mono uppercase tracking-widest text-zinc-500">
                    {step.badge}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {step.title}
                </h3>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  {step.description}
                </p>
              </div>
              {i < steps.length - 1 && (
                <div className="hidden md:flex absolute -right-4 top-1/2 -translate-y-1/2 z-10">
                  <div className="h-8 w-8 rounded-full bg-zinc-900 border border-white/10 flex items-center justify-center">
                    <ArrowRight className="h-4 w-4 text-fuchsia-400" />
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
