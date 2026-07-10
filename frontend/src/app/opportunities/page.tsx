"use client";

import { Fragment, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import { Opportunity, PressureTest } from "@/types";
import { Gauge, Loader2 } from "lucide-react";

const CATEGORIES = ["", "bottleneck", "growth_lever", "missing_piece", "technical_debt"];
const CATEGORY_LABEL: Record<string, string> = {
  bottleneck: "Bottleneck",
  growth_lever: "Growth Lever",
  missing_piece: "Missing Piece",
  technical_debt: "Tech Debt",
};
const CATEGORY_COLOR: Record<string, string> = {
  bottleneck: "text-red-400 bg-red-400/10",
  growth_lever: "text-green-400 bg-green-400/10",
  missing_piece: "text-blue-400 bg-blue-400/10",
  technical_debt: "text-orange-400 bg-orange-400/10",
};
const VERDICT_COLOR: Record<PressureTest["verdict"], string> = {
  BUILD: "text-green-400 bg-green-400/10 border-green-400/30",
  RESHAPE: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  SKIP: "text-red-400 bg-red-400/10 border-red-400/30",
};

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-zinc-600 text-xs font-mono">—</span>;
  const color = score >= 80 ? "text-green-400" : score >= 60 ? "text-amber-400" : "text-zinc-500";
  return <span className={`text-lg font-bold font-mono ${color}`}>{score}</span>;
}

function PressureTestDetail({ pt }: { pt: PressureTest }) {
  return (
    <div className="space-y-3 text-xs">
      <div>
        <p className="text-zinc-500 uppercase tracking-wide mb-1">Core assumption</p>
        <p className="text-zinc-300">{pt.core_assumption}</p>
      </div>
      <div>
        <p className="text-zinc-500 uppercase tracking-wide mb-1">Fatal flaws</p>
        <div className="space-y-2">
          {pt.fatal_flaws.map((f, i) => (
            <div key={i} className="border-l-2 border-red-400/40 pl-3">
              <p className="font-semibold text-red-300">{f.label}</p>
              <p className="text-zinc-400">{f.why_it_kills}</p>
              <p className="text-zinc-500 mt-0.5">Overcome if: {f.what_overcomes}</p>
            </div>
          ))}
        </div>
      </div>
      <div>
        <p className="text-zinc-500 uppercase tracking-wide mb-1">Why the founder shrugs</p>
        <p className="text-zinc-400">{pt.founder_shrug_risk}</p>
      </div>
      <div>
        <p className="text-zinc-500 uppercase tracking-wide mb-1">Cut to ship in one weekend</p>
        <ul className="list-disc list-inside text-zinc-400 space-y-0.5">
          {pt.cuts_for_weekend.map((c, i) => <li key={i}>{c}</li>)}
        </ul>
      </div>
      <div>
        <p className="text-zinc-500 uppercase tracking-wide mb-1">Verdict</p>
        <p className="text-zinc-300">{pt.verdict_reasoning}</p>
      </div>
    </div>
  );
}

export default function OpportunitiesPage() {
  const [category, setCategory] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["opportunities", category, minScore],
    queryFn: () => api.getOpportunities({
      ...(category && { category }),
      ...(minScore > 0 && { min_score: minScore }),
      limit: 50,
    }),
  });

  const pressureTest = useMutation({
    mutationFn: (id: string) => api.pressureTestOpportunity(id),
    onSuccess: (opp) => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      setExpandedId(opp.id);
    },
  });

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Opportunities</h1>
        <span className="text-sm text-zinc-500">{data?.total ?? 0} total</span>
      </div>

      <div className="flex gap-3 items-center">
        <select
          className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORIES.map((c) => <option key={c} value={c}>{c ? CATEGORY_LABEL[c] : "All Categories"}</option>)}
        </select>
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-500">Min score: {minScore}</span>
          <input
            type="range" min={0} max={90} step={10}
            value={minScore}
            onChange={(e) => setMinScore(+e.target.value)}
            className="accent-amber-400"
          />
        </div>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-500 text-xs">
              <th className="text-left px-4 py-3 font-medium w-12">Score</th>
              <th className="text-left px-4 py-3 font-medium">Opportunity</th>
              <th className="text-left px-4 py-3 font-medium">Category</th>
              <th className="text-left px-4 py-3 font-medium">PoW</th>
              <th className="text-left px-4 py-3 font-medium w-32">Gate</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={5} className="text-center py-12 text-zinc-600">Loading...</td></tr>
            ) : data?.items.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-12 text-zinc-600">No opportunities yet. Run the pipeline first.</td></tr>
            ) : (
              data?.items.map((o: Opportunity) => (
                <Fragment key={o.id}>
                  <tr className="border-b border-zinc-800/60 hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-3 text-center">
                      <ScoreBadge score={o.fit_score} />
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/companies/${o.company_id}`} className="hover:text-amber-400 transition-colors">
                        <p className="font-medium">{o.title}</p>
                        <p className="text-xs text-zinc-500 mt-0.5 line-clamp-1">{o.description}</p>
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      {o.category && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${CATEGORY_COLOR[o.category] || "text-zinc-400 bg-zinc-800"}`}>
                          {CATEGORY_LABEL[o.category] || o.category}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {o.pow_idea ? (
                        <span className="text-xs text-green-400">✓ Generated</span>
                      ) : (
                        <span className="text-xs text-zinc-600">Pending</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {o.pressure_test ? (
                        <button
                          onClick={() => setExpandedId(expandedId === o.id ? null : o.id)}
                          className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${VERDICT_COLOR[o.pressure_test.verdict]}`}
                        >
                          {o.pressure_test.verdict}
                        </button>
                      ) : (
                        <button
                          onClick={() => pressureTest.mutate(o.id)}
                          disabled={pressureTest.isPending}
                          className="flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-zinc-700 text-zinc-400 hover:border-amber-400 hover:text-amber-400 transition-colors disabled:opacity-50"
                        >
                          {pressureTest.isPending && pressureTest.variables === o.id
                            ? <Loader2 size={11} className="animate-spin" />
                            : <Gauge size={11} />}
                          Pressure Test
                        </button>
                      )}
                    </td>
                  </tr>
                  {expandedId === o.id && o.pressure_test && (
                    <tr className="border-b border-zinc-800/60 bg-zinc-950/60">
                      <td colSpan={5} className="px-6 py-4">
                        <PressureTestDetail pt={o.pressure_test} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
