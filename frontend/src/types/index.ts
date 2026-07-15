export interface Company {
  id: string;
  name: string;
  website: string | null;
  description: string | null;
  mission: string | null;
  product_summary: string | null;
  recent_launches: string[] | null;
  tech_stack: string[] | null;
  current_focus: string | null;
  sector: string | null;
  city: string | null;
  stage: string | null;
  source: string | null;
  source_url: string | null;
  linkedin_url: string | null;
  twitter_url: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyDetail extends Company {
  opportunities: Opportunity[];
  founders: Founder[];
  outreach: Outreach[];
  contacts: Contact[];
}

export interface PressureTestFlaw {
  label: string;
  severity: "fatal" | "moderate" | "minor";
  why_it_matters: string;
  what_overcomes: string;
}

export interface PressureTest {
  core_assumption: string;
  weekend_worth_score: number;
  flaws: PressureTestFlaw[];
  founder_shrug_risk: string;
  cuts_for_weekend: string[];
  verdict: "BUILD" | "RESHAPE" | "SKIP";
  verdict_reasoning: string;
}

export interface Opportunity {
  id: string;
  company_id: string;
  title: string;
  category: string | null;
  description: string | null;
  impact: string | null;
  fit_score: number | null;
  fit_reasoning: string | null;
  pow_idea: string | null;
  pow_repo_url: string | null;
  skills_required: string[] | null;
  pressure_test: PressureTest | null;
  created_at: string;
}

export interface Founder {
  id: string;
  company_id: string;
  name: string;
  role: string | null;
  linkedin_url: string | null;
  twitter_url: string | null;
  personal_blog: string | null;
  background: string | null;
  complaints: string[] | null;
  podcast_links: string[] | null;
  interview_links: string[] | null;
  created_at: string;
}

export interface Contact {
  id: string;
  company_id: string;
  founder_id: string | null;
  name: string;
  email: string | null;
  linkedin_url: string | null;
  role: string | null;
  contact_type: string | null;
  status: string;
  notes: string | null;
  last_contacted: string | null;
  next_followup: string | null;
  created_at: string;
  updated_at: string;
}

export interface Outreach {
  id: string;
  company_id: string;
  opportunity_id: string | null;
  contact_id: string | null;
  channel: string | null;
  subject: string | null;
  body: string | null;
  hook: string | null;
  why_company: string | null;
  why_problem: string | null;
  why_me: string | null;
  what_i_built: string | null;
  call_to_action: string | null;
  version: number;
  created_at: string;
}

export interface PipelineStatus {
  id: string;
  status: string;
  current_agent: string | null;
  agents_done: string[] | null;
  total_companies: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export type CRMBoard = Record<string, Contact[]>;
