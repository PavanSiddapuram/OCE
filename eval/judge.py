#!/usr/bin/env python3
"""
OCE — LLM-as-Judge Evaluation Harness

Runs the OCE agents (3–7) against a seeded company profile
(no Tavily or Firecrawl required) then uses a separate LLM call
to score each output on quality dimensions.

Supported providers — set ONE key in eval/.env or as env var:
  ANTHROPIC_API_KEY=sk-ant-...      → uses Claude claude-sonnet-4-6 as judge, claude-haiku-4-5 as agents
  GOOGLE_API_KEY=AIza...            → uses Gemini 2.0 Flash as both agent and judge

Usage:
  ANTHROPIC_API_KEY=sk-ant-... python eval/judge.py
  GOOGLE_API_KEY=AIza...           python eval/judge.py

Or create eval/.env with either key and just run:
  python eval/judge.py
"""
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# ── load eval/.env ────────────────────────────────────────────────────────────
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

if not ANTHROPIC_API_KEY and not GOOGLE_API_KEY:
    print("ERROR: No API key found.")
    print("Set one of the following in eval/.env or as an env var:")
    print("  ANTHROPIC_API_KEY=sk-ant-...   (uses Claude)")
    print("  GOOGLE_API_KEY=AIza...          (uses Gemini 2.0 Flash — free tier)")
    print()
    print("Get a free Google key at: https://aistudio.google.com/app/apikey")
    sys.exit(1)

# ── provider setup ────────────────────────────────────────────────────────────

PROVIDER: str  # "anthropic" | "google"
AGENT_MODEL: str
JUDGE_MODEL: str

if ANTHROPIC_API_KEY:
    try:
        import anthropic as _anthropic_mod
    except ImportError:
        print("ERROR: Run: pip install anthropic")
        sys.exit(1)
    PROVIDER = "anthropic"
    AGENT_MODEL = "claude-haiku-4-5-20251001"
    JUDGE_MODEL = "claude-sonnet-4-6"
    _ant_client = _anthropic_mod.Anthropic(api_key=ANTHROPIC_API_KEY)

    def run_llm(system: str, user: str, model: str = "") -> str:
        model = model or AGENT_MODEL
        r = _ant_client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return r.content[0].text

else:
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError:
        print("ERROR: Run: pip install google-generativeai")
        sys.exit(1)
    PROVIDER = "google"
    AGENT_MODEL = "gemini-2.0-flash"
    JUDGE_MODEL = "gemini-2.0-flash"
    genai.configure(api_key=GOOGLE_API_KEY)

    def run_llm(system: str, user: str, model: str = "") -> str:
        model = model or AGENT_MODEL
        _model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system,
        )
        response = _model.generate_content(user)
        return response.text


def _parse_json(raw: str) -> dict | list:
    """Strip markdown fences and parse JSON."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


# ── seed company & resume ─────────────────────────────────────────────────────

SEED_COMPANY = {
    "name": "Sarvam AI",
    "website": "https://www.sarvam.ai",
    "mission": "Build AI infrastructure for Indic languages — speech, translation, and LLMs that work for 1.4 billion people.",
    "product_summary": (
        "Sarvam builds speech-to-text, text-to-speech, and LLM APIs optimised for 10 Indic languages. "
        "Their flagship product, Sarvam-1, is a 7B model fine-tuned on Indic datasets. "
        "They also offer a voice AI platform used by banks and healthcare companies for phone automation."
    ),
    "tech_stack": ["Python", "PyTorch", "FastAPI", "React", "Kubernetes", "CUDA", "Triton Inference Server"],
    "recent_launches": [
        "Sarvam-1 7B Indic LLM (open-weights)",
        "Sarvam Translate API for 10 languages",
        "Voice AI platform for IVR automation",
        "Batch transcription API",
    ],
    "current_focus": "Enterprise voice AI contracts and developer API adoption",
    "sector": "AI / ML",
    "city": "Bangalore",
}

RESUME_TEXT = """
Arjun Mehta — Software Engineer
Chennai, India | arjun@example.com | github.com/arjunm

EXPERIENCE
Freshworks (2022–present) — Backend Engineer
  • Built real-time messaging infra serving 50M events/day on Kafka + Redis
  • Led migration of ML inference pipeline from CPU to GPU (3× latency reduction)
  • Wrote automated eval harness for NLP classifiers (F1 tracking across 20 models)

