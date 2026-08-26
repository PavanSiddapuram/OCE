const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || res.statusText);
  }
  return res.json();
}

export const api = {
  // FRONTIER OS Core APIs
  getCandidateState: () => request<any>("/me/state"),
  getWeeklyPlan: () => request<any>("/weekly/plan"),
  generateWeeklyPlan: (weekStart?: string) =>
    request<any>("/weekly/plan", {
      method: "POST",
      body: JSON.stringify({ week_start: weekStart || "" }),
    }),

  // Track A: Interview OS
  listQuestions: () => request<any[]>("/interviews/questions"),
  startInterviewSession: (body: { mode: string; difficulty: string; target_role: string }) =>
    request<any>("/interviews/sessions", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getInterviewSession: (sessionId: string) => request<any>(`/interviews/sessions/${sessionId}`),
  debriefInterviewSession: (sessionId: string, body: { code_response: string; self_evaluation?: string }) =>
    request<any>(`/interviews/sessions/${sessionId}/debrief`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Track B: Research Lab & Experiments
  listResearchProjects: () => request<any[]>("/research/projects"),
  createResearchProject: (body: { title: string; question: string; hypothesis: string; repo_url?: string; tags?: string[] }) =>
    request<any>("/research/projects", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  logExperiment: (body: { project_id: string; commit_sha?: string; dataset?: string; config?: any; metrics?: any; result_summary?: string }) =>
    request<any>("/research/experiments", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Gemini Deep Research Agent (Interactions API)
  startDeepResearch: (body: { prompt: string; agent?: string; collaborative_planning?: boolean; visualization?: string; use_alphaxiv_mcp?: boolean }) =>
    request<any>("/research/deep-research/start", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getDeepResearchStatus: (interactionId: string) =>
    request<any>(`/research/deep-research/${interactionId}`),
  refineDeepResearchPlan: (interactionId: string, body: { prompt: string; approve_plan?: boolean }) =>
    request<any>(`/research/deep-research/${interactionId}/refine`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // alphaXiv MCP Tools Integrations
  discoverAlphaXivPapers: (body: { keywords: string[]; question: string; difficulty?: number }) =>
    request<any>("/alphaxiv/discover", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getAlphaXivPaperContent: (body: { url: string; full_text?: boolean; queries?: string[] }) =>
    request<any>("/alphaxiv/paper", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  readAlphaXivRepo: (body: { github_url: string; path?: string }) =>
    request<any>("/alphaxiv/repo", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  findAlphaXivResearchers: (body: { query?: string; topic?: string; affiliation?: string; role?: string }) =>
    request<any>("/alphaxiv/researchers", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getAlphaXivLibrary: () => request<any>("/alphaxiv/library"),
  saveAlphaXivPaper: (body: { paper_ids_or_urls: string[]; folder_id?: string }) =>
    request<any>("/alphaxiv/library/save", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Evidence & Proof
  listEvidence: () => request<any[]>("/evidence"),
  createEvidence: (body: { type: string; claim: string; source_url?: string; source_type?: string; confidence?: number; supports?: string[]; artifact_url?: string; provenance_notes?: string }) =>
    request<any>("/evidence", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Opportunities & 7-Signal Matching
  getOpportunities: (params?: Record<string, string | number>) => {
    const q = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return request<{ items: any[]; total: number; page: number }>(`/opportunities${q}`);
  },
  createOpportunity: (body: { title: string; target_type?: string; target_name?: string; category?: string; description: string; skills_required?: string[] }) =>
    request<any>("/opportunities", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  reviewOpportunity: (id: string, action: "approve" | "snooze" | "archive") =>
    request<any>(`/opportunities/${id}/review?action=${action}`, { method: "POST" }),
  pressureTestOpportunity: (id: string) =>
    request<import("@/types").Opportunity>(`/opportunities/${id}/pressure-test`, { method: "POST" }),

  // Outreach
  getOutreach: (companyId: string) =>
    request<import("@/types").Outreach[]>(`/outreach/${companyId}`),
  getAllOutreach: (channel?: string) => {
    const q = channel ? `?channel=${channel}` : "";
    return request<import("@/types").Outreach[]>(`/outreach${q}`);
  },

  // Pipeline (Startup track)
  runPipeline: (body: { city: string; sector: string; max_companies: number; resume_text: string }) =>
    request<{ pipeline_run_id: string; status: string }>("/pipeline/run", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getPipelineStatus: (runId: string) =>
    request<import("@/types").PipelineStatus>(`/pipeline/${runId}/status`),

  // Companies
  getCompanies: (params?: Record<string, string | number>) => {
    const q = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return request<{ items: import("@/types").Company[]; total: number; page: number }>(`/companies${q}`);
  },

  getCompany: (id: string) => request<import("@/types").CompanyDetail>(`/companies/${id}`),

  // CRM
  getCRMBoard: () => request<import("@/types").CRMBoard>("/crm/board"),
  updateContactStage: (contactId: string, stage: string) =>
    request<any>(`/crm/contacts/${contactId}/stage`, {
      method: "PATCH",
      body: JSON.stringify({ stage }),
    }),
  updateContactStatus: (contactId: string, status: string) =>
    request<any>(`/crm/contacts/${contactId}/stage`, {
      method: "PATCH",
      body: JSON.stringify({ stage: status }),
    }),
};
