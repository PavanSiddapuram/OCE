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
  // Pipeline
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

  // Opportunities
  getOpportunities: (params?: Record<string, string | number>) => {
    const q = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return request<{ items: import("@/types").Opportunity[]; total: number; page: number }>(`/opportunities${q}`);
  },

  pressureTestOpportunity: (id: string) =>
    request<import("@/types").Opportunity>(`/opportunities/${id}/pressure-test`, { method: "POST" }),

  // Outreach
  getOutreach: (companyId: string) =>
    request<import("@/types").Outreach[]>(`/outreach/${companyId}`),

  getAllOutreach: (channel?: string) => {
    const q = channel ? `?channel=${channel}` : "";
    return request<import("@/types").Outreach[]>(`/outreach${q}`);
  },

  // CRM
  getCRMBoard: () => request<import("@/types").CRMBoard>("/crm/board"),

  createContact: (body: {
    company_id: string;
    name: string;
    role?: string;
    contact_type?: string;
    linkedin_url?: string;
    email?: string;
    notes?: string;
  }) => request<import("@/types").Contact>("/contacts", { method: "POST", body: JSON.stringify(body) }),

  updateContactStatus: (id: string, status: string) =>
    request<import("@/types").Contact>(`/contacts/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
};
