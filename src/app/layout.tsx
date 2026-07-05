import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ZorkVDO — Create Viral Videos from Any Inspiration",
  description:
    "AI-powered viral video blueprint engine. Upload any viral video, get a reusable editing blueprint, drop in your own clips, and ship a brand-new video with the same energy. No copying. Just the style.",
  keywords: [
    "ZorkVDO",
    "AI video editing",
    "viral video",
    "video blueprint",
    "content creation",
    "TikTok",
    "Instagram Reels",
    "YouTube Shorts",
  ],
  authors: [{ name: "ZorkVDO" }],
  openGraph: {
    title: "ZorkVDO — Create Viral Videos from Any Inspiration",
    description:
      "Reverse-engineer any viral video into a reusable editing blueprint. Drop in your clips, get a new video.",
    siteName: "ZorkVDO",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ZorkVDO — Create Viral Videos from Any Inspiration",
    description:
      "Reverse-engineer any viral video into a reusable editing blueprint.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-950 text-zinc-100 selection:bg-fuchsia-500/30`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
