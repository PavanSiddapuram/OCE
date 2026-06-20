import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Sidebar } from "@/components/layout/Sidebar";

export const metadata: Metadata = {
  title: "OCE — Opportunity Creation Engine",
  description: "Discover startups, find hidden problems, create opportunities.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex h-screen overflow-hidden bg-zinc-950 text-zinc-100">
        <Providers>
          <Sidebar />
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
