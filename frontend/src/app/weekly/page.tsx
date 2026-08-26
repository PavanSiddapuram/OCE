"use client";

import { useEffect, useState } from "react";
import { Calendar, ShieldAlert, RefreshCw, CheckCircle2, Clock, Activity, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";

export default function WeeklyCoordinatorPage() {
  const [weeklyPlan, setWeeklyPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadWeeklyPlan();
  }, []);

  const loadWeeklyPlan = () => {
    api.getWeeklyPlan()
      .then((data) => setWeeklyPlan(data))
      .catch((err) => console.error("Failed to load weekly plan:", err))
      .finally(() => setLoading(false));
  };

  const handleGeneratePlan = async () => {
    setGenerating(true);
    try {
      const data = await api.generateWeeklyPlan();
      setWeeklyPlan(data);
    } catch (err) {
      console.error("Generate weekly plan failed:", err);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh] text-zinc-400">
        <Activity className="animate-spin mr-2" size={20} />
        Loading Weekly Coordinator Control Plane...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Calendar className="text-amber-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Weekly Coordinator Control Plane</h1>
          </div>
          <p className="text-zinc-400 text-xs mt-1">
            7-Day Time Budget & Priority Outcome Planner (Rule: Max 3 "Must-Win" Priorities)
          </p>
        </div>

        <button
          onClick={handleGeneratePlan}
          disabled={generating}
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs flex items-center gap-2 transition-all shadow"
        >
          {generating ? <RefreshCw className="animate-spin" size={14} /> : <RefreshCw size={14} />}
          Run Sunday Priority Selection Algorithm
        </button>
      </div>

      {/* Overview Banner */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="text-xs text-amber-400 font-semibold uppercase tracking-wider">
            Active Week: {weeklyPlan?.week_start || "Current Week"}
          </div>
          <h2 className="text-lg font-bold text-white mt-0.5">
            Priority Formula: (Impact × Weakness Reduction × Evidence Value × Urgency) / Effort
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Daily Budget: 90 Minutes Focus Block (45m Track A Interview Prep + 45m Track B Research)
          </p>
        </div>

        <div className="flex gap-4 text-xs">
          <div className="px-4 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-center">
            <div className="text-zinc-500">Track A Quota</div>
            <div className="text-sm font-bold text-emerald-400">{weeklyPlan?.track_a_quota || 5} sessions/wk</div>
          </div>
          <div className="px-4 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-center">
            <div className="text-zinc-500">Track B Quota</div>
            <div className="text-sm font-bold text-sky-400">{weeklyPlan?.track_b_quota || 2} experiments/wk</div>
          </div>
        </div>
      </div>

      {/* 3 Must-Win Priorities Breakdown */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <ShieldAlert className="text-amber-400" size={18} /> Allocated Must-Win Priority Outcomes
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {weeklyPlan?.priorities?.map((item: any, idx: number) => (
            <div key={idx} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-3 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="w-7 h-7 rounded-full bg-amber-500/20 text-amber-400 font-bold text-xs flex items-center justify-center">
                  #{idx + 1}
                </span>
                <span className="px-2 py-0.5 rounded bg-zinc-800 text-amber-300 text-[10px] font-semibold uppercase">
                  {item.track}
                </span>
              </div>

              <h4 className="text-sm font-bold text-white leading-snug">{item.title}</h4>

              <div className="p-3 rounded bg-zinc-950 border border-zinc-800 text-xs text-zinc-300">
                <strong className="text-amber-400">Target Metric:</strong> {item.target_metric}
              </div>

              <div className="text-[11px] text-zinc-500 flex items-center justify-between pt-2 border-t border-zinc-800">
                <span className="flex items-center gap-1"><Clock size={12} /> {item.estimated_hours} Hours</span>
                <span className="text-emerald-400 font-medium flex items-center gap-1"><CheckCircle2 size={12} /> Scheduled</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
