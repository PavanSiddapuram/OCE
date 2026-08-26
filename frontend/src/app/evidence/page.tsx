"use client";

import { useEffect, useState } from "react";
import { FileCheck, ShieldCheck, ExternalLink, Plus, Copy, Check, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

export default function EvidenceStudio() {
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // New Evidence Modal
  const [showModal, setShowModal] = useState(false);
  const [claim, setClaim] = useState("");
  const [type, setType] = useState("benchmark");
  const [sourceUrl, setSourceUrl] = useState("");

  useEffect(() => {
    loadEvidence();
  }, []);

  const loadEvidence = () => {
    api.listEvidence()
      .then((data) => setEvidenceList(data))
      .catch((err) => console.error("Failed to load evidence:", err))
      .finally(() => setLoading(false));
  };

  const handleCreateEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim) return;
    try {
      await api.createEvidence({
        type,
        claim,
        source_url: sourceUrl,
        confidence: 0.9,
        supports: ["3d_geometry", "webgpu_wasm"],
      });
      setShowModal(false);
      setClaim("");
      setSourceUrl("");
      loadEvidence();
    } catch (err) {
      console.error("Create evidence failed:", err);
    }
  };

  const copyMarkdown = (item: any) => {
    const md = `### Evidence Artifact: ${item.claim}\n- Type: ${item.type}\n- Provenance: ${item.source_url || "Local benchmark"}\n- Confidence Rating: ${(item.confidence * 100).toFixed(0)}%\n- Verified Date: ${new Date(item.created_at).toLocaleDateString()}`;
    navigator.clipboard.writeText(md);
    setCopiedId(item.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <FileCheck className="text-emerald-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Evidence & Public Proof Studio</h1>
          </div>
          <p className="text-zinc-400 text-xs mt-1">
            Provenanced Claims, Benchmark Records, GitHub Repos & Public Evidence Graph
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-bold text-xs flex items-center gap-2 transition-all shadow"
        >
          <Plus size={14} /> Add Verified Evidence Claim
        </button>
      </div>

      {/* Main List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {evidenceList.map((item) => (
          <div key={item.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4 hover:border-zinc-700 transition-all shadow-sm">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold uppercase tracking-wider">
                {item.type} • Confidence {(item.confidence * 100).toFixed(0)}%
              </span>
              <button
                onClick={() => copyMarkdown(item)}
                className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 font-mono"
              >
                {copiedId === item.id ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                {copiedId === item.id ? "Copied" : "Copy Proof MD"}
              </button>
            </div>

            <p className="text-sm font-semibold text-zinc-100 leading-snug">{item.claim}</p>

            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-400 space-y-1">
              <div>
                <strong className="text-zinc-300">Provenance Notes:</strong> {item.provenance_notes || "Benchmarked & verified locally"}
              </div>
              {item.source_url && (
                <div className="flex items-center gap-1 text-emerald-400 pt-1">
                  <ExternalLink size={12} />
                  <a href={item.source_url} target="_blank" rel="noreferrer" className="hover:underline font-mono truncate">
                    {item.source_url}
                  </a>
                </div>
              )}
            </div>

            {item.supports && item.supports.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {item.supports.map((s: string) => (
                  <span key={s} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 text-[10px] font-mono">
                    #{s}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-lg w-full space-y-4">
            <h2 className="text-lg font-bold text-white">Record Evidence Claim</h2>
            <form onSubmit={handleCreateEvidence} className="space-y-4 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1">Claim Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                >
                  <option value="benchmark">Benchmark Record</option>
                  <option value="code">Code Repository / Implementation</option>
                  <option value="technical_note">Technical Post / Note</option>
                  <option value="oss_pr">OSS PR Contribution</option>
                  <option value="paper_read">Paper Reproduction</option>
                </select>
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Evidence Claim Statement</label>
                <textarea
                  required
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="What was built, measured, or proved?"
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Source / Artifact URL</label>
                <input
                  type="text"
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  placeholder="https://github.com/..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded bg-zinc-800 text-zinc-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-emerald-500 hover:bg-emerald-400 text-zinc-950 text-xs font-bold"
                >
                  Save Claim
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
