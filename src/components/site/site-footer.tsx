"use client";

import { Zap, Github, Twitter, Youtube } from "lucide-react";

const footerNav = {
  Product: ["Features", "Templates", "Pricing", "Changelog", "Roadmap"],
  Developers: ["API docs", "Blueprint schema", "OpenAPI spec", "Status"],
  Company: ["About", "Blog", "Careers", "Contact", "Press kit"],
  Legal: ["Privacy", "Terms", "Security", "GDPR", "DMCA"],
};

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-white/5 bg-zinc-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 mb-10">
          <div className="col-span-2">
            <a href="#top" className="flex items-center gap-2 mb-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-fuchsia-500 to-rose-500 flex items-center justify-center">
                <Zap className="h-4 w-4 text-white fill-white" />
              </div>
              <span className="text-base font-bold text-white">
                Zork<span className="text-fuchsia-400">VDO</span>
              </span>
            </a>
            <p className="text-sm text-zinc-500 max-w-xs leading-relaxed">
              Create viral videos from any inspiration. AI-powered blueprint
              engine for creators.
            </p>
            <div className="flex items-center gap-3 mt-4">
              {[Twitter, Youtube, Github].map((Icon, i) => (
                <a
                  key={i}
                  href="#top"
                  className="h-8 w-8 rounded-lg border border-white/10 bg-white/5 flex items-center justify-center text-zinc-400 hover:text-white hover:border-white/20 transition-colors"
                  aria-label="Social link"
                >
                  <Icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          {Object.entries(footerNav).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-xs font-mono uppercase tracking-widest text-zinc-500 mb-3">
                {title}
              </h4>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#top"
                      className="text-sm text-zinc-400 hover:text-white transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-zinc-600">
            © {new Date().getFullYear()} ZorkVDO. All rights reserved.
          </p>
          <div className="flex items-center gap-2 text-xs text-zinc-600">
            <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-mono">All systems operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