Zoho (2020–2022) — Software Engineer
  • Built Telugu/Hindi speech transcription pipeline (Whisper + custom post-processing)
  • Reduced transcription error rate 40% via language-model rescoring
  • Shipped multilingual customer support bot used by 500K+ users

SKILLS
Python (expert), FastAPI, PyTorch, Triton Inference Server, Redis, Kafka, PostgreSQL,
React, Docker, Kubernetes, CUDA basics, Indic NLP

EDUCATION
NIT Trichy — B.Tech Computer Science (2020)
"""

# ── Agent 3: Opportunity Detection ───────────────────────────────────────────

A3_SYSTEM = """You are an experienced software-focused founder reviewing your own company.
Identify 3-5 specific things a skilled software engineer could build or improve.
Categories: bottleneck | growth_lever | missing_piece | technical_debt

For each opportunity return JSON with:
- title, category, description (2-3 sentences), impact (1-2 sentences), skills_required (list)

Respond ONLY with JSON: {"opportunities": [...]}"""

def run_agent3(company: dict) -> list[dict]:
    prompt = f"""Company: {company['name']}
Mission: {company['mission']}
Product: {company['product_summary']}
Tech Stack: {', '.join(company['tech_stack'])}
Recent Launches: {', '.join(company['recent_launches'])}
Current Focus: {company['current_focus']}
Sector: {company['sector']}

Identify 3-5 specific opportunities. Respond with JSON only."""
    raw = run_llm(A3_SYSTEM, prompt)
    try:
        return _parse_json(raw).get("opportunities", [])  # type: ignore
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()).get("opportunities", []) if m else []


# ── Agent 4: Skill Match ──────────────────────────────────────────────────────

A4_SYSTEM = """You are a calibrated talent evaluator.
Score how well the resume matches each opportunity (0-100):
80-100 strong fit | 60-79 decent | 40-59 stretch | 0-39 poor

For each, return JSON: title, fit_score (int), fit_reasoning (2-3 sentences).
Respond ONLY with JSON: {"matches": [...]}"""

def run_agent4(company: dict, opportunities: list[dict], resume: str) -> list[dict]:
    opp_text = "\n\n".join(
        f"Title: {o['title']}\nCategory: {o['category']}\nDescription: {o['description']}\nSkills: {', '.join(o.get('skills_required', []))}"
        for o in opportunities
    )
    prompt = f"""Engineer Resume:\n{resume}\n\nOpportunities:\n{opp_text}\n\nRespond with JSON only."""
    raw = run_llm(A4_SYSTEM, prompt)
    try:
        return _parse_json(raw).get("matches", [])  # type: ignore
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()).get("matches", []) if m else []


# ── Agent 5: Proof-of-Work ────────────────────────────────────────────────────

A5_SYSTEM = """You are a senior engineer who builds proof-of-work projects to land startup roles.
Design a mini-project: directly solves the problem, buildable in a weekend (8-24 hrs).
Return JSON: name, description (3 bullets), rough_structure, estimated_hours, why_impressive.
Respond ONLY with valid JSON (no markdown)."""

def run_agent5(company: dict, opportunity: dict) -> dict:
    prompt = f"""Company: {company['name']}
Tech Stack: {', '.join(company['tech_stack'])}
Current Focus: {company['current_focus']}

Opportunity: {opportunity['title']}
Description: {opportunity['description']}
Impact: {opportunity['impact']}
Skills: {', '.join(opportunity.get('skills_required', []))}

Design a proof-of-work project. Respond with JSON only."""
    raw = run_llm(A5_SYSTEM, prompt)
    try:
        return _parse_json(raw)  # type: ignore
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()) if m else {}


# ── Agent 6: Founder Research ─────────────────────────────────────────────────

A6_SYSTEM = """You are a researcher building a founder profile for cold outreach.
Create a realistic profile for the CEO/co-founder.
Return JSON: name, role, background (2-3 sentences), complaints (list of 3-5 specific things
they repeatedly worry about), key_insight (single most actionable outreach insight).
Respond ONLY with valid JSON."""

def run_agent6(company: dict) -> dict:
    prompt = f"""Company: {company['name']}
Mission: {company['mission']}
Sector: {company['sector']}, City: {company['city']}

Create a realistic founder profile. Respond with JSON only."""
    raw = run_llm(A6_SYSTEM, prompt)
    try:
        return _parse_json(raw)  # type: ignore
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()) if m else {}


# ── Agent 7: Outreach Narrative ───────────────────────────────────────────────

A7_SYSTEM = """You are an expert at founder-specific cold outreach that gets replies.
Write peer-to-peer, specific messages. NOT generic.

