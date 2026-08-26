"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldAlert, Cpu, Sparkles, FileCheck, Target, Calendar, Users, Building2 } from "lucide-react";

const nav = [
  { href: "/command", label: "Command Center", icon: ShieldAlert },
  { href: "/interview", label: "Track A: Interview OS", icon: Cpu },
  { href: "/research", label: "Track B: Research Lab", icon: Sparkles },
  { href: "/evidence", label: "Evidence & Proof", icon: FileCheck },
  { href: "/opportunities", label: "Opportunity Engine", icon: Target },
  { href: "/weekly", label: "Weekly Coordinator", icon: Calendar },
  { href: "/crm", label: "People & CRM", icon: Users },
  { href: "/companies", label: "Startups Track", icon: Building2 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 border-r border-zinc-800 bg-zinc-950 flex flex-col">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-xs">
            F
          </div>
          <div>
            <div className="font-bold text-sm tracking-tight text-white">FRONTIER OS</div>
            <div className="text-[10px] text-amber-400 font-medium">DeepMind Trajectory</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        <div className="px-3 pt-2 pb-1 text-[10px] font-semibold uppercase text-zinc-500 tracking-wider">
          Core Operating System
        </div>
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                active
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900"
              }`}
            >
              <Icon size={16} className={active ? "text-amber-400" : "text-zinc-400"} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-zinc-800 bg-zinc-900/50">
        <div className="text-[11px] text-zinc-400 flex items-center justify-between">
          <span>Target Horizon</span>
          <span className="text-amber-400 font-semibold">Aug '26 - Mar '27</span>
        </div>
        <div className="mt-1 text-[10px] text-zinc-500">
          Edge: Geometry × WebGPU × AI Systems
        </div>
      </div>
    </aside>
  );
}
