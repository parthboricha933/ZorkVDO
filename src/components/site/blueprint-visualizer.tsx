"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Scissors,
  Music4,
  Type,
  Sparkles,
} from "lucide-react";
import { sampleScenes } from "@/lib/sample-data";
import { cn } from "@/lib/utils";

export function BlueprintVisualizer() {
  const [playing, setPlaying] = useState(false);
  const [activeScene, setActiveScene] = useState(0);
  const totalDuration = sampleScenes.reduce((a, s) => a + s.duration, 0);

  useEffect(() => {
    if (!playing) return;
    const interval = setInterval(() => {
      setActiveScene((prev) => {
        const next = prev + 1;
        if (next >= sampleScenes.length) {
          setPlaying(false);
          return 0;
        }
        return next;
      });
    }, 1200);
    return () => clearInterval(interval);
  }, [playing]);

  return (
    <section id="blueprint" className="relative py-24 sm:py-32">
      {/* Background glow */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[40rem] w-[60rem] rounded-full bg-purple-900/15 blur-3xl" />
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: explainer */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <span className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-fuchsia-300 mb-4">
                <Sparkles className="h-3.5 w-3.5" />
                The Blueprint
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
                A reusable JSON contract
                <br />
                for any editing style
              </h2>
              <p className="text-zinc-400 text-lg leading-relaxed mb-8">
                Every analyzed video becomes a serializable blueprint: scenes,
                transitions, captions, beats, color grade, camera motion. Stable
                schema, swappable AI providers, ready to drive your timeline
                editor.
              </p>

              <div className="space-y-3">
                {[
                  { icon: Scissors, label: "Per-scene shot type, duration, transition" },
                  { icon: Music4, label: "BPM + beat times synced to cuts" },
                  { icon: Type, label: "Caption text, font, position, animation" },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center gap-3 text-sm text-zinc-300"
                  >
                    <div className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                      <item.icon className="h-4 w-4 text-fuchsia-400" />
                    </div>
                    {item.label}
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Right: interactive timeline */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="relative rounded-2xl border border-white/10 bg-zinc-900/60 backdrop-blur-xl overflow-hidden shadow-2xl shadow-purple-950/40">
              {/* Top bar: "video preview" */}
              <div className="aspect-[9/16] sm:aspect-[9/12] max-h-[480px] relative bg-gradient-to-br from-zinc-900 to-black flex items-center justify-center overflow-hidden">
                <AnimatePresence mode="wait">
                  {sampleScenes.map((scene, i) =>
                    activeScene === i ? (
                      <motion.div
                        key={scene.index}
                        initial={{ opacity: 0, scale: 1.1 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.3 }}
                        className={cn(
                          "absolute inset-0 bg-gradient-to-br opacity-90",
                          scene.color
                        )}
                      >
                        {/* Mock content silhouettes */}
                        <div className="absolute inset-0 flex flex-col justify-between p-6">
                          <div className="flex items-start justify-between">
                            <span className="text-[10px] font-mono uppercase tracking-widest text-white/80">
                              Scene {scene.index + 1} · {scene.shotType}
                            </span>
                            <span className="text-[10px] font-mono text-white/80">
                              {scene.duration.toFixed(1)}s
                            </span>
                          </div>
                          <div className="space-y-2">
                            <div className="h-2 w-3/4 rounded-full bg-white/20" />
                            <div className="h-2 w-1/2 rounded-full bg-white/15" />
                          </div>
                          {scene.caption && (
                            <div className="self-center">
                              <span className="text-xl sm:text-2xl font-bold text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.6)] uppercase tracking-wide">
                                {scene.caption}
                              </span>
                            </div>
                          )}
                          <div className="text-[10px] font-mono text-white/70">
                            {scene.motion}
                          </div>
                        </div>
                      </motion.div>
                    ) : null
                  )}
                </AnimatePresence>

                {/* Beat sync indicator */}
                <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2 py-1 rounded-md bg-black/40 backdrop-blur-sm border border-white/10">
                  <Music4 className="h-3 w-3 text-fuchsia-300" />
                  <span className="text-[10px] font-mono text-white/80">128 BPM</span>
                </div>
              </div>

              {/* Timeline track */}
              <div className="p-4 border-t border-white/5 bg-black/30">
                <div className="flex items-center gap-2 mb-3">
                  <button
                    onClick={() => setActiveScene(Math.max(0, activeScene - 1))}
                    className="p-1.5 rounded-md hover:bg-white/5 text-zinc-400 hover:text-white"
                    aria-label="Previous scene"
                  >
                    <SkipBack className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setPlaying(!playing)}
                    className="h-9 w-9 rounded-full bg-gradient-to-br from-fuchsia-500 to-rose-500 flex items-center justify-center shadow-lg shadow-fuchsia-500/30 hover:scale-105 transition-transform"
                    aria-label={playing ? "Pause" : "Play"}
                  >
                    {playing ? (
                      <Pause className="h-4 w-4 text-white fill-white" />
                    ) : (
                      <Play className="h-4 w-4 text-white fill-white ml-0.5" />
                    )}
                  </button>
                  <button
                    onClick={() =>
                      setActiveScene(
                        Math.min(sampleScenes.length - 1, activeScene + 1)
                      )
                    }
                    className="p-1.5 rounded-md hover:bg-white/5 text-zinc-400 hover:text-white"
                    aria-label="Next scene"
                  >
                    <SkipForward className="h-4 w-4" />
                  </button>
                  <div className="ml-auto text-xs font-mono text-zinc-400">
                    00:0{activeScene}.{Math.floor(activeScene * 12)}/00:
                    {Math.floor(totalDuration)}.
                    {Math.floor((totalDuration % 1) * 10)}
                  </div>
                </div>

                {/* Scene strip */}
                <div className="flex gap-1 h-12">
                  {sampleScenes.map((scene, i) => (
                    <button
                      key={scene.index}
                      onClick={() => setActiveScene(i)}
                      className={cn(
                        "relative rounded-md flex-1 overflow-hidden transition-all",
                        activeScene === i
                          ? "ring-2 ring-white"
                          : "ring-1 ring-white/10 opacity-60 hover:opacity-100"
                      )}
                      style={{
                        flexGrow: scene.duration,
                      }}
                    >
                      <div
                        className={cn(
                          "absolute inset-0 bg-gradient-to-br",
                          scene.color
                        )}
                      />
                      <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white/90">
                        {scene.transition === "flash" && "⚡"}
                        {scene.transition === "cut" && "✂"}
                        {scene.transition === "dissolve" && "✦"}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Caption track */}
                <div className="mt-2 flex gap-1 h-5 text-[9px] font-mono text-zinc-500">
                  {sampleScenes.map((scene, i) => (
                    <div
                      key={`cap-${scene.index}`}
                      className={cn(
                        "flex-1 flex items-center justify-center rounded-sm",
                        activeScene === i ? "bg-fuchsia-500/20 text-fuchsia-200" : "bg-white/5"
                      )}
                      style={{ flexGrow: scene.duration }}
                    >
                      {scene.caption ? "T" : "—"}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Floating JSON badge */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="absolute -bottom-4 -left-4 hidden sm:block rounded-lg border border-white/10 bg-zinc-950/90 backdrop-blur-md px-3 py-2 shadow-xl"
            >
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs font-mono text-zinc-300">
                  schema_version: "1.0.0"
                </span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
