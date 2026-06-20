"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Building2, Target, Users, MessageSquare, Zap } from "lucide-react";

const nav = [
  { href: "/discover", label: "Discover", icon: Compass },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/opportunities", label: "Opportunities", icon: Target },
  { href: "/crm", label: "CRM", icon: Users },
  { href: "/outreach", label: "Outreach", icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 flex-shrink-0 border-r border-zinc-800 bg-zinc-900 flex flex-col">
      <div className="p-4 border-b border-zinc-800 flex items-center gap-2">
        <Zap size={18} className="text-amber-400" />
        <span className="font-bold text-sm tracking-tight">OCE</span>
      </div>
      <nav className="flex-1 p-2 space-y-0.5">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60"
              }`}
            >
              <Icon size={15} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
