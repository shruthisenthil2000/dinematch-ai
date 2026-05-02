import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Phase 7 - DineMatch",
  description: "Evaluation, safety, and hardening frontend for recommendations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
