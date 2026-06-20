"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import { ExternalLink, ChevronRight } from "lucide-react";

const STATUS_COLOR: Record<string, string> = {
  discovered: "bg-zinc-700 text-zinc-300",
  intel_done: "bg-amber-400/20 text-amber-400",
  analyzed: "bg-blue-400/20 text-blue-400",
  outreach_ready: "bg-green-400/20 text-green-400",
};

export default function CompaniesPage() {
  const [search, setSearch] = useState({ city: "", sector: "", status: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["companies", search],
    queryFn: () => api.getCompanies(Object.fromEntries(Object.entries(search).filter(([, v]) => v))),
  });

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Companies</h1>
        <span className="text-sm text-zinc-500">{data?.total ?? 0} total</span>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        {(["city", "sector", "status"] as const).map((key) => (
          <input
            key={key}
            placeholder={`Filter by ${key}...`}
            className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm flex-1"
            value={search[key]}
            onChange={(e) => setSearch((s) => ({ ...s, [key]: e.target.value }))}
          />
        ))}
      </div>

      {/* Table */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-500 text-xs">
              <th className="text-left px-4 py-3 font-medium">Company</th>
              <th className="text-left px-4 py-3 font-medium">Sector</th>
              <th className="text-left px-4 py-3 font-medium">Stage</th>
              <th className="text-left px-4 py-3 font-medium">Source</th>
              <th className="text-left px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={6} className="text-center py-12 text-zinc-600">Loading...</td></tr>
            ) : data?.items.length === 0 ? (
              <tr><td colSpan={6} className="text-center py-12 text-zinc-600">No companies yet. Run the pipeline first.</td></tr>
            ) : (
              data?.items.map((c) => (
                <tr key={c.id} className="border-b border-zinc-800/60 hover:bg-zinc-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium">{c.name}</p>
                      {c.website && (
                        <a href={c.website} target="_blank" rel="noopener noreferrer" className="text-xs text-zinc-500 hover:text-zinc-300 flex items-center gap-1">
                          {c.city} <ExternalLink size={10} />
                        </a>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-zinc-400">{c.sector}</td>
                  <td className="px-4 py-3 text-zinc-400 capitalize">{c.stage || "—"}</td>
                  <td className="px-4 py-3 text-zinc-400 uppercase text-xs">{c.source}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLOR[c.status] || STATUS_COLOR.discovered}`}>
                      {c.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link href={`/companies/${c.id}`} className="text-zinc-500 hover:text-white">
                      <ChevronRight size={16} />
                    </Link>
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
