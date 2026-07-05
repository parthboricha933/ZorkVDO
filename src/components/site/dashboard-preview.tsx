"use client";

import { motion } from "framer-motion";
import {
  FolderPlus,
  Film,
  Layers,
  Clock,
  HardDrive,
  TrendingUp,
} from "lucide-react";
import { stats } from "@/lib/sample-data";

export function DashboardPreview() {
  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="order-2 lg:order-1"
          >
            <span className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-rose-300 mb-4">
              <TrendingUp className="h-3.5 w-3.5" />
              Creator dashboard
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
              Every project, every render,
              <br />
              every blueprint in one place
            </h2>
            <p className="text-zinc-400 text-lg leading-relaxed mb-8">
              The dashboard tracks your projects, videos, renders, storage
              usage, and recent activity — all surfaced through a clean
              REST API. JWT-authenticated, owner-scoped, ready to plug into
              any client.
            </p>

            <div className="grid grid-cols-2 gap-3">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-lg border border-white/10 bg-zinc-900/40 px-4 py-3"
                >
                  <div className="text-2xl font-bold text-white">
                    {stat.value}
                  </div>
                  <div className="text-xs text-zinc-500 mt-0.5">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Mock dashboard */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="order-1 lg:order-2"
          >
            <div className="relative rounded-2xl border border-white/10 bg-zinc-900/60 backdrop-blur-xl overflow-hidden shadow-2xl shadow-purple-950/30">
              {/* Window chrome */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-black/30">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-rose-500/70" />
                  <div className="h-3 w-3 rounded-full bg-amber-500/70" />
                  <div className="h-3 w-3 rounded-full bg-emerald-500/70" />
                </div>
                <span className="ml-2 text-xs font-mono text-zinc-500">
                  zorkvdo.app/dashboard
                </span>
              </div>

              {/* Dashboard body */}
              <div className="p-4 space-y-4">
                {/* Stat cards */}
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { icon: FolderPlus, label: "Projects", val: "12", accent: "text-fuchsia-300" },
                    { icon: Film, label: "Videos", val: "47", accent: "text-purple-300" },
                    { icon: Layers, label: "Blueprints", val: "8", accent: "text-rose-300" },
                    { icon: Clock, label: "Rendered", val: "23", accent: "text-amber-300" },
                  ].map((card) => (
                    <div
                      key={card.label}
                      className="rounded-lg border border-white/5 bg-white/[0.02] p-2.5"
                    >
                      <card.icon className={`h-3.5 w-3.5 ${card.accent} mb-1.5`} />
                      <div className="text-lg font-bold text-white">
                        {card.val}
                      </div>
                      <div className="text-[10px] text-zinc-500">{card.label}</div>
                    </div>
                  ))}
                </div>

                {/* Recent activity */}
                <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">
                  <div className="text-xs font-medium text-zinc-400 mb-3">
                    Recent activity
                  </div>
                  <div className="space-y-2">
                    {[
                      { action: "Blueprint generated", time: "2m ago", color: "bg-fuchsia-500" },
                      { action: "Video uploaded", time: "8m ago", color: "bg-purple-500" },
                      { action: "Render completed", time: "23m ago", color: "bg-rose-500" },
                      { action: "Project created", time: "1h ago", color: "bg-amber-500" },
                    ].map((item, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -8 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 + i * 0.08 }}
                        className="flex items-center gap-2.5 text-xs"
                      >
                        <div className={`h-1.5 w-1.5 rounded-full ${item.color}`} />
                        <span className="text-zinc-300 flex-1">{item.action}</span>
                        <span className="text-zinc-600 font-mono">{item.time}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Storage bar */}
                <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">
                  <div className="flex items-center justify-between text-xs mb-2">
                    <span className="text-zinc-400 flex items-center gap-1.5">
                      <HardDrive className="h-3 w-3" />
                      Storage used
                    </span>
                    <span className="text-zinc-500 font-mono">3.4 / 10 GB</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "34%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className="h-full bg-gradient-to-r from-fuchsia-500 to-rose-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
