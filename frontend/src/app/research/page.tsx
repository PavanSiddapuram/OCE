"use client";

import { useEffect, useState } from "react";
import { Sparkles, Plus, Code, GitCommit, Activity, RefreshCw, Layers, CheckCircle2, Search, BookOpen, ExternalLink, Bot, Check, Play, MessageSquare, BarChart3 } from "lucide-react";
import { api } from "@/lib/api";

export default function ResearchLab() {
  const [activeTab, setActiveTab] = useState<"lab" | "alphaxiv" | "deep-research">("lab");
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Form state for projects
  const [newTitle, setNewTitle] = useState("");
  const [newQuestion, setNewQuestion] = useState("");
  const [newHypothesis, setNewHypothesis] = useState("");
  const [showNewModal, setShowNewModal] = useState(false);

  // Log experiment state
  const [commitSha, setCommitSha] = useState("main-a7f9");
  const [resultSummary, setResultSummary] = useState("");
  const [logLoading, setLogLoading] = useState(false);

  // alphaXiv Corpus Explorer State
  const [searchKeywords, setSearchKeywords] = useState("3DGS, WebGPU, Spatial AI");
  const [searchQuestion, setSearchQuestion] = useState("Fast 3D Gaussian Splatting WebGPU compute rasterizers for SIMA 2 virtual agent environments");
  const [discoveredPapers, setDiscoveredPapers] = useState<any[]>([]);
  const [searchingPapers, setSearchingPapers] = useState(false);
  const [selectedPaperReport, setSelectedPaperReport] = useState<any>(null);
  const [paperRepoData, setPaperRepoData] = useState<any>(null);

  // Gemini Deep Research Agent (Interactions API) State
  const [deepPrompt, setDeepPrompt] = useState("Analyze 3D Gaussian Splatting vs Instant-NGP NeRF for Google DeepMind SIMA 2 virtual agent environments. Include a comparative performance table of FPS, VRAM, and training time.");
  const [deepAgentModel, setDeepAgentModel] = useState("deep-research-preview-04-2026");
  const [collaborativePlanning, setCollaborativePlanning] = useState(false);
  const [useAlphaXivMcp, setUseAlphaXivMcp] = useState(true);
  const [currentInteractionId, setCurrentInteractionId] = useState<string | null>(null);
  const [deepResearchResult, setDeepResearchResult] = useState<any>(null);
  const [startingDeepResearch, setStartingDeepResearch] = useState(false);
  const [refinementText, setRefinementText] = useState("");

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = () => {
    api.listResearchProjects()
      .then((data) => {
        setProjects(data);
        if (data.length > 0) setSelectedProject(data[0]);
      })
      .catch((err) => console.error("Failed to load projects:", err))
      .finally(() => setLoading(false));
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newQuestion) return;
    try {
      await api.createResearchProject({
        title: newTitle,
        question: newQuestion,
        hypothesis: newHypothesis,
      });
      setShowNewModal(false);
      setNewTitle("");
      setNewQuestion("");
      setNewHypothesis("");
      loadProjects();
    } catch (err) {
      console.error("Create project failed:", err);
    }
  };

  const handleLogExperiment = async () => {
    if (!selectedProject) return;
    setLogLoading(true);
    try {
      await api.logExperiment({
        project_id: selectedProject.id,
        commit_sha: commitSha,
        metrics: { fps: 62, psnr: 34.2, vram_mb: 1150 },
        result_summary: resultSummary || "Ablation run confirmed 60+ FPS under WebGPU compute shader sorting.",
      });
      setResultSummary("");
      alert("Experiment run logged & evidence claim created!");
      loadProjects();
    } catch (err) {
      console.error("Log experiment failed:", err);
    } finally {
      setLogLoading(false);
    }
  };

  const handleDiscoverAlphaXiv = async () => {
    setSearchingPapers(true);
    setDiscoveredPapers([]);
    try {
      const kw = searchKeywords.split(",").map((s) => s.trim()).filter(Boolean);
      const res = await api.discoverAlphaXivPapers({
        keywords: kw,
        question: searchQuestion,
        difficulty: 6,
      });
      setDiscoveredPapers(res.papers || []);
    } catch (err) {
      console.error("alphaXiv discovery failed:", err);
    } finally {
      setSearchingPapers(false);
    }
  };

  const handleInspectPaper = async (paperUrl: string, githubUrl?: string) => {
    try {
      const reportRes = await api.getAlphaXivPaperContent({ url: paperUrl });
      setSelectedPaperReport(reportRes);
      if (githubUrl) {
        const repoRes = await api.readAlphaXivRepo({ github_url: githubUrl, path: "/" });
        setPaperRepoData(repoRes);
      } else {
        setPaperRepoData(null);
      }
    } catch (err) {
      console.error("Inspect paper failed:", err);
    }
  };

  const handleStartDeepResearch = async () => {
    setStartingDeepResearch(true);
    setDeepResearchResult(null);
    try {
      const res = await api.startDeepResearch({
        prompt: deepPrompt,
        agent: deepAgentModel,
        collaborative_planning: collaborativePlanning,
        use_alphaxiv_mcp: useAlphaXivMcp,
      });
      setCurrentInteractionId(res.interaction_id);
      if (res.raw) setDeepResearchResult(res.raw);
    } catch (err) {
      console.error("Start deep research failed:", err);
    } finally {
      setStartingDeepResearch(false);
    }
  };

  const handlePollDeepResearch = async () => {
    if (!currentInteractionId) return;
    try {
      const res = await api.getDeepResearchStatus(currentInteractionId);
      setDeepResearchResult(res);
    } catch (err) {
      console.error("Poll deep research failed:", err);
    }
  };

  const handleRefinePlan = async (approve: boolean = false) => {
    if (!currentInteractionId) return;
    setStartingDeepResearch(true);
    try {
      const res = await api.refineDeepResearchPlan(currentInteractionId, {
        prompt: approve ? "Plan looks good! Start research." : refinementText,
        approve_plan: approve,
      });
      if (res.interaction_id) setCurrentInteractionId(res.interaction_id);
      setDeepResearchResult(res);
      setRefinementText("");
    } catch (err) {
      console.error("Refine plan failed:", err);
    } finally {
      setStartingDeepResearch(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh] text-zinc-400">
        <Activity className="animate-spin mr-2" size={20} />
        Loading Track B Research Lab...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header with Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-zinc-800 pb-5 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="text-sky-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Track B: Research & Experiment Lab</h1>
          </div>
          <p className="text-zinc-400 text-xs mt-1">
            Baselines, Ablations, Native alphaXiv MCP & Gemini Deep Research Agent (Interactions API)
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-3">
          <div className="bg-zinc-900 border border-zinc-800 p-1 rounded-lg flex gap-1">
            <button
              onClick={() => setActiveTab("lab")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                activeTab === "lab"
                  ? "bg-sky-500 text-zinc-950 shadow"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Experiments & Baselines
            </button>
            <button
              onClick={() => setActiveTab("alphaxiv")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                activeTab === "alphaxiv"
                  ? "bg-sky-500 text-zinc-950 shadow"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              alphaXiv MCP Explorer
            </button>
            <button
              onClick={() => setActiveTab("deep-research")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                activeTab === "deep-research"
                  ? "bg-gradient-to-r from-amber-500 to-sky-500 text-zinc-950 shadow"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Gemini Deep Research Agent
            </button>
          </div>

          <button
            onClick={() => setShowNewModal(true)}
            className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white font-semibold text-xs flex items-center gap-1.5 transition-all"
          >
            <Plus size={14} /> New Project
          </button>
        </div>
      </div>

      {/* Tab 1: Experiments & Baselines */}
      {activeTab === "lab" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-zinc-400">
              Active Research Projects ({projects.length})
            </h2>

            <div className="space-y-3">
              {projects.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProject(p)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    selectedProject?.id === p.id
                      ? "bg-sky-500/10 border-sky-500/40 text-sky-300 shadow-sm"
                      : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-400 text-[10px] font-bold uppercase tracking-wider">
                      {p.stage}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {p.created_at ? new Date(p.created_at).toLocaleDateString() : ""}
                    </span>
                  </div>
                  <h3 className="font-bold text-sm text-zinc-100">{p.title}</h3>
                  <p className="text-xs text-zinc-400 mt-1 line-clamp-2">{p.question}</p>
                </button>
              ))}
            </div>
          </div>

          {selectedProject && (
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="px-2.5 py-1 rounded bg-sky-500/10 text-sky-400 border border-sky-500/30 text-[11px] font-bold uppercase tracking-wider">
                      Stage: {selectedProject.stage}
                    </span>
                    <h2 className="text-xl font-bold text-white mt-2">{selectedProject.title}</h2>
                  </div>
                  {selectedProject.repo_url && (
                    <a
                      href={selectedProject.repo_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-sky-400 hover:underline flex items-center gap-1 font-mono"
                    >
                      <Code size={13} /> Repository
                    </a>
                  )}
                </div>

                <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-300 space-y-2">
                  <div>
                    <strong className="text-sky-400">Research Question:</strong> {selectedProject.question}
                  </div>
                  <div>
                    <strong className="text-sky-400">Hypothesis:</strong> {selectedProject.hypothesis}
                  </div>
                  <div className="pt-2 border-t border-zinc-800 text-zinc-400">
                    <strong>Next Action:</strong> {selectedProject.next_action}
                  </div>
                </div>
              </div>

              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <GitCommit className="text-sky-400" size={18} /> Record Baseline / Ablation Experiment Run
                </h3>

                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <label className="block text-zinc-400 mb-1">Commit SHA</label>
                    <input
                      type="text"
                      value={commitSha}
                      onChange={(e) => setCommitSha(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-zinc-400 mb-1">Target Metrics (JSON)</label>
                    <input
                      type="text"
                      disabled
                      value='{"fps": 62, "psnr": 34.2, "vram_mb": 1150}'
                      className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-400 font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-zinc-400 mb-1">Result Summary & Observations</label>
                  <textarea
                    value={resultSummary}
                    onChange={(e) => setResultSummary(e.target.value)}
                    placeholder="Record ablation results, hardware configuration, and baseline comparison..."
                    rows={3}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded p-3 text-xs text-zinc-200 focus:outline-none focus:border-sky-400"
                  />
                </div>

                <button
                  onClick={handleLogExperiment}
                  disabled={logLoading}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-zinc-950 font-bold text-xs flex items-center gap-2 transition-all"
                >
                  {logLoading ? <RefreshCw className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
                  Log Experiment & Write Evidence Claim
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: alphaXiv MCP Corpus Explorer */}
      {activeTab === "alphaxiv" && (
        <div className="space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Search className="text-sky-400" size={18} /> alphaXiv Agentic Corpus Discovery (MCP v1.0.0)
              </h2>
              <span className="text-xs text-zinc-500 font-mono">Endpoint: api.alphaxiv.org/mcp/v1</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1">Keywords</label>
                <input
                  type="text"
                  value={searchKeywords}
                  onChange={(e) => setSearchKeywords(e.target.value)}
                  placeholder="3DGS, WebGPU, Spatial AI"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200 font-mono"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-zinc-400 mb-1">Semantic Question Description</label>
                <input
                  type="text"
                  value={searchQuestion}
                  onChange={(e) => setSearchQuestion(e.target.value)}
                  placeholder="Describe target research concepts..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>
            </div>

            <button
              onClick={handleDiscoverAlphaXiv}
              disabled={searchingPapers}
              className="px-4 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-zinc-950 font-bold text-xs flex items-center gap-2 transition-all shadow"
            >
              {searchingPapers ? <RefreshCw className="animate-spin" size={14} /> : <BookOpen size={14} />}
              Run discover_papers Tool Call
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {discoveredPapers.map((paper) => (
              <div key={paper.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-3 hover:border-sky-500/40 transition-all shadow-sm">
                <div className="flex justify-between items-start">
                  <span className="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/30 text-[10px] font-bold font-mono">
                    arXiv:{paper.id}
                  </span>
                  <span className="text-[11px] text-zinc-500">{paper.published_at}</span>
                </div>

                <h3 className="text-base font-bold text-white">{paper.title}</h3>
                <div className="text-xs text-zinc-400">
                  <strong>Organizations:</strong> {paper.organizations?.join(", ") || "Google DeepMind"}
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed">{paper.abstract}</p>

                <div className="flex items-center gap-3 pt-2 border-t border-zinc-800 text-xs">
                  <button
                    onClick={() => handleInspectPaper(paper.arxiv_url || paper.id, paper.github_url)}
                    className="text-sky-400 hover:underline flex items-center gap-1 font-bold"
                  >
                    <BookOpen size={13} /> Inspect Content & GitHub Repo
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Gemini Deep Research Agent (Interactions API) */}
      {activeTab === "deep-research" && (
        <div className="space-y-6">
          <div className="bg-zinc-900 border border-amber-500/30 rounded-xl p-6 space-y-5 shadow-lg">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2">
                <Bot className="text-amber-400" size={22} />
                <h2 className="text-base font-bold text-white">Gemini Deep Research Agent (Google Interactions API)</h2>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40 text-[10px] font-bold font-mono">
                API Revision: 2026-05-20
              </span>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1">Deep Research Topic Prompt</label>
                <textarea
                  value={deepPrompt}
                  onChange={(e) => setDeepPrompt(e.target.value)}
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-3 text-zinc-200 focus:outline-none focus:border-amber-400"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-zinc-400 mb-1">Agent Version</label>
                  <select
                    value={deepAgentModel}
                    onChange={(e) => setDeepAgentModel(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200 font-mono"
                  >
                    <option value="deep-research-preview-04-2026">Deep Research (Speed & Stream)</option>
                    <option value="deep-research-max-preview-04-2026">Deep Research Max (Max Synthesis)</option>
                  </select>
                </div>

                <div className="flex items-center gap-2 pt-5">
                  <input
                    type="checkbox"
                    id="collabPlan"
                    checked={collaborativePlanning}
                    onChange={(e) => setCollaborativePlanning(e.target.checked)}
                    className="rounded bg-zinc-950 border-zinc-800 text-amber-500 focus:ring-0"
                  />
                  <label htmlFor="collabPlan" className="text-zinc-300 font-semibold cursor-pointer">
                    Collaborative Planning Mode
                  </label>
                </div>

                <div className="flex items-center gap-2 pt-5">
                  <input
                    type="checkbox"
                    id="mcpBind"
                    checked={useAlphaXivMcp}
                    onChange={(e) => setUseAlphaXivMcp(e.target.checked)}
                    className="rounded bg-zinc-950 border-zinc-800 text-amber-500 focus:ring-0"
                  />
                  <label htmlFor="mcpBind" className="text-zinc-300 font-semibold cursor-pointer">
                    Bind alphaXiv MCP Server Tool
                  </label>
                </div>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={handleStartDeepResearch}
                  disabled={startingDeepResearch}
                  className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-sky-500 hover:from-amber-400 hover:to-sky-400 text-zinc-950 font-bold text-xs flex items-center gap-2 transition-all shadow-md"
                >
                  {startingDeepResearch ? <RefreshCw className="animate-spin" size={15} /> : <Play size={15} />}
                  Start Async Deep Research Task (background=True)
                </button>

                {currentInteractionId && (
                  <button
                    onClick={handlePollDeepResearch}
                    className="px-4 py-2.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white font-semibold text-xs flex items-center gap-1.5 transition-all"
                  >
                    <RefreshCw size={14} /> Poll Status
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Research Results & Steps */}
          {deepResearchResult && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div className="flex items-center gap-2">
                  <BarChart3 className="text-sky-400" size={18} />
                  <h3 className="text-base font-bold text-white">Interaction Results & Output Steps</h3>
                </div>
                <span className="text-xs font-mono text-amber-400 font-bold uppercase">
                  Status: {deepResearchResult.status || "completed"}
                </span>
              </div>

              {/* Collaborative Planning Control */}
              {collaborativePlanning && deepResearchResult.status !== "completed" && (
                <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 space-y-3 text-xs">
                  <strong className="text-amber-300 block">Proposed Plan Received — Refine or Approve:</strong>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={refinementText}
                      onChange={(e) => setRefinementText(e.target.value)}
                      placeholder="e.g. Focus more on WebGPU compute shaders and less on history..."
                      className="flex-1 bg-zinc-950 border border-zinc-800 rounded p-2 text-zinc-200"
                    />
                    <button
                      onClick={() => handleRefinePlan(false)}
                      className="px-3 py-1.5 rounded bg-zinc-800 text-white font-semibold"
                    >
                      Refine Plan
                    </button>
                    <button
                      onClick={() => handleRefinePlan(true)}
                      className="px-4 py-1.5 rounded bg-amber-500 text-zinc-950 font-bold"
                    >
                      Approve & Execute
                    </button>
                  </div>
                </div>
              )}

              {/* Output Steps Display */}
              <div className="space-y-4">
                {deepResearchResult.steps?.map((step: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-2">
                    <div className="text-[10px] text-zinc-500 font-mono uppercase">Step #{idx + 1} — {step.type}</div>
                    {step.content?.map((c: any, cIdx: number) => (
                      <div key={cIdx}>
                        {c.type === "text" && (
                          <div className="text-xs text-zinc-200 font-mono leading-relaxed whitespace-pre-wrap">
                            {c.text}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* New Project Modal */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-lg w-full space-y-4">
            <h2 className="text-lg font-bold text-white">Create New Research Project</h2>
            <form onSubmit={handleCreateProject} className="space-y-4 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1">Project Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. PyTorch Custom C++ CUDA Point Cloud Operator"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Core Research Question</label>
                <textarea
                  required
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder="What technical question are you testing?"
                  rows={2}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Hypothesis</label>
                <textarea
                  value={newHypothesis}
                  onChange={(e) => setNewHypothesis(e.target.value)}
                  placeholder="What is your expected baseline outcome?"
                  rows={2}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded p-2.5 text-zinc-200"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 rounded bg-zinc-800 text-zinc-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-sky-500 hover:bg-sky-400 text-zinc-950 text-xs font-bold"
                >
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
