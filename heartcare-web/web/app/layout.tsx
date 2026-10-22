import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ScoreProvider } from "@/lib/store";
import { ThemeSetup } from "@/components/theme-setup";
import { SiteNav } from "@/components/site-nav";

const geist = Geist({ subsets: ["latin"], variable: "--font-sans" });
const mono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

export const metadata: Metadata = {
  title: "HeartCare — Know your heart",
  description: "Educational heart-health score from clinical measurements. Not a medical device.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geist.variable} ${mono.variable} font-sans antialiased`}>
        <ThemeSetup>
          <ScoreProvider>
            <SiteNav />
            <main className="mx-auto max-w-6xl px-6 pb-16">{children}</main>
            <footer className="border-t">
              <p className="text-muted-foreground mx-auto max-w-6xl px-6 py-6 text-center text-[12.5px]">
                <b>HeartCare</b> · classroom machine learning ·{" "}
                This is an educational tool, NOT a medical device. Trained on a small 1980s dataset
                (UCI Cleveland, 303 rows). Not clinically validated. For emergencies, seek urgent care immediately.
              </p>
            </footer>
          </ScoreProvider>
        </ThemeSetup>
      </body>
    </html>
  );
}
