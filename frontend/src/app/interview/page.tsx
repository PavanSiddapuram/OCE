"use client";

import { useEffect, useState } from "react";
import { Cpu, Play, CheckCircle2, AlertTriangle, Send, RefreshCw, Award, Code2 } from "lucide-react";
import { api } from "@/lib/api";

export default function InterviewStudio() {
  const [questions, setQuestions] = useState<any[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null);
  const [session, setSession] = useState<any>(null);
  const [codeResponse, setCodeResponse] = useState("");
  const [selfEvaluation, setSelfEvaluation] = useState("");
  const [debrief, setDebrief] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("pressure_coding");
  const [difficulty, setDifficulty] = useState("frontier");

  useEffect(() => {
    api.listQuestions()
      .then((qs) => {
        setQuestions(qs);
        if (qs.length > 0) setSelectedQuestion(qs[0]);
      })
      .catch((err) => console.error("Failed to load questions:", err));
  }, []);

  const handleStartSession = async () => {
    setLoading(true);
    setDebrief(null);
    try {
      const sess = await api.startInterviewSession({
        mode,
        difficulty,
        target_role: "Google DeepMind Research Engineer",
      });
      setSession(sess);
    } catch (err) {
      console.error("Start session failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDebrief = async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await api.debriefInterviewSession(session.session_id, {
        code_response: codeResponse,
        self_evaluation: selfEvaluation,
      });
      setDebrief(res.scorecard);
    } catch (err) {
      console.error("Debrief failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="text-amber-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Track A: Interview OS</h1>
          </div>
          <p className="text-zinc-400 text-xs mt-1">
            Adaptive AI Mock-Interview Loop & Failure Fingerprint Evaluator
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="bg-zinc-900 text-zinc-200 text-xs rounded-lg px-3 py-2 border border-zinc-700 focus:outline-none focus:border-amber-400"
          >
            <option value="pressure_coding">Pressure Coding (Timed)</option>
            <option value="dsa">Foundational DSA</option>
            <option value="lld">LLD & OOP Reasoning</option>
            <option value="hld">Distributed Systems (HLD)</option>
            <option value="ai_systems">AI/ML Systems & CUDA</option>
          </select>

          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="bg-zinc-900 text-zinc-200 text-xs rounded-lg px-3 py-2 border border-zinc-700 focus:outline-none focus:border-amber-400"
          >
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
            <option value="frontier">Frontier Level</option>
          </select>

          <button
            onClick={handleStartSession}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs flex items-center gap-2 transition-all shadow-md"
          >
            {loading ? <RefreshCw className="animate-spin" size={14} /> : <Play size={14} />}
            Start Mock Session
          </button>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column: Question & Interview Dialogue */}
        <div className="space-y-6">
          
          {/* Question Prompt Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-bold uppercase tracking-wider">
                {selectedQuestion?.difficulty || difficulty} • {selectedQuestion?.mode || mode}
              </span>
              <span className="text-xs text-zinc-500 font-mono">Google DeepMind Rubric</span>
            </div>

            <h2 className="text-lg font-bold text-white mb-2">
              {selectedQuestion?.title || "3D Gaussian Splatting Rasterization Invariant & Ray Intersect"}
            </h2>

            <div className="p-4 rounded-lg bg-zinc-950/80 border border-zinc-800 text-xs text-zinc-300 leading-relaxed font-mono space-y-2">
              <p>{selectedQuestion?.prompt?.problem || "Design and implement a fast ray-sphere bounding test for a 3D point cloud scene under real-time frame budget constraints (16ms). Explain time/space complexity and invariant properties under affine transform."}</p>
              <div className="pt-2 border-t border-zinc-800 text-zinc-400">
                <strong>Constraints:</strong> {selectedQuestion?.prompt?.constraints || "O(N) pass, O(log N) ray traversal. Space overhead <= 1.5x buffer."}
              </div>
            </div>
          </div>

          {/* Active Session Dialogue & Probing */}
          {session && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Send size={15} className="text-amber-400" /> Interviewer Dialogue & Probing
              </h3>

              <div className="p-3.5 rounded-lg bg-amber-500/5 border border-amber-500/20 text-xs text-amber-200">
                <span className="font-semibold text-amber-400">Interviewer Probe:</span> "Before completing your code, explicitly state your loop invariant and spatial bounding assumption. How does your solution handle degenerate collinear points?"
              </div>
            </div>
          )}

          {/* Question Selector List */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-sm font-bold text-white mb-3">Frontier Question Registry</h3>
            <div className="space-y-2">
              {questions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => setSelectedQuestion(q)}
                  className={`w-full text-left p-3 rounded-lg border text-xs transition-all ${
                    selectedQuestion?.id === q.id
                      ? "bg-amber-500/10 border-amber-500/40 text-amber-300"
                      : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="font-bold">{q.title}</div>
                  <div className="text-[10px] text-zinc-500 mt-1 flex justify-between">
                    <span>Mode: {q.mode}</span>
                    <span className="capitalize">{q.difficulty}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Code Response & Debrief Scorecard */}
        <div className="space-y-6">
          
          {/* Code & Reasoning Editor */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Code2 size={18} className="text-amber-400" /> Candidate Reasoning & Implementation
              </h2>
              <span className="text-[11px] text-zinc-500 font-mono">C++ / Python / Rust</span>
            </div>

            <textarea
              value={codeResponse}
              onChange={(e) => setCodeResponse(e.target.value)}
              placeholder="// Write your problem decomposition, invariant reasoning, and solution code here..."
              rows={12}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-4 font-mono text-xs text-zinc-200 focus:outline-none focus:border-amber-400"
            />

            <button
              onClick={handleDebrief}
              disabled={loading || !session}
              className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs flex items-center justify-center gap-2 transition-all shadow"
            >
              {loading ? <RefreshCw className="animate-spin" size={14} /> : <CheckCircle2 size={14} />}
              Submit Solution & Run Debrief Evaluator
            </button>
          </div>

          {/* Debrief Scorecard Output */}
          {debrief && (
            <div className="bg-zinc-900 border border-amber-500/40 rounded-xl p-6 space-y-4 shadow-lg">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div className="flex items-center gap-2">
                  <Award className="text-amber-400" size={20} />
                  <h3 className="text-base font-bold text-white">Session Debrief Scorecard</h3>
                </div>
                <div className="text-xl font-extrabold text-amber-400 font-mono">
                  {debrief.overall_score}/100
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Problem Decomposition</div>
                  <div className="font-bold text-zinc-100 font-mono mt-0.5">{debrief.problem_decomposition}%</div>
                </div>
                <div className="p-3 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Invariant Rigor</div>
                  <div className="font-bold text-zinc-100 font-mono mt-0.5">{debrief.invariant_reasoning}%</div>
                </div>
                <div className="p-3 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Pressure Stability</div>
                  <div className="font-bold text-zinc-100 font-mono mt-0.5">{debrief.pressure_stability}%</div>
                </div>
                <div className="p-3 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Recovery Metric</div>
                  <div className="font-bold text-zinc-100 font-mono mt-0.5">{debrief.recovery_metric}%</div>
                </div>
              </div>

              <div className="p-3.5 rounded bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300">
                <strong>Failure Fingerprint Observation:</strong> {debrief.failure_fingerprint}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