Structure per message: hook, why_company, why_problem, why_me, what_i_built, call_to_action, body.
Channels: linkedin (<250 words), email (<400 words), twitter_dm (<100 words).
Respond ONLY with JSON: {"messages": [...]}"""

def run_agent7(company: dict, top_opp: dict, pow_idea: dict, founder: dict, resume: str) -> list[dict]:
    prompt = f"""Company: {company['name']}
Mission: {company['mission']}
Current Focus: {company['current_focus']}

Opportunity: {top_opp.get('title')} — {top_opp.get('description')}

Proof-of-Work:
{json.dumps(pow_idea, indent=2)}

Founder: {founder.get('name')}
Complaints: {', '.join(founder.get('complaints', []))}
Key Insight: {founder.get('key_insight', '')}

Resume (abbreviated):
{resume[:2000]}

Write outreach for linkedin, email, twitter_dm. Respond with JSON only."""
    raw = run_llm(A7_SYSTEM, prompt)
    try:
        return _parse_json(raw).get("messages", [])  # type: ignore
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group()).get("messages", []) if m else []


# ── Judge ─────────────────────────────────────────────────────────────────────

JUDGE_SYSTEM = """You are an expert evaluator of an AI pipeline that helps engineers create
job opportunities at startups. Score outputs on quality dimensions (1-10):
  10 = exceptional   7-9 = good   5-6 = mediocre   1-4 = poor

For each dimension return: dimension, score (int), reasoning (2-3 sentences), improvement (one specific fix).
Respond ONLY with JSON: {"scores": [...]}"""

@dataclass
class JudgeScore:
    dimension: str
    score: int
    reasoning: str
    improvement: str

def judge_output(agent_name: str, output: object, context: dict, dimensions: list[str]) -> list[JudgeScore]:
    dim_spec = "\n".join(f'- "{d}"' for d in dimensions)
    prompt = f"""Evaluating: {agent_name}

Context:
{json.dumps(context, indent=2)}

Agent Output:
{json.dumps(output, indent=2)}

Score on these dimensions:
{dim_spec}

