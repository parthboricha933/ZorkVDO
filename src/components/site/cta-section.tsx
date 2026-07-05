"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative rounded-3xl overflow-hidden border border-white/10"
        >
          {/* Gradient bg */}
          <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-600/30 via-purple-700/30 to-rose-600/30" />
          <div className="absolute inset-0 bg-gradient-to-br from-zinc-950 via-zinc-950/50 to-zinc-950" />
          <div
            className="absolute inset-0 opacity-[0.07]"
            style={{
              backgroundImage:
                "linear-gradient(to right, white 1px, transparent 1px), linear-gradient(to bottom, white 1px, transparent 1px)",
              backgroundSize: "40px 40px",
            }}
          />

          {/* Ambient glow */}
          <div className="absolute -top-20 -left-20 h-60 w-60 rounded-full bg-fuchsia-500/30 blur-3xl" />
          <div className="absolute -bottom-20 -right-20 h-60 w-60 rounded-full bg-rose-500/30 blur-3xl" />

          <div className="relative px-6 py-16 sm:px-12 sm:py-20 text-center">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-200 text-xs font-medium mb-6">
              <Sparkles className="h-3 w-3" />
              Beta access open
            </div>
            <h2 className="text-3xl sm:text-5xl font-bold text-white max-w-2xl mx-auto">
              Stop guessing what makes a video go viral.
              <span className="block mt-2 bg-gradient-to-r from-fuchsia-400 to-rose-400 bg-clip-text text-transparent">
                Reverse-engineer it.
              </span>
            </h2>
            <p className="mt-6 text-zinc-300 text-lg max-w-xl mx-auto">
              Free tier includes 3 projects, 720p rendering, and the full
              analysis pipeline. No credit card required.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                className="group bg-gradient-to-r from-fuchsia-500 to-rose-500 hover:from-fuchsia-400 hover:to-rose-400 text-white border-0 shadow-xl shadow-fuchsia-500/30 px-8 h-12 text-base"
              >
                Start free
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-white/20 bg-white/5 backdrop-blur-sm text-white hover:bg-white/10 hover:text-white h-12 px-6 text-base"
              >
                View API docs
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
