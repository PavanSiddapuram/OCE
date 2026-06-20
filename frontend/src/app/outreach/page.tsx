"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Outreach } from "@/types";
import { Copy, Check } from "lucide-react";
import Link from "next/link";

const CHANNELS = ["", "linkedin", "email", "twitter"];
const CHANNEL_COLOR: Record<string, string> = {
  linkedin: "text-blue-400 bg-blue-400/10",
  email: "text-amber-400 bg-amber-400/10",
  twitter: "text-sky-400 bg-sky-400/10",
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-white transition-colors">
      {copied ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

export default function OutreachPage() {
  const [channel, setChannel] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const { data = [], isLoading } = useQuery<Outreach[]>({
    queryKey: ["outreach-all", channel],
    queryFn: () => api.getAllOutreach(channel || undefined),
  });

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Outreach Library</h1>
        <span className="text-sm text-zinc-500">{data.length} messages</span>
      </div>

      <div className="flex gap-2">
        {CHANNELS.map((c) => (
          <button
            key={c}
            onClick={() => setChannel(c)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              channel === c ? "border-amber-400 text-amber-400" : "border-zinc-700 text-zinc-500 hover:border-zinc-500"
            }`}
          >
            {c || "All"}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-zinc-600 text-center py-20">Loading...</div>
      ) : data.length === 0 ? (
        <div className="text-zinc-600 text-center py-20">No outreach yet. Run the pipeline first.</div>
      ) : (
        <div className="space-y-3">
          {data.map((o: Outreach) => (
            <div key={o.id} className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
              <div
                className="p-4 flex items-start justify-between cursor-pointer hover:bg-zinc-800/30"
                onClick={() => setExpanded(expanded === o.id ? null : o.id)}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${CHANNEL_COLOR[o.channel || ""] || "bg-zinc-800 text-zinc-400"}`}>
                      {o.channel?.toUpperCase()}
                    </span>
                    <Link
                      href={`/companies/${o.company_id}`}
                      className="text-xs text-zinc-500 hover:text-white"
                      onClick={(e) => e.stopPropagation()}
                    >
                      → View Company
                    </Link>
                  </div>
                  <p className="text-sm font-medium">{o.hook || o.subject || "Outreach message"}</p>
                </div>
                {o.body && <CopyButton text={o.body} />}
              </div>

              {expanded === o.id && (
                <div className="border-t border-zinc-800 p-4 space-y-3">
                  {[
                    ["Hook", o.hook],
                    ["Why this company", o.why_company],
                    ["Why this problem", o.why_problem],
                    ["Why me", o.why_me],
                    ["What I built", o.what_i_built],
                    ["Call to action", o.call_to_action],
                  ].map(([label, text]) => text && (
                    <div key={label}>
                      <p className="text-xs text-zinc-600 mb-0.5">{label}</p>
                      <div className="flex items-start gap-2">
                        <p className="text-sm text-zinc-300 flex-1">{text}</p>
                        <CopyButton text={text} />
                      </div>
                    </div>
                  ))}
                  {o.body && (
                    <div className="pt-2 border-t border-zinc-800">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs text-zinc-600">Full message</p>
                        <CopyButton text={o.body} />
                      </div>
                      <pre className="text-sm text-zinc-300 whitespace-pre-wrap font-sans bg-zinc-800 rounded-lg p-3">{o.body}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
