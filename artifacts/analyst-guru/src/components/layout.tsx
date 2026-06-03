import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import {
  LayoutDashboard,
  Files,
  SearchCheck,
  BrainCircuit,
  Cuboid,
  Network,
  ShieldCheck,
  Settings as SettingsIcon,
  Menu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLanguage, Lang } from "@/lib/i18n";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [location] = useLocation();
  const { lang, setLang, t } = useLanguage();

  const navItems = [
    { href: "/", label: t.nav_dashboard, icon: LayoutDashboard },
    { href: "/documents", label: t.nav_documents, icon: Files },
    { href: "/reviews", label: t.nav_reviews, icon: SearchCheck },
    { href: "/knowledge-base", label: t.nav_knowledge_base, icon: BrainCircuit },
    { href: "/architecture-studio", label: t.nav_architecture, icon: Cuboid },
    { href: "/memory", label: t.nav_memory, icon: Network },
    { href: "/audit", label: t.nav_audit, icon: ShieldCheck },
    { href: "/settings", label: t.nav_settings, icon: SettingsIcon },
  ];

  const otherLang: Lang = lang === "ru" ? "en" : "ru";

  return (
    <div className="min-h-screen flex w-full">
      <aside className="w-64 bg-sidebar text-sidebar-foreground flex flex-col hidden md:flex shrink-0 fixed inset-y-0 left-0 border-r border-sidebar-border">
        <div className="h-16 flex items-center px-6 border-b border-sidebar-border bg-sidebar font-semibold tracking-tight text-lg">
          <div className="w-8 h-8 rounded bg-sidebar-primary flex items-center justify-center mr-3 text-sidebar-primary-foreground">
            <BrainCircuit size={18} />
          </div>
          AnalystGuru
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="px-3 space-y-1">
            {navItems.map((item) => {
              const isActive =
                location === item.href ||
                (item.href !== "/" && location.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 ${
                      isActive
                        ? "text-sidebar-primary"
                        : "text-sidebar-foreground/50"
                    }`}
                  />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="p-4 border-t border-sidebar-border flex items-center justify-between">
          <span className="text-xs text-sidebar-foreground/50 font-mono">
            {t.system_core}
          </span>
          <button
            onClick={() => setLang(otherLang)}
            className="text-xs font-semibold text-sidebar-foreground/60 hover:text-sidebar-foreground bg-sidebar-accent/40 hover:bg-sidebar-accent px-2 py-1 rounded transition-colors"
            title={otherLang === "en" ? "Switch to English" : "Переключить на русский"}
            data-testid="lang-toggle-sidebar"
          >
            {otherLang.toUpperCase()}
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col md:pl-64 min-w-0">
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6 sticky top-0 z-10">
          <div className="flex items-center md:hidden">
            <Button variant="ghost" size="icon" className="mr-2">
              <Menu className="h-5 w-5" />
            </Button>
            <span className="font-semibold text-lg flex items-center">
              <BrainCircuit className="h-5 w-5 text-primary mr-2" />
              AnalystGuru
            </span>
          </div>
          <div className="flex items-center space-x-3 ml-auto">
            <div className="flex items-center rounded-md border border-border overflow-hidden text-xs font-semibold">
              <button
                onClick={() => setLang("ru")}
                className={`px-3 py-1.5 transition-colors ${
                  lang === "ru"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-muted-foreground hover:bg-muted"
                }`}
                data-testid="lang-ru"
              >
                RU
              </button>
              <button
                onClick={() => setLang("en")}
                className={`px-3 py-1.5 transition-colors ${
                  lang === "en"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-muted-foreground hover:bg-muted"
                }`}
                data-testid="lang-en"
              >
                EN
              </button>
            </div>
          </div>
        </header>
        <main className="flex-1 p-6 overflow-x-hidden">
          <div className="mx-auto max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
