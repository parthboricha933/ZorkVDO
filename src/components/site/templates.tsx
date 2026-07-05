"use client";

import { motion } from "framer-motion";
import { Crown, ArrowRight } from "lucide-react";
import { templates } from "@/lib/sample-data";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const paceColor: Record<string, string> = {
  slow: "text-emerald-300 bg-emerald-500/10 border-emerald-500/20",
  medium: "text-amber-300 bg-amber-500/10 border-amber-500/20",
  fast: "text-rose-300 bg-rose-500/10 border-rose-500/20",
  hyper: "text-fuchsia-300 bg-fuchsia-500/10 border-fuchsia-500/20",
};

const categoryGradient: Record<string, string> = {
  product: "from-fuchsia-500 to-purple-600",
  education: "from-purple-600 to-indigo-600",
  action: "from-rose-500 to-orange-500",
  lifestyle: "from-emerald-500 to-teal-600",
};

export function Templates() {
  return (
    <section id="templates" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl sm:text-4xl font-bold text-white"
          >
            Start from a template, or analyze your own
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.05 }}
            className="mt-4 text-zinc-400 text-lg"
          >
            Four curated templates seeded by default. Premium templates unlock
            with the Creator plan. Or skip templates entirely — upload any
            viral video and ZorkVDO reverse-engineers it.
          </motion.p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {templates.map((tpl, i) => (
            <motion.div
              key={tpl.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="group relative rounded-2xl border border-white/10 bg-zinc-900/40 backdrop-blur-sm overflow-hidden hover:border-white/20 transition-all"
            >
              {/* Preview thumbnail */}
              <div className="relative aspect-[9/12] overflow-hidden">
                <div
                  className={cn(
                    "absolute inset-0 bg-gradient-to-br opacity-90 group-hover:scale-105 transition-transform duration-500",
                    categoryGradient[tpl.category]
                  )}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

                {/* Mock scene bars */}
                <div className="absolute bottom-3 left-3 right-3 flex gap-0.5 h-6">
                  {Array.from({ length: tpl.scenes }).map((_, idx) => (
                    <div
                      key={idx}
                      className="flex-1 rounded-sm bg-white/30 backdrop-blur-sm"
                      style={{ flexGrow: 1 + (idx % 3) * 0.4 }}
                    />
                  ))}
                </div>

                {tpl.isPremium && (
                  <div className="absolute top-3 right-3">
                    <Badge
                      variant="outline"
                      className="border-amber-400/40 bg-amber-400/10 text-amber-200 backdrop-blur-sm"
                    >
                      <Crown className="mr-1 h-3 w-3" />
                      PRO
                    </Badge>
                  </div>
                )}

                <div className="absolute top-3 left-3">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-white/70">
                    {tpl.category}
                  </span>
                </div>
              </div>

              {/* Body */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-base font-semibold text-white">
                    {tpl.name}
                  </h3>
                  <span
                    className={cn(
                      "text-[10px] font-mono uppercase px-1.5 py-0.5 rounded border",
                      paceColor[tpl.pace]
                    )}
                  >
                    {tpl.pace}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed mb-3 line-clamp-2">
                  {tpl.description}
                </p>
                <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                  <span>{tpl.scenes} scenes</span>
                  <span>{tpl.duration}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-10 text-center">
          <a
            href="#top"
            className="inline-flex items-center text-sm font-medium text-fuchsia-300 hover:text-fuchsia-200"
          >
            Browse all templates in the app
            <ArrowRight className="ml-1.5 h-4 w-4" />
          </a>
        </div>
      </div>
    </section>
  );
}
