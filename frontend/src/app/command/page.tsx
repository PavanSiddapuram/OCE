"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ShieldAlert, Zap, Cpu, Sparkles, FileCheck, Target, ArrowRight, CheckCircle2, AlertTriangle, Activity } from "lucide-react";
import { api } from "@/lib/api";

export default function CommandCenter() {
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCandidateState()
      .then((data) => setState(data))
      .catch((err) => console.error("Error loading candidate state:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh] text-zinc-400">
        <Activity className="animate-spin mr-2" size={20} />
        Initializing FRONTIER OS Command Center...
      </div>
    );
  }

  const profile = state?.profile || {};
  const skills = state?.skills || [];
  const failures = state?.failures || [];
  const weekly = state?.weekly_plan || {};
  const events = state?.recent_events || [];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* North-Star Header */}
      <div className="bg-gradient-to-r from-amber-500/10 via-zinc-900 to-zinc-950 border border-amber-500/30 rounded-xl p-6 relative overflow-hidden shadow-lg">
        <div className="absolute top-0 right-0 p-8 text-amber-500/10 font-mono font-bold text-6xl select-none pointer-events-none">
          FRONTIER OS
        </div>

        <div className="flex items-center gap-3 mb-2">
          <span className="px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 text-[11px] font-bold tracking-wide uppercase">
            Trajectory: Google DeepMind / SWE AI-ML
          </span>
          <span className="text-zinc-500 text-xs">• 6-7 Month Window (Aug '26 → Mar '27)</span>
        </div>

        <h1 className="text-2xl font-bold text-white tracking-tight mb-2">
          Pavan Siddapuram — Personal Control Center
        </h1>
        <p className="text-zinc-300 text-sm max-w-3xl leading-relaxed">
          <strong className="text-amber-400 font-semibold">North-Star Focus:</strong> “What is the highest-leverage thing Pavan can do this week that makes him technically stronger and more legible to a top team?”
        </p>

        {/* Quick Trajectory Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-zinc-800/80">
          <div>
            <div className="text-[11px] text-zinc-500 font-medium">Candidate Edge</div>
            <div className="text-xs font-semibold text-zinc-200 mt-0.5">Geometry × WebGPU × AI Systems</div>
          </div>
          <div>
            <div className="text-[11px] text-zinc-500 font-medium">Track A (Interview)</div>
            <div className="text-xs font-semibold text-emerald-400 mt-0.5">DSA, Pressure Coding, LLD</div>
          </div>
          <div>
            <div className="text-[11px] text-zinc-500 font-medium">Track B (Research)</div>
            <div className="text-xs font-semibold text-sky-400 mt-0.5">3DGS, Spatial AI, SIMA 2</div>
          </div>
          <div>
            <div className="text-[11px] text-zinc-500 font-medium">Daily Time Allocation</div>
            <div className="text-xs font-semibold text-amber-400 mt-0.5">60 – 90 mins / day</div>
          </div>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col (2-Span): Weekly Must-Win Outcomes & Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Weekly Priorities Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <ShieldAlert className="text-amber-400" size={20} />
                <h2 className="text-base font-bold text-white">This Week's Must-Win Priorities</h2>
              </div>
              <Link href="/weekly" className="text-xs text-amber-400 hover:underline flex items-center gap-1 font-medium">
                Manage Weekly Coordinator <ArrowRight size={13} />
              </Link>
            </div>

            {weekly?.priorities?.length > 0 ? (
              <div className="space-y-3">
                {weekly.priorities.map((item: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-lg bg-zinc-950/60 border border-zinc-800/80 flex items-start gap-3 hover:border-zinc-700 transition-all">
                    <div className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">{item.track}</span>
                        <span className="text-[11px] text-zinc-500">{item.estimated_hours}h allocated</span>
                      </div>
                      <h3 className="text-sm font-bold text-zinc-100 mt-1">{item.title}</h3>
                      <p className="text-xs text-zinc-400 mt-1">Target Metric: {item.target_metric}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-zinc-950/40 text-center text-zinc-500 text-xs">
                No priorities generated for this week yet. Click below to generate.
              </div>
            )}
          </div>

          {/* Quick Execution Action Hub */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/interview"
              className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 hover:bg-zinc-800/50 transition-all group"
            >
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-3 group-hover:scale-105 transition-transform">
                <Cpu size={20} />
              </div>
              <h3 className="text-sm font-bold text-white group-hover:text-amber-400 transition-colors">Start Track A Mock</h3>
              <p className="text-xs text-zinc-400 mt-1">Adaptive pressure coding & reasoning session</p>
            </Link>

            <Link
              href="/research"
              className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 hover:bg-zinc-800/50 transition-all group"
            >
              <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 mb-3 group-hover:scale-105 transition-transform">
                <Sparkles size={20} />
              </div>
              <h3 className="text-sm font-bold text-white group-hover:text-amber-400 transition-colors">Log Research Experiment</h3>
              <p className="text-xs text-zinc-400 mt-1">Record baseline metrics, ablations & code commit</p>
            </Link>

            <Link
              href="/opportunities"
              className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-amber-500/40 hover:bg-zinc-800/50 transition-all group"
            >
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-3 group-hover:scale-105 transition-transform">
                <Target size={20} />
              </div>
              <h3 className="text-sm font-bold text-white group-hover:text-amber-400 transition-colors">Opportunity Engine</h3>
              <p className="text-xs text-zinc-400 mt-1">7-Signal matched DeepMind & target teams</p>
            </Link>
          </div>

          {/* Candidate Skill & Posterior Radar */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-base font-bold text-white mb-4">Demonstrated Candidate Skill State</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {skills.map((s: any) => (
                <div key={s.skill_id} className="p-3.5 rounded-lg bg-zinc-950/60 border border-zinc-800">
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="font-semibold text-zinc-200 capitalize">{s.skill_id.replace(/_/g, " ")}</span>
                    <span className="font-mono text-amber-400 font-bold">{s.score}/100</span>
                  </div>
                  <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-amber-500 to-amber-400 h-full rounded-full transition-all duration-500"
                      style={{ width: `${s.score}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-zinc-500 mt-1.5 flex justify-between">
                    <span>Confidence: {(s.confidence * 100).toFixed(0)}%</span>
                    <span>Posterior score</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Col: Failure Fingerprints & Audit Log */}
        <div className="space-y-6">

          {/* Failure Fingerprints Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="text-amber-400" size={18} />
              <h2 className="text-base font-bold text-white">Active Failure Fingerprints</h2>
            </div>
            <p className="text-xs text-zinc-400 mb-4">
              Recurring weakness observations that drive target adaptive training.
            </p>

            <div className="space-y-3">
              {failures.map((f: any) => (
                <div key={f.id} className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800/80">
                  <div className="flex items-center justify-between text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">
                    <span>{f.domain}</span>
                    <span className="px-1.5 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20 text-[10px]">
                      Count: {f.count}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-200 font-medium">{f.pattern}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Audit Event Stream */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="text-amber-400" size={18} />
              <h2 className="text-base font-bold text-white">Audit Event Stream</h2>
            </div>

            <div className="space-y-3 font-mono text-[11px] max-h-72 overflow-y-auto pr-1">
              {events.map((ev: any) => (
                <div key={ev.id} className="p-2.5 rounded bg-zinc-950 border border-zinc-800/50">
                  <div className="flex justify-between text-zinc-400">
                    <span className="text-amber-400 font-semibold">{ev.event_type}</span>
                    <span className="text-[10px] text-zinc-500">
                      {ev.created_at ? new Date(ev.created_at).toLocaleTimeString() : ""}
                    </span>
                  </div>
                  <div className="text-zinc-500 mt-1 truncate">Ref: {ev.entity_ref}</div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
