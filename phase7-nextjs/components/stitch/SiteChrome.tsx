import Link from "next/link";
import type { ReactNode } from "react";
import { ThemeToggle } from "./ThemeToggle";

export type StitchNavId = "home" | "recommendations" | "eval";

function navLinkClass(active: boolean): string {
  return active
    ? "text-sm font-semibold text-[#E23744] dark:text-[#ffb3b1]"
    : "text-sm text-zinc-600 transition-colors hover:text-zinc-900 dark:text-zinc-500 dark:hover:text-zinc-200";
}

export function SiteChrome({
  children,
  activeNav,
  mainClassName = "",
  showFooter = true,
}: {
  children: ReactNode;
  activeNav: StitchNavId;
  mainClassName?: string;
  /** When false, omits the global footer so single-viewport layouts (e.g. home) can avoid extra scroll. */
  showFooter?: boolean;
}) {
  const shellClass = showFooter
    ? "min-h-screen pt-14 sm:pt-16"
    : "flex min-h-[calc(100dvh-3.5rem)] flex-col pt-14 sm:min-h-[calc(100dvh-4rem)] sm:pt-16";

  return (
    <>
      <header className="fixed top-0 left-0 z-50 w-full border-b themed-border bg-[color:var(--dm-bg)]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-6 px-4 sm:h-16 sm:px-6">
          <Link
            href="/"
            className="text-base font-bold tracking-tight themed-text transition-opacity hover:opacity-90 sm:text-lg"
          >
            DineMatch AI
          </Link>
          <nav className="flex items-center gap-4 sm:gap-6" aria-label="Main">
            <Link href="/" className={navLinkClass(activeNav === "home")}>
              Home
            </Link>
            <Link href="/recommendations" className={navLinkClass(activeNav === "recommendations")}>
              Results
            </Link>
            <ThemeToggle />
          </nav>
        </div>
      </header>

      <div className={`${shellClass} ${mainClassName}`}>{children}</div>

      {showFooter ? (
        <footer className="mt-auto border-t themed-border themed-bg px-4 py-8 sm:px-6 sm:py-10">
          <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-6 text-center text-xs text-zinc-500 dark:text-zinc-500 sm:flex-row sm:text-left">
            <div>
              <span className="text-sm font-bold text-[#E23744]">DineMatch AI</span>
              <p className="mt-1">© {new Date().getFullYear()} DineMatch AI</p>
            </div>
            <div className="flex flex-wrap justify-center gap-6 sm:justify-end">
              <span className="text-zinc-500 dark:text-zinc-600">Support</span>
              <span className="text-zinc-500 dark:text-zinc-600">Privacy</span>
              <span className="text-zinc-500 dark:text-zinc-600">Terms</span>
            </div>
          </div>
        </footer>
      ) : null}
    </>
  );
}
