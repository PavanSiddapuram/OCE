"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import { Contact, CRMBoard } from "@/types";
import { ExternalLink, Search, Users, UserCheck, BookOpen, Sparkles, RefreshCw } from "lucide-react";

const COLUMNS = [
  { id: "not_contacted", label: "Discovered", color: "text-zinc-400" },
  { id: "messaged", label: "Context Ready", color: "text-blue-400" },
  { id: "replied", label: "Contacted", color: "text-amber-400" },
  { id: "meeting", label: "Conversation", color: "text-purple-400" },
  { id: "interview", label: "Technical Rel", color: "text-green-400" },
  { id: "offer", label: "Referral Ready", color: "text-emerald-400" },
];

function ContactCard({ contact, index }: { contact: Contact; index: number }) {
  const daysSince = contact.last_contacted
    ? Math.floor((Date.now() - new Date(contact.last_contacted).getTime()) / 86400000)
    : null;

  return (
    <Draggable draggableId={contact.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`bg-zinc-900 border rounded-xl p-3.5 space-y-2 cursor-grab active:cursor-grabbing transition-all ${
            snapshot.isDragging ? "border-amber-400/50 shadow-lg shadow-amber-400/10" : "border-zinc-800"
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-semibold text-sm text-zinc-100">{contact.name}</p>
              <p className="text-xs text-zinc-400">{contact.role || "Research Engineer"} · {contact.contact_type || "Google DeepMind"}</p>
            </div>
            {contact.linkedin_url && (
              <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-zinc-200">
                <ExternalLink size={13} />
              </a>
            )}
          </div>

          <div className="flex items-center justify-between text-[11px] text-zinc-500 pt-1 border-t border-zinc-800/80">
            {daysSince !== null ? <span>{daysSince}d ago</span> : <span>New Record</span>}
            {contact.next_followup && (
              <span className="text-amber-400 font-medium">
                Follow up {new Date(contact.next_followup).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}
              </span>
            )}
          </div>
        </div>
      )}
    </Draggable>
  );
}

export default function CRMPage() {
  const [activeTab, setActiveTab] = useState<"kanban" | "researchers">("kanban");
  const [searchTopic, setSearchTopic] = useState("3DGS");
  const [searchAffiliation, setSearchAffiliation] = useState("Google DeepMind");
  const [foundResearchers, setFoundResearchers] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  const { data: board, isLoading } = useQuery<CRMBoard>({
    queryKey: ["crm-board"],
    queryFn: api.getCRMBoard,
  });

  const mutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.updateContactStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["crm-board"] }),
  });

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    const { draggableId, destination } = result;
    mutation.mutate({ id: draggableId, status: destination.droppableId });
  };

  const handleSearchResearchers = async () => {
    setSearching(true);
    try {
      const res = await api.findAlphaXivResearchers({
        topic: searchTopic,
        affiliation: searchAffiliation,
      });
      setFoundResearchers(res.researchers || []);
    } catch (err) {
      console.error("Find researchers failed:", err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header with Sub-tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-zinc-800 pb-5 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="text-amber-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">People & Researcher Relationship CRM</h1>
          </div>
          <p className="text-zinc-400 text-xs mt-1">
            Human-in-the-loop Relationship Stages (Discovered → Context Ready → Technical Relationship → Referral)
          </p>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 p-1 rounded-lg flex gap-1">
          <button
            onClick={() => setActiveTab("kanban")}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
              activeTab === "kanban" ? "bg-amber-500 text-zinc-950 shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            Relationship Stage Kanban
          </button>
          <button
            onClick={() => setActiveTab("researchers")}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
              activeTab === "researchers" ? "bg-amber-500 text-zinc-950 shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            alphaXiv Researcher Finder
          </button>
        </div>
      </div>

      {/* Tab 1: Kanban Board */}
      {activeTab === "kanban" && (
        <>
          {isLoading ? (
            <div className="text-zinc-500 text-center py-20">Loading Relationship Board...</div>
          ) : (
            <DragDropContext onDragEnd={onDragEnd}>
              <div className="grid grid-cols-1 md:grid-cols-6 gap-4 overflow-x-auto pb-4">
                {COLUMNS.map((col) => {
                  const contacts = (board as any)?.[col.id] || [];
                  return (
                    <div key={col.id} className="bg-zinc-950/60 border border-zinc-800/80 rounded-xl p-3.5 space-y-3 min-w-[200px]">
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-bold uppercase tracking-wider ${col.color}`}>
                          {col.label}
                        </span>
                        <span className="text-[10px] font-mono text-zinc-500 px-1.5 py-0.5 rounded bg-zinc-900">
                          {contacts.length}
                        </span>
                      </div>

                      <Droppable droppableId={col.id}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.droppableProps}
                            className={`space-y-2.5 min-h-[400px] transition-colors rounded-lg p-1 ${
                              snapshot.isDraggingOver ? "bg-zinc-900/40" : ""
                            }`}
                          >
                            {contacts.map((contact: Contact, index: number) => (
                              <ContactCard key={contact.id} contact={contact} index={index} />
                            ))}
                            {provided.placeholder}
                          </div>
                        )}
                      </Droppable>
                    </div>
                  );
                })}
              </div>
            </DragDropContext>
          )}
        </>
      )}

      {/* Tab 2: alphaXiv Researcher Finder */}
      {activeTab === "researchers" && (
        <div className="space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Search className="text-amber-400" size={18} /> Find Researchers via alphaXiv Authorship Graph
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1">Research Topic</label>
                <input
                  type="text"
                  value={searchTopic}
                  onChange={(e) => setSearchTopic(e.target.value)}
                  placeholder="3DGS, Spatial AI, SIMA 2"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>
              <div>
                <label className="block text-zinc-400 mb-1">Target Affiliation / Org</label>
                <input
                  type="text"
                  value={searchAffiliation}
                  onChange={(e) => setSearchAffiliation(e.target.value)}
                  placeholder="Google DeepMind"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>
            </div>

            <button
              onClick={handleSearchResearchers}
              disabled={searching}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow"
            >
              {searching ? <RefreshCw className="animate-spin" size={14} /> : <Sparkles size={14} />}
              Run find_researchers Tool Call
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {foundResearchers.map((r: any) => (
              <div key={r.slug} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-3 hover:border-amber-500/30 transition-all">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-base font-bold text-white">{r.name}</h3>
                    <p className="text-xs text-amber-400 font-medium mt-0.5">{r.current_position}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 text-[10px] font-mono">
                    {r.citations?.toLocaleString()} citations
                  </span>
                </div>

                {r.topics && (
                  <div className="flex flex-wrap gap-1.5 text-[10px] font-mono">
                    {r.topics.map((t: string) => (
                      <span key={t} className="px-2 py-0.5 rounded bg-zinc-950 text-zinc-300 border border-zinc-800">
                        #{t}
                      </span>
                    ))}
                  </div>
                )}

                {r.recent_papers && (
                  <div className="p-3 rounded bg-zinc-950 border border-zinc-800 text-xs text-zinc-400 space-y-1">
                    <strong className="text-zinc-300 block mb-1">Recent Publications:</strong>
                    <ul className="list-disc list-inside space-y-0.5">
                      {r.recent_papers.map((p: string, idx: number) => (
                        <li key={idx} className="truncate">{p}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="pt-2 flex justify-between items-center border-t border-zinc-800 text-xs">
                  <span className="text-zinc-500">Slug: @{r.slug}</span>
                  <button className="px-3 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded font-semibold text-[11px]">
                    Draft Outreach Brief
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
