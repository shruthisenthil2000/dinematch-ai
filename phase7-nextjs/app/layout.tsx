import { Be_Vietnam_Pro } from "next/font/google";
import "./globals.css";
import type { Metadata } from "next";

const beVietnam = Be_Vietnam_Pro({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DineMatch AI",
  description: "AI-powered restaurant recommendations tailored to your tastes",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap"
        />
      </head>
      <body className={beVietnam.className}>{children}</body>
    </html>
  );
}
