"use client";

import { useEffect, useState } from "react";
import { Target, CheckCircle2, XCircle, Clock, ExternalLink, Activity, Sparkles, Award } from "lucide-react";
import { api } from "@/lib/api";

export default function OpportunityEnginePage() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBrief, setSelectedBrief] = useState<any>(null);

  useEffect(() => {
    loadOpps();
  }, []);

  const loadOpps = () => {
    api.getOpportunities()
      .then((res) => setOpportunities(res.items || []))
      .catch((err) => console.error("Failed to load opportunities:", err))
      .finally(() => setLoading(false));
  };

  const handleReview = async (id: string, action: "approve" | "snooze" | "archive") => {
    try {
      await api.reviewOpportunity(id, action);
      loadOpps();
    } catch (err) {
      console.error("Review opportunity failed:", err);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh] text-zinc-400">
        <Activity className="animate-spin mr-2" size={20} />
        Scoring opportunities with 7-signal Opportunity Engine...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Target className="text-amber-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Opportunity Engine (7-Signal Matcher)</h1>
          </div>
          <p className="text-zinc-400 text-xs mt-1">
            Matches Candidate Proof & Edge to Target Teams, Research Problems & Key People (No Blind Apply Policy)
          </p>
        </div>

        <div className="text-right font-mono text-xs text-zinc-400">
          <div>Composite Score Weights</div>
          <div className="text-amber-400 font-bold text-[10px]">
            30% Fit • 20% Proof • 15% Problem • 10% Gap • 10% Network • 10% Role • 5% Edge
          </div>
        </div>
      </div>

      {/* Opportunity List */}
      <div className="space-y-6">
        {opportunities.map((opp) => (
          <div
            key={opp.id}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-amber-500/30 transition-all shadow-sm space-y-4"
          >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-zinc-800 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-bold uppercase tracking-wider">
                    {opp.target_type || "Research Team"}
                  </span>
                  <span className="text-xs font-semibold text-zinc-300">{opp.target_name}</span>
                </div>
                <h2 className="text-lg font-bold text-white">{opp.title}</h2>
              </div>

              {/* Score Gauge */}
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">7-Signal Score</div>
                  <div className="text-2xl font-extrabold text-amber-400 font-mono">{opp.fit_score}/100</div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleReview(opp.id, "approve")}
                    className={`px-3 py-1.5 rounded text-xs font-bold transition-all ${
                      opp.status === "approved"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                        : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700"
                    }`}
                  >
                    Approve Target
                  </button>
                  <button
                    onClick={() => handleReview(opp.id, "snooze")}
                    className="px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-400 text-xs font-semibold"
                  >
                    Snooze
                  </button>
                </div>
              </div>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">{opp.description}</p>

            {/* 7 Signals Breakdown Grid */}
            {opp.signal_scores && (
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 bg-zinc-950 p-3 rounded-lg border border-zinc-800 text-[10px] font-mono">
                <div>
                  <div className="text-zinc-500">Tech Fit (30%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.technical_fit}</div>
                </div>
                <div>
                  <div className="text-zinc-500">Evidence (20%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.evidence_strength}</div>
                </div>
                <div>
                  <div className="text-zinc-500">Problem (15%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.problem_relevance}</div>
                </div>
                <div>
                  <div className="text-zinc-500">Gap Close (10%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.gap_closability}</div>
                </div>
                <div>
                  <div className="text-zinc-500">Network (10%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.relationship_access}</div>
                </div>
                <div>
                  <div className="text-zinc-500">Role Avail (10%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.role_availability}</div>
                </div>
                <div>
                  <div className="text-zinc-500">Edge (5%)</div>
                  <div className="font-bold text-amber-400">{opp.signal_scores.strategic_uniqueness}</div>
                </div>
              </div>
            )}

            {/* Opportunity Brief Button */}
            {opp.brief && (
              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={() => setSelectedBrief(opp.brief)}
                  className="text-xs text-amber-400 hover:underline flex items-center gap-1 font-bold"
                >
                  <Sparkles size={14} /> Open Complete Opportunity Brief & Outreach Brief
                </button>
                <span className="text-[10px] text-zinc-500">Google Careers Cap: 3 Applications / 30 Days</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Brief Modal */}
      {selectedBrief && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-2xl w-full space-y-5 my-8">
            <div className="flex justify-between items-center border-b border-zinc-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Award className="text-amber-400" size={20} /> Opportunity Brief
              </h2>
              <button
                onClick={() => setSelectedBrief(null)}
                className="text-zinc-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs text-zinc-300">
              <div className="p-3.5 rounded bg-zinc-950 border border-zinc-800">
                <strong className="text-amber-400 block mb-1">Target Problem:</strong>
                <p>{selectedBrief.problem}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded bg-zinc-950 border border-zinc-800">
                  <strong className="text-amber-400 block mb-1">Why Now:</strong>
                  <p>{selectedBrief.why_now}</p>
                </div>
                <div className="p-3 rounded bg-zinc-950 border border-zinc-800">
                  <strong className="text-amber-400 block mb-1">Why You (Candidate Fit):</strong>
                  <p>{selectedBrief.why_you}</p>
                </div>
              </div>

              <div className="p-3.5 rounded bg-zinc-950 border border-zinc-800">
                <strong className="text-amber-400 block mb-1">Build Next (Mini PoW):</strong>
                <p>{selectedBrief.build_next}</p>
              </div>

              <div className="p-3.5 rounded bg-amber-500/10 border border-amber-500/30">
                <strong className="text-amber-300 block mb-1">Technical Outreach Conversation Angle (Human Approval Required):</strong>
                <p className="italic">{selectedBrief.conversation_angle}</p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedBrief(null)}
                className="px-4 py-2 rounded bg-amber-500 text-zinc-950 font-bold text-xs"
              >
                Close Brief
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
