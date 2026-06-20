"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import { Contact, CRMBoard } from "@/types";
import { ExternalLink } from "lucide-react";

const COLUMNS = [
  { id: "not_contacted", label: "Not Contacted", color: "text-zinc-400" },
  { id: "messaged", label: "Messaged", color: "text-blue-400" },
  { id: "replied", label: "Replied", color: "text-amber-400" },
  { id: "meeting", label: "Meeting", color: "text-purple-400" },
  { id: "interview", label: "Interview", color: "text-green-400" },
  { id: "offer", label: "Offer", color: "text-emerald-400" },
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
          className={`bg-zinc-900 border rounded-xl p-3 space-y-1.5 cursor-grab active:cursor-grabbing transition-shadow ${
            snapshot.isDragging ? "border-amber-400/50 shadow-lg shadow-amber-400/10" : "border-zinc-800"
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-medium text-sm">{contact.name}</p>
              <p className="text-xs text-zinc-500">{contact.role} · {contact.contact_type}</p>
            </div>
            {contact.linkedin_url && (
              <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-zinc-600 hover:text-zinc-300">
                <ExternalLink size={12} />
              </a>
            )}
          </div>
          <div className="flex items-center justify-between text-xs text-zinc-600">
            {daysSince !== null && <span>{daysSince}d ago</span>}
            {contact.next_followup && (
              <span className="text-amber-400/70">
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

  if (isLoading) return <div className="text-zinc-600 text-center py-20">Loading...</div>;

  const totalContacts = Object.values(board || {}).reduce((sum, col) => sum + col.length, 0);

  return (
    <div className="space-y-4 h-full">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">CRM Board</h1>
        <span className="text-sm text-zinc-500">{totalContacts} contacts</span>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="flex gap-3 overflow-x-auto pb-4" style={{ minHeight: "calc(100vh - 160px)" }}>
          {COLUMNS.map((col) => {
            const contacts = board?.[col.id] || [];
            return (
              <div key={col.id} className="flex-shrink-0 w-56">
                <div className="flex items-center justify-between mb-2 px-1">
                  <span className={`text-xs font-semibold uppercase tracking-wider ${col.color}`}>{col.label}</span>
                  <span className="text-xs text-zinc-600 bg-zinc-800 px-1.5 py-0.5 rounded-full">{contacts.length}</span>
                </div>
                <Droppable droppableId={col.id}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`min-h-48 rounded-xl p-2 space-y-2 transition-colors ${
                        snapshot.isDraggingOver ? "bg-zinc-800/50" : "bg-zinc-900/30"
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
    </div>
  );
}
