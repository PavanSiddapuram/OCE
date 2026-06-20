"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import { PipelineStatus, Company } from "@/types";
import { Play, Loader2, CheckCircle, XCircle, Zap } from "lucide-react";

const SECTORS = ["AI", "Developer Tools", "Manufacturing", "Deeptech", "Robotics", "Fintech", "Healthtech", "SaaS"];
const CITIES = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Singapore", "San Francisco"];
const AGENT_LABELS: Record<string, string> = {
  agent1_discovery: "Discovering startups",
  agent2_intelligence: "Gathering company intelligence",
  agent3_opportunity: "Detecting opportunities",
  agent4_skill_match: "Scoring skill fit",
  agent5_pow: "Generating PoW ideas",
  agent6_founder_research: "Researching founders",
  agent7_narrative: "Writing outreach",
  agent8_crm_updater: "Updating CRM",
};

export default function DiscoverPage() {
  const [form, setForm] = useState({ city: "Bengaluru", sector: "AI", max_companies: 10, resume_text: "" });
  const [runId, setRunId] = useState<string | null>(null);

  const { data: status } = useQuery<PipelineStatus>({
    queryKey: ["pipeline", runId],
    queryFn: () => api.getPipelineStatus(runId!),
    enabled: !!runId && !["completed", "failed"].includes(""),
    refetchInterval: (query) => {
      const s = query.state.data?.status;
      return s === "completed" || s === "failed" ? false : 3000;
    },
  });

  const { data: companiesData } = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.getCompanies({ limit: 20 }),
    refetchInterval: runId && status?.status === "running" ? 5000 : false,
  });

  const mutation = useMutation({
    mutationFn: api.runPipeline,
    onSuccess: (data) => {
      setRunId(data.pipeline_run_id);
      queryClient.invalidateQueries({ queryKey: ["pipeline"] });
    },
  });

  const isRunning = status?.status === "running" || status?.status === "pending";
  const agentsDone = status?.agents_done?.length ?? 0;
  const totalAgents = 8;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Pipeline Control</h1>
        <p className="text-zinc-400 text-sm mt-1">Run the discovery pipeline to find startup opportunities.</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Form */}
        <div className="col-span-1 bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-4">
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">City</label>
            <select
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm"
              value={form.city}
              onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
            >
              {CITIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">Sector</label>
            <select
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm"
              value={form.sector}
              onChange={(e) => setForm((f) => ({ ...f, sector: e.target.value }))}
            >
              {SECTORS.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">Max companies: {form.max_companies}</label>
            <input
              type="range" min={5} max={50} step={5}
              value={form.max_companies}
              onChange={(e) => setForm((f) => ({ ...f, max_companies: +e.target.value }))}
              className="w-full accent-amber-400"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-400 mb-1 block">Your Resume</label>
            <textarea
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm h-40 resize-none"
              placeholder="Paste your resume text here..."
              value={form.resume_text}
              onChange={(e) => setForm((f) => ({ ...f, resume_text: e.target.value }))}
            />
          </div>
          <button
            onClick={() => mutation.mutate(form)}
            disabled={isRunning || !form.resume_text.trim()}
            className="w-full flex items-center justify-center gap-2 bg-amber-400 hover:bg-amber-300 text-black font-semibold rounded-lg py-2.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isRunning ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
            {isRunning ? "Running..." : "Run Pipeline"}
          </button>
        </div>

        {/* Status */}
        <div className="col-span-2 space-y-4">
          {status && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {status.status === "completed" && <CheckCircle size={16} className="text-green-400" />}
                  {status.status === "failed" && <XCircle size={16} className="text-red-400" />}
                  {isRunning && <Loader2 size={16} className="animate-spin text-amber-400" />}
                  <span className="font-medium text-sm capitalize">{status.status}</span>
                </div>
                <span className="text-xs text-zinc-500">{status.total_companies} companies found</span>
              </div>
              {isRunning && (
                <>
                  <div className="w-full bg-zinc-800 rounded-full h-1.5">
                    <div
                      className="bg-amber-400 h-1.5 rounded-full transition-all"
                      style={{ width: `${(agentsDone / totalAgents) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-zinc-400">
                    {status.current_agent ? AGENT_LABELS[status.current_agent] || status.current_agent : "Starting..."}
                  </p>
                </>
              )}
              {status.error_message && (
                <p className="text-xs text-red-400 bg-red-400/10 rounded-lg p-2">{status.error_message}</p>
              )}
            </div>
          )}

          {/* Company cards */}
          <div className="grid grid-cols-2 gap-3">
            {companiesData?.items.map((company: Company) => (
              <a key={company.id} href={`/companies/${company.id}`} className="block bg-zinc-900 border border-zinc-800 hover:border-zinc-600 rounded-xl p-3 transition-colors">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-sm">{company.name}</p>
                    <p className="text-xs text-zinc-500">{company.sector} · {company.city}</p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${
                    company.status === "outreach_ready" ? "bg-green-400/20 text-green-400" :
                    company.status === "analyzed" ? "bg-blue-400/20 text-blue-400" :
                    company.status === "intel_done" ? "bg-amber-400/20 text-amber-400" :
                    "bg-zinc-700 text-zinc-400"
                  }`}>
                    {company.status.replace("_", " ")}
                  </span>
                </div>
                {company.mission && (
                  <p className="text-xs text-zinc-400 mt-2 line-clamp-2">{company.mission}</p>
                )}
                <div className="flex gap-1 mt-2 flex-wrap">
                  {company.tech_stack?.slice(0, 3).map((t) => (
                    <span key={t} className="text-xs bg-zinc-800 px-2 py-0.5 rounded text-zinc-400">{t}</span>
                  ))}
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