Respond with JSON only."""
    raw = run_llm(JUDGE_SYSTEM, prompt, model=JUDGE_MODEL)
    try:
        return [JudgeScore(**s) for s in _parse_json(raw).get("scores", [])]  # type: ignore
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            return [JudgeScore(**s) for s in json.loads(m.group()).get("scores", [])]
        return []


# ── Display ───────────────────────────────────────────────────────────────────

BOLD = "\033[1m"; GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
CYAN = "\033[96m"; DIM = "\033[2m"; RESET = "\033[0m"

def color_score(n: int) -> str:
    c = GREEN if n >= 8 else YELLOW if n >= 6 else RED
    return f"{c}{n}/10{RESET}"

def section(title: str):
    print(f"\n{BOLD}{CYAN}{'═'*62}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'═'*62}{RESET}")

def show_scores(scores: list[JudgeScore]):
    for s in scores:
        print(f"\n  {BOLD}{s.dimension}{RESET}: {color_score(s.score)}")
        print(f"  {DIM}{s.reasoning}{RESET}")
        print(f"  {YELLOW}↑ {s.improvement}{RESET}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}OCE — LLM-as-Judge Evaluation{RESET}")
    print(f"Provider : {BOLD}{PROVIDER}{RESET}  |  Agent: {AGENT_MODEL}  |  Judge: {JUDGE_MODEL}")
    print(f"Company  : {SEED_COMPANY['name']} ({SEED_COMPANY['city']}, {SEED_COMPANY['sector']})")
    print("─" * 62)

    all_scores: dict[str, list[JudgeScore]] = {}
    ctx = {"company": SEED_COMPANY["name"], "sector": SEED_COMPANY["sector"]}

    # Agent 3
    section("Agent 3 — Opportunity Detection")
    t = time.time()
    opportunities = run_agent3(SEED_COMPANY)
    print(f"  {len(opportunities)} opportunities found  ({time.time()-t:.1f}s)")
    for o in opportunities:
        print(f"  • [{o.get('category','?')}] {o.get('title','?')}")
    scores = judge_output("Agent 3: Opportunity Detection", opportunities,
        {**ctx, "tech_stack": SEED_COMPANY["tech_stack"], "current_focus": SEED_COMPANY["current_focus"]},
        ["specificity_to_company", "business_impact", "engineer_actionability", "category_accuracy"])
    show_scores(scores); all_scores["agent3"] = scores

    # Agent 4
    section("Agent 4 — Skill Match")
    t = time.time()
    matches = run_agent4(SEED_COMPANY, opportunities, RESUME_TEXT)
    print(f"  {len(matches)} matches scored  ({time.time()-t:.1f}s)")
    for m in matches:
        print(f"  • {str(m.get('title','?'))[:52]}  →  {m.get('fit_score','?')}/100")
    scores = judge_output("Agent 4: Skill Match", matches,
        {**ctx, "resume_summary": "Backend/ML engineer, Indic NLP experience, Freshworks/Zoho"},
        ["score_calibration", "reasoning_quality", "discrimination_power"])
    show_scores(scores); all_scores["agent4"] = scores

    # Top opportunity by fit score
    paired = [(m.get("fit_score", 0), o) for m, o in zip(matches, opportunities) if m.get("fit_score")]
    top_opp = max(paired, default=(0, opportunities[0] if opportunities else {}))[1]

    # Agent 5
    section(f"Agent 5 — Proof-of-Work  [{top_opp.get('title', 'top opp')}]")
    t = time.time()
    pow_idea = run_agent5(SEED_COMPANY, top_opp)
    print(f"  {pow_idea.get('name','?')}  ({pow_idea.get('estimated_hours','?')})  ({time.time()-t:.1f}s)")
    scores = judge_output("Agent 5: Proof-of-Work", pow_idea,
        {**ctx, "opportunity": top_opp.get("title"), "tech_stack": SEED_COMPANY["tech_stack"]},
        ["relevance_to_opportunity", "weekend_buildability", "founder_impressiveness", "technical_specificity"])
    show_scores(scores); all_scores["agent5"] = scores

    # Agent 6
    section("Agent 6 — Founder Research")
    t = time.time()
    founder = run_agent6(SEED_COMPANY)
    print(f"  Founder: {founder.get('name','?')} ({founder.get('role','?')})  ({time.time()-t:.1f}s)")
    for c in founder.get("complaints", []):
        print(f"    – {c}")
    scores = judge_output("Agent 6: Founder Research", founder, ctx,
        ["complaint_specificity", "outreach_utility", "background_plausibility"])
    show_scores(scores); all_scores["agent6"] = scores

    # Agent 7
    section("Agent 7 — Outreach Narrative")
    t = time.time()
    messages = run_agent7(SEED_COMPANY, top_opp, pow_idea, founder, RESUME_TEXT)
    print(f"  {len(messages)} messages generated  ({time.time()-t:.1f}s)")
    for msg in messages:
        body = msg.get("body", "")
        print(f"\n  ── {msg.get('channel','?').upper()} ({len(body.split())} words) ──")
        print("  " + body[:280].replace("\n", "\n  ") + ("…" if len(body) > 280 else ""))
    scores = judge_output("Agent 7: Outreach Narrative", messages,
        {**ctx, "founder_complaint": (founder.get("complaints") or [""])[0], "pow": pow_idea.get("name")},
        ["hook_specificity", "peer_to_peer_tone", "pow_integration", "cta_effectiveness", "channel_fit"])
    show_scores(scores); all_scores["agent7"] = scores

    # Summary
    section("JUDGE SUMMARY DASHBOARD")
    grand_total = grand_count = 0
    for key, scores in all_scores.items():
        if not scores:
            continue
        avg = sum(s.score for s in scores) / len(scores)
        grand_total += sum(s.score for s in scores)
        grand_count += len(scores)
        print(f"\n  {BOLD}{key}{RESET}  avg {color_score(round(avg))}")
        for s in scores:
            bar = "█" * s.score + "░" * (10 - s.score)
            print(f"    {s.dimension:<38} {bar} {color_score(s.score)}")

    if grand_count:
        overall = grand_total / grand_count
        print(f"\n  {BOLD}Overall pipeline quality: {color_score(round(overall))} ({overall:.1f}/10){RESET}")

    out = Path(__file__).parent / "eval_results.json"
    out.write_text(json.dumps(
        {k: [vars(s) for s in v] for k, v in all_scores.items()}, indent=2))
    print(f"\n  Full results → {out}\n")


if __name__ == "__main__":
    main()
