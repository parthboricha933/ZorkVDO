"use client";

import { motion } from "framer-motion";
import { ArrowRight, Play, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function Hero() {
  return (
    <section
      id="top"
      className="relative pt-32 pb-20 sm:pt-40 sm:pb-28 overflow-hidden"
    >
      {/* Ambient gradient blobs */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -left-40 h-[40rem] w-[40rem] rounded-full bg-fuchsia-600/20 blur-3xl" />
        <div className="absolute top-20 -right-40 h-[35rem] w-[35rem] rounded-full bg-purple-700/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-[30rem] w-[60rem] rounded-full bg-rose-600/10 blur-3xl" />
      </div>

      {/* Grid texture */}
      <div
        className="absolute inset-0 -z-10 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          maskImage:
            "radial-gradient(ellipse at center, black 30%, transparent 75%)",
          WebkitMaskImage:
            "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        }}
      />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex justify-center mb-6"
          >
            <Badge
              variant="outline"
              className="border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-200 backdrop-blur-sm px-4 py-1.5 text-xs font-medium"
            >
              <Sparkles className="mr-1.5 h-3.5 w-3.5" />
              AI-powered viral video blueprint engine
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.05 }}
            className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white"
          >
            Create viral videos
            <br />
            from{" "}
            <span className="relative inline-block">
              <span className="bg-gradient-to-r from-fuchsia-400 via-purple-400 to-rose-400 bg-clip-text text-transparent">
                any inspiration
              </span>
              <svg
                viewBox="0 0 300 12"
                className="absolute -bottom-2 left-0 w-full"
                preserveAspectRatio="none"
              >
                <motion.path
                  d="M2 8 Q 75 2, 150 6 T 298 5"
                  fill="none"
                  stroke="url(#grad)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 1, delay: 0.6 }}
                />
                <defs>
                  <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#e879f9" />
                    <stop offset="50%" stopColor="#c084fc" />
                    <stop offset="100%" stopColor="#fb7185" />
                  </linearGradient>
                </defs>
              </svg>
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="mt-8 text-lg sm:text-xl text-zinc-300 max-w-2xl mx-auto leading-relaxed"
          >
            Upload a viral video. ZorkVDO reverse-engineers its editing style
            — every cut, beat, caption, and color grade — into a reusable
            blueprint. Drop in your own clips, get a brand-new video that
            matches the rhythm. No copying. Just the style.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25 }}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button
              size="lg"
              className="group bg-gradient-to-r from-fuchsia-500 to-rose-500 hover:from-fuchsia-400 hover:to-rose-400 text-white border-0 shadow-xl shadow-fuchsia-500/30 px-8 h-12 text-base"
            >
              Analyze your first video
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white/15 bg-white/5 backdrop-blur-sm text-white hover:bg-white/10 hover:text-white h-12 px-6 text-base"
            >
              <Play className="mr-2 h-4 w-4 fill-white" />
              Watch demo
            </Button>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="mt-6 text-sm text-zinc-500"
          >
            Free tier · No credit card · 3 projects included
          </motion.p>
        </div>

        {/* Platform bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-20 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-zinc-500"
        >
          <span className="text-xs uppercase tracking-widest text-zinc-600">
            Built for
          </span>
          {["Instagram Reels", "TikTok", "YouTube Shorts", "Facebook Reels"].map(
            (platform) => (
              <span
                key={platform}
                className="text-sm font-medium text-zinc-400"
              >
                {platform}
              </span>
            )
          )}
        </motion.div>
      </div>
    </section>
  );
}
