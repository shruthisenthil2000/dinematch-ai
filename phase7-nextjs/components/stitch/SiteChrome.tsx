import Link from "next/link";
import type { ReactNode } from "react";

export type StitchNavId = "home" | "recommendations" | "eval";

function navLinkClass(active: boolean): string {
  return active
    ? "text-[#E23744] font-semibold border-b-2 border-[#E23744] pb-1"
    : "text-zinc-400 hover:text-zinc-200 transition-colors";
}

export function SiteChrome({
  children,
  activeNav,
  aside,
  mainClassName = "",
}: {
  children: ReactNode;
  activeNav: StitchNavId;
  aside?: ReactNode;
  mainClassName?: string;
}) {
  return (
    <>
      <nav className="fixed top-0 left-0 z-50 flex h-16 w-full items-center justify-between border-b border-white/5 bg-[#0F0F0F]/70 px-4 shadow-2xl shadow-black/50 backdrop-blur-2xl sm:px-8">
        <div className="flex items-center gap-4 md:gap-8">
          <Link href="/" className="text-lg font-bold tracking-tighter text-white sm:text-xl">
            DineMatch AI
          </Link>
          <div className="hidden items-center gap-6 md:flex">
            <Link href="/" className={`text-sm tracking-tight ${navLinkClass(activeNav === "home")}`}>
              Home
            </Link>
            <Link
              href="/recommendations"
              className={`text-sm tracking-tight ${navLinkClass(activeNav === "recommendations")}`}
            >
              Results
            </Link>
            <span className="text-sm text-zinc-600">Dining Out</span>
            <span className="text-sm text-zinc-600">Delivery</span>
            <Link href="/eval" className={`text-sm tracking-tight ${navLinkClass(activeNav === "eval")}`}>
              Sample scenarios
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-2 sm:gap-4">
          <div className="relative hidden max-w-[200px] lg:block lg:max-w-none">
            <input
              readOnly
              className="w-64 rounded-full border border-white/10 bg-white/5 py-1.5 pl-4 pr-10 text-xs text-zinc-300 placeholder:text-zinc-600 focus:border-[#E23744]/50 focus:outline-none"
              placeholder="Search culinary experiences..."
              aria-label="Search (display only)"
            />
            <span className="material-symbols-outlined pointer-events-none absolute right-3 top-1.5 text-sm text-zinc-500">
              search
            </span>
          </div>
          <button
            type="button"
            className="flex items-center gap-2 rounded-full px-2 py-1.5 transition-all duration-300 hover:bg-white/5 sm:px-3"
            aria-label="Profile"
          >
            <span className="material-symbols-outlined text-zinc-400">account_circle</span>
            <span className="hidden text-sm text-zinc-300 sm:inline">Profile</span>
          </button>
        </div>
      </nav>

      {aside}

      <div className={`min-h-screen pt-16 ${aside ? "md:pr-80" : ""} ${mainClassName}`}>{children}</div>

      <footer className="mt-auto flex w-full flex-col items-center justify-between gap-4 border-t border-white/5 bg-[#0F0F0F] px-8 py-12 text-xs text-zinc-500 md:flex-row">
        <div className="flex flex-col items-center gap-2 md:items-start">
          <span className="text-lg font-black text-[#E23744]">DineMatch AI</span>
          <p>© {new Date().getFullYear()} DineMatch AI. The discerning concierge.</p>
        </div>
        <div className="flex flex-wrap justify-center gap-6 md:gap-8">
          <span className="text-zinc-600">Support</span>
          <span className="text-zinc-600">For restaurants</span>
          <span className="text-zinc-600">Privacy</span>
          <span className="text-zinc-600">Terms</span>
        </div>
        <div className="flex gap-4">
          <div className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-white/10 transition-colors hover:bg-[#E23744]/10">
            <span className="material-symbols-outlined text-sm">share</span>
          </div>
          <div className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-white/10 transition-colors hover:bg-[#E23744]/10">
            <span className="material-symbols-outlined text-sm">public</span>
          </div>
        </div>
      </footer>
    </>
  );
}

export function InsightsAside({ children }: { children: ReactNode }) {
  return (
    <aside className="fixed right-0 top-16 z-40 hidden h-[calc(100vh-64px)] w-80 translate-x-0 flex-col border-l border-white/10 bg-[#1E1E1E]/80 p-6 shadow-[-20px_0_30px_rgba(0,0,0,0.5)] backdrop-blur-3xl md:flex">
      <div className="mb-8">
        <h3 className="text-lg font-bold text-white">AI Insights</h3>
        <p className="text-xs text-zinc-500">Why these matches?</p>
      </div>
      <div className="flex flex-grow flex-col gap-2">{children}</div>
      <div className="glass-panel mt-auto rounded-xl border-white/5 p-4">
        <div className="mb-2 flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#ff535a]">
            <span className="material-symbols-outlined text-sm text-white">auto_awesome</span>
          </div>
          <span className="text-xs font-semibold text-white">Concierge active</span>
        </div>
        <p className="text-[10px] leading-relaxed text-zinc-400">
          Your filters and optional richer AI explanations keep every shortlist aligned with what you asked for.
        </p>
      </div>
    </aside>
  );
}
