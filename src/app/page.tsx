import { SiteNav } from "@/components/site/site-nav";
import { Hero } from "@/components/site/hero";
import { HowItWorks } from "@/components/site/how-it-works";
import { BlueprintVisualizer } from "@/components/site/blueprint-visualizer";
import { Features } from "@/components/site/features";
import { Templates } from "@/components/site/templates";
import { DashboardPreview } from "@/components/site/dashboard-preview";
import { Pricing } from "@/components/site/pricing";
import { CTASection } from "@/components/site/cta-section";
import { SiteFooter } from "@/components/site/site-footer";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-zinc-100">
      <SiteNav />
      <main className="flex-1">
        <Hero />
        <HowItWorks />
        <BlueprintVisualizer />
        <Features />
        <Templates />
        <DashboardPreview />
        <Pricing />
        <CTASection />
      </main>
      <SiteFooter />
    </div>
  );
}
