"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Check, Sparkles } from "lucide-react";
import { plans } from "@/lib/sample-data";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Pricing() {
  const [yearly, setYearly] = useState(false);

  return (
    <section id="pricing" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <motion.h2
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl sm:text-4xl font-bold text-white"
          >
            Pricing that scales with your output
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.05 }}
            className="mt-4 text-zinc-400 text-lg"
          >
            Start free. Upgrade when you ship. Cancel anytime.
          </motion.p>

          {/* Billing toggle */}
          <div className="mt-8 inline-flex items-center rounded-full border border-white/10 bg-zinc-900/60 backdrop-blur-sm p-1">
            <button
              onClick={() => setYearly(false)}
              className={cn(
                "px-4 py-1.5 text-sm rounded-full transition-colors",
                !yearly
                  ? "bg-white text-zinc-900 font-medium"
                  : "text-zinc-400 hover:text-white"
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setYearly(true)}
              className={cn(
                "px-4 py-1.5 text-sm rounded-full transition-colors flex items-center gap-2",
                yearly
                  ? "bg-white text-zinc-900 font-medium"
                  : "text-zinc-400 hover:text-white"
              )}
            >
              Yearly
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">
                -17%
              </span>
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.code}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className={cn(
                "relative rounded-2xl p-6 flex flex-col",
                plan.highlight
                  ? "border-2 border-fuchsia-500/40 bg-gradient-to-b from-fuchsia-500/10 to-zinc-900/40 backdrop-blur-sm shadow-xl shadow-fuchsia-500/10"
                  : "border border-white/10 bg-zinc-900/40 backdrop-blur-sm"
              )}
            >
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <div className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-fuchsia-500 to-rose-500 text-white text-xs font-medium shadow-lg">
                    <Sparkles className="h-3 w-3" />
                    Most popular
                  </div>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white">{plan.name}</h3>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-white">
                    ${yearly ? Math.floor(plan.priceYearly / 12) : plan.priceMonthly}
                  </span>
                  <span className="text-sm text-zinc-400">/mo</span>
                </div>
                <p className="mt-1 text-xs text-zinc-500">
                  {yearly && plan.priceYearly > 0
                    ? `Billed $${plan.priceYearly}/year`
                    : "Billed monthly"}
                </p>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5">
                    <div
                      className={cn(
                        "mt-0.5 h-4 w-4 rounded-full flex items-center justify-center flex-shrink-0",
                        plan.highlight
                          ? "bg-fuchsia-500/20"
                          : "bg-white/5"
                      )}
                    >
                      <Check
                        className={cn(
                          "h-3 w-3",
                          plan.highlight ? "text-fuchsia-300" : "text-zinc-300"
                        )}
                      />
                    </div>
                    <span className="text-sm text-zinc-300">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                className={cn(
                  "w-full h-11",
                  plan.highlight
                    ? "bg-gradient-to-r from-fuchsia-500 to-rose-500 hover:from-fuchsia-400 hover:to-rose-400 text-white border-0 shadow-lg shadow-fuchsia-500/30"
                    : "bg-white/5 border border-white/10 text-white hover:bg-white/10"
                )}
              >
                {plan.cta}
              </Button>
            </motion.div>
          ))}
        </div>

        <p className="mt-10 text-center text-xs text-zinc-500">
          All plans include JWT auth, unlimited blueprint storage, and access
          to the public API. Prices in USD.
        </p>
      </div>
    </section>
  );
}
