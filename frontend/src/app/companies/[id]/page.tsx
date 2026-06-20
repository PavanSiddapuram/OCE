"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Opportunity, Founder, Outreach } from "@/types";
import { ExternalLink, Copy, Check, Star } from "lucide-react";

const TABS = ["Intelligence", "Opportunities", "Founders", "Outreach"] as const;

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} className="p-1.5 rounded hover:bg-zinc-700 text-zinc-500 hover:text-zinc-200 transition-colors">
      {copied ? <Check size={13} className="text-green-400" /> : <Copy size={13} />}
    </button>
  );
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-zinc-600 text-xs">—</span>;
  const color = score >= 80 ? "text-green-400 bg-green-400/10" : score >= 60 ? "text-amber-400 bg-amber-400/10" : "text-zinc-400 bg-zinc-800";
  return <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${color}`}>{score}</span>;
}

export default function CompanyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<typeof TABS[number]>("Intelligence");

  const { data: company, isLoading } = useQuery({
    queryKey: ["company", id],
    queryFn: () => api.getCompany(id),
    enabled: !!id,
  });

  if (isLoading) return <div className="text-zinc-600 py-20 text-center">Loading...</div>;
  if (!company) return <div className="text-zinc-600 py-20 text-center">Company not found</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">{company.name}</h1>
            <div className="flex items-center gap-3 mt-1 text-sm text-zinc-400">
              <span>{company.sector}</span>
              <span>·</span>
              <span>{company.city}</span>
              <span>·</span>
              <span className="capitalize">{company.stage || "Stage unknown"}</span>
              {company.website && (
                <>
                  <span>·</span>
                  <a href={company.website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:text-white">
                    Website <ExternalLink size={11} />
                  </a>
                </>
              )}
            </div>
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${
            company.status === "outreach_ready" ? "bg-green-400/20 text-green-400" :
            company.status === "analyzed" ? "bg-blue-400/20 text-blue-400" :
            "bg-zinc-700 text-zinc-400"
          }`}>{company.status.replace("_", " ")}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-zinc-800">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm transition-colors ${
              tab === t ? "text-white border-b-2 border-amber-400" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {t}
            {t === "Opportunities" && company.opportunities.length > 0 && (
              <span className="ml-1.5 text-xs text-zinc-600">({company.opportunities.length})</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === "Intelligence" && (
        <div className="space-y-4">
          {company.mission && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
              <p className="text-xs text-zinc-500 mb-1">Mission</p>
              <p className="text-sm">{company.mission}</p>
            </div>
          )}
          {company.product_summary && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
              <p className="text-xs text-zinc-500 mb-1">Product</p>
              <p className="text-sm">{company.product_summary}</p>
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            {company.recent_launches && company.recent_launches.length > 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                <p className="text-xs text-zinc-500 mb-2">Recent Launches</p>
                <ul className="space-y-1">
                  {company.recent_launches.map((l, i) => (
                    <li key={i} className="text-sm flex items-start gap-2"><span className="text-amber-400 mt-0.5">·</span>{l}</li>
                  ))}
                </ul>
              </div>
            )}
            {company.tech_stack && company.tech_stack.length > 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                <p className="text-xs text-zinc-500 mb-2">Tech Stack</p>
                <div className="flex flex-wrap gap-1.5">
                  {company.tech_stack.map((t) => (
                    <span key={t} className="text-xs bg-zinc-800 border border-zinc-700 px-2 py-0.5 rounded">{t}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
          {company.current_focus && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
              <p className="text-xs text-zinc-500 mb-1">Current Focus</p>
              <p className="text-sm">{company.current_focus}</p>
            </div>
          )}
        </div>
      )}

      {tab === "Opportunities" && (
        <div className="space-y-3">
          {company.opportunities.length === 0 ? (
            <p className="text-zinc-600 text-sm">No opportunities yet. Wait for agent 3 to complete.</p>
          ) : (
            company.opportunities
              .sort((a, b) => (b.fit_score ?? 0) - (a.fit_score ?? 0))
              .map((o: Opportunity) => (
                <div key={o.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-2">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-sm">{o.title}</p>
                      <p className="text-xs text-zinc-500 capitalize">{o.category?.replace("_", " ")}</p>
                    </div>
                    <ScoreBadge score={o.fit_score} />
                  </div>
                  <p className="text-sm text-zinc-400">{o.description}</p>
                  {o.impact && <p className="text-xs text-zinc-500 italic">{o.impact}</p>}
                  {o.fit_reasoning && (
                    <p className="text-xs text-zinc-400 bg-zinc-800 rounded-lg p-2">{o.fit_reasoning}</p>
                  )}
                  {o.pow_idea && (
                    <details className="text-xs">
                      <summary className="text-amber-400 cursor-pointer hover:text-amber-300">PoW Idea</summary>
                      <pre className="mt-2 text-zinc-400 whitespace-pre-wrap bg-zinc-800 rounded-lg p-3">{o.pow_idea}</pre>
                    </details>
                  )}
                  {o.skills_required && (
                    <div className="flex flex-wrap gap-1">
                      {o.skills_required.map((s) => (
                        <span key={s} className="text-xs bg-zinc-800 px-2 py-0.5 rounded text-zinc-500">{s}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))
          )}
        </div>
      )}

      {tab === "Founders" && (
        <div className="space-y-3">
          {company.founders.length === 0 ? (
            <p className="text-zinc-600 text-sm">No founder data yet. Wait for agent 6 to complete.</p>
          ) : (
            company.founders.map((f: Founder) => (
              <div key={f.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">{f.name}</p>
                    <p className="text-sm text-zinc-500">{f.role}</p>
                  </div>
                  <div className="flex gap-2">
                    {f.linkedin_url && (
                      <a href={f.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-xs text-zinc-500 hover:text-white flex items-center gap-1">
                        LinkedIn <ExternalLink size={10} />
                      </a>
                    )}
                  </div>
                </div>
                {f.background && <p className="text-sm text-zinc-400">{f.background}</p>}
                {f.complaints && f.complaints.length > 0 && (
                  <div>
                    <p className="text-xs text-zinc-500 mb-1.5">Pain Points <Star size={11} className="inline text-amber-400" /></p>
                    <ul className="space-y-1">
                      {f.complaints.map((c, i) => (
                        <li key={i} className="text-sm text-amber-400/80 bg-amber-400/5 rounded-lg px-3 py-1.5">"{c}"</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {tab === "Outreach" && (
        <div className="space-y-4">
          {company.outreach.length === 0 ? (
            <p className="text-zinc-600 text-sm">No outreach generated yet. Wait for agent 7 to complete.</p>
          ) : (
            company.outreach.map((o: Outreach) => (
              <div key={o.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400 bg-zinc-800 px-2 py-0.5 rounded">
                    {o.channel}
                  </span>
                  {o.body && <CopyButton text={o.body} />}
                </div>
                {[
                  ["Hook", o.hook],
                  ["Why this company", o.why_company],
                  ["Why this problem", o.why_problem],
                  ["Why me", o.why_me],
                  ["What I built", o.what_i_built],
                  ["Call to action", o.call_to_action],
                ].map(([label, text]) => text && (
                  <div key={label} className="space-y-0.5">
                    <p className="text-xs text-zinc-600">{label}</p>
                    <div className="flex items-start gap-2">
                      <p className="text-sm text-zinc-300 flex-1">{text}</p>
                      <CopyButton text={text} />
                    </div>
                  </div>
                ))}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
