"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import { Opportunity } from "@/types";

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

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-zinc-600 text-xs font-mono">—</span>;
  const color = score >= 80 ? "text-green-400" : score >= 60 ? "text-amber-400" : "text-zinc-500";
  return <span className={`text-lg font-bold font-mono ${color}`}>{score}</span>;
}

export default function OpportunitiesPage() {
  const [category, setCategory] = useState("");
  const [minScore, setMinScore] = useState(0);

  const { data, isLoading } = useQuery({
    queryKey: ["opportunities", category, minScore],
    queryFn: () => api.getOpportunities({
      ...(category && { category }),
      ...(minScore > 0 && { min_score: minScore }),
      limit: 50,
    }),
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
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={4} className="text-center py-12 text-zinc-600">Loading...</td></tr>
            ) : data?.items.length === 0 ? (
              <tr><td colSpan={4} className="text-center py-12 text-zinc-600">No opportunities yet. Run the pipeline first.</td></tr>
            ) : (
              data?.items.map((o: Opportunity) => (
                <tr key={o.id} className="border-b border-zinc-800/60 hover:bg-zinc-800/30 transition-colors">
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
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
