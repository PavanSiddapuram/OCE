#!/usr/bin/env python3
"""
OCE — LLM-as-Judge Evaluation Harness

Runs OCE agents 3-7 against a seeded company profile (no Tavily/Firecrawl
needed) then scores each output using a second LLM judge call.

Supported providers — set ONE key in eval/.env or as env var:
  ANTHROPIC_API_KEY=sk-ant-...   Claude haiku-4-5 (agents) + sonnet-4-6 (judge)
  GOOGLE_API_KEY=AIza...         Gemini 2.0 Flash — free tier
  DEEPSEEK_API_KEY=sk-...        DeepSeek-V3 — cheapest (~$0.001 per full run)

Provider pricing (per 1M tokens):
  DeepSeek V3    $0.27 input  /  $1.10 output   ← best value
  Gemini 2.0 Flash  free tier (rate-limited)
  Claude haiku-4-5  $0.80 input  /  $4.00 output
  Claude sonnet-4-6 $3.00 input  / $15.00 output

Usage:
  DEEPSEEK_API_KEY=sk-... python eval/judge.py
  GOOGLE_API_KEY=AIza...  python eval/judge.py

Or create eval/.env with one key and just run:
  python eval/judge.py
"""
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
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
GOOGLE_API_KEY    = os.environ.get("GOOGLE_API_KEY", "")
DEEPSEEK_API_KEY  = os.environ.get("DEEPSEEK_API_KEY", "")

if not any([ANTHROPIC_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY]):
    print("ERROR: No API key found. Set one in eval/.env or as an env var:\n")
    print("  DEEPSEEK_API_KEY=sk-...      (cheapest — ~$0.001 per full run)")
    print("  GOOGLE_API_KEY=AIza...       (free tier — aistudio.google.com/app/apikey)")
    print("  ANTHROPIC_API_KEY=sk-ant-... (Claude)")
    sys.exit(1)

# ── token cost tracker ────────────────────────────────────────────────────────

# Prices in USD per 1M tokens
_PRICING: dict[str, dict[str, float]] = {
    # DeepSeek
    "deepseek-chat":             {"input": 0.27,  "output": 1.10},
    "deepseek-reasoner":         {"input": 0.55,  "output": 2.19},
    # Gemini
    "gemini-2.0-flash":          {"input": 0.0,   "output": 0.0},   # free tier
    "gemini-2.5-flash":          {"input": 0.0,   "output": 0.0},
    # Claude
    "claude-haiku-4-5-20251001": {"input": 0.80,  "output": 4.00},
    "claude-sonnet-4-6":         {"input": 3.00,  "output": 15.00},
}

@dataclass
class CostTracker:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    _model: str = ""

    def record(self, model: str, inp: int, out: int):
        self.calls += 1
        self.input_tokens += inp
        self.output_tokens += out
        price = _PRICING.get(model, {"input": 0.0, "output": 0.0})
        self.cost_usd += (inp * price["input"] + out * price["output"]) / 1_000_000

    def summary(self) -> str:
        return (
            f"calls={self.calls}  "
            f"tokens={self.input_tokens:,}in/{self.output_tokens:,}out  "
            f"cost=${self.cost_usd:.5f}"
        )

_tracker = CostTracker()

# ── provider setup ────────────────────────────────────────────────────────────

PROVIDER: str
AGENT_MODEL: str
JUDGE_MODEL: str

if DEEPSEEK_API_KEY:
    try:
        from openai import OpenAI as _OAI
    except ImportError:
        print("ERROR: Run: pip install openai")
        sys.exit(1)
    PROVIDER    = "deepseek"
    AGENT_MODEL = "deepseek-chat"   # DeepSeek-V3
    JUDGE_MODEL = "deepseek-chat"
    _ds_client  = _OAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    def run_llm(system: str, user: str, model: str = "") -> str:
        model = model or AGENT_MODEL
        r = _ds_client.chat.completions.create(
            model=model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        usage = r.usage
        if usage:
            _tracker.record(model, usage.prompt_tokens, usage.completion_tokens)
        return r.choices[0].message.content or ""

elif ANTHROPIC_API_KEY:
    try:
        import anthropic as _ant
    except ImportError:
        print("ERROR: Run: pip install anthropic")
        sys.exit(1)
    PROVIDER    = "anthropic"
    AGENT_MODEL = "claude-haiku-4-5-20251001"
    JUDGE_MODEL = "claude-sonnet-4-6"
    _ant_client = _ant.Anthropic(api_key=ANTHROPIC_API_KEY)

    def run_llm(system: str, user: str, model: str = "") -> str:
        model = model or AGENT_MODEL
        r = _ant_client.messages.create(
            model=model, max_tokens=2048, system=system,
            messages=[{"role": "user", "content": user}],
        )
        _tracker.record(model, r.usage.input_tokens, r.usage.output_tokens)
        return r.content[0].text

else:  # Google
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError:
        print("ERROR: Run: pip install google-generativeai")
        sys.exit(1)
    PROVIDER    = "google"
    AGENT_MODEL = "gemini-2.0-flash"
    JUDGE_MODEL = "gemini-2.0-flash"
    genai.configure(api_key=GOOGLE_API_KEY)

    def run_llm(system: str, user: str, model: str = "") -> str:
        model = model or AGENT_MODEL
        _m = genai.GenerativeModel(model_name=model, system_instruction=system)
        r  = _m.generate_content(user)
        # Gemini token counts available on usage_metadata
        meta = getattr(r, "usage_metadata", None)
        if meta:
            _tracker.record(model,
                            getattr(meta, "prompt_token_count", 0),
                            getattr(meta, "candidates_token_count", 0))
        return r.text


def _parse_json(raw: str) -> dict | list:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def _safe_json(raw: str, key: str) -> list | dict:
    try:
        parsed = _parse_json(raw)
        return parsed.get(key, parsed) if isinstance(parsed, dict) else parsed
    except Exception:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            parsed = json.loads(m.group())
            return parsed.get(key, parsed) if isinstance(parsed, dict) else parsed
        return [] if key else {}


# ── seed data ─────────────────────────────────────────────────────────────────

SEED_COMPANY = {
    "name": "Sarvam AI",
    "website": "https://www.sarvam.ai",
    "mission": "Build AI infrastructure for Indic languages — speech, translation, and LLMs for 1.4 billion people.",
    "product_summary": (
        "Sarvam builds speech-to-text, text-to-speech, and LLM APIs optimised for 10 Indic languages. "
        "Sarvam-1 is a 7B model fine-tuned on Indic datasets. They offer a voice AI platform used by "
        "banks and healthcare companies for phone automation."
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
Arjun Mehta — Software Engineer | Chennai, India

EXPERIENCE
Freshworks (2022–present) — Backend Engineer
  • Real-time messaging infra: 50M events/day on Kafka + Redis
  • ML inference migration CPU→GPU: 3× latency reduction
  • Automated eval harness for NLP classifiers (F1 tracking, 20 models)

Zoho (2020–2022) — Software Engineer
  • Telugu/Hindi speech transcription (Whisper + LM rescoring, −40% WER)
  • Multilingual customer support bot used by 500K+ users

SKILLS: Python, FastAPI, PyTorch, Triton Inference Server, Redis, Kafka,
        PostgreSQL, Docker, Kubernetes, CUDA basics, Indic NLP

EDUCATION: NIT Trichy — B.Tech Computer Science (2020)
"""

# ── agents ────────────────────────────────────────────────────────────────────

def run_agent3(company: dict) -> list[dict]:
    system = """You are an experienced startup founder reviewing your own company.
Identify 3-5 things a software engineer could build or improve (bottleneck | growth_lever | missing_piece | technical_debt).
Each: title, category, description (2-3 sentences), impact (1-2 sentences), skills_required (list).
Respond ONLY with JSON: {"opportunities": [...]}"""
    prompt = f"""Company: {company['name']}
Mission: {company['mission']}
Product: {company['product_summary']}
Tech Stack: {', '.join(company['tech_stack'])}
Recent Launches: {', '.join(company['recent_launches'])}
Current Focus: {company['current_focus']}"""
    return _safe_json(run_llm(system, prompt), "opportunities")  # type: ignore


def run_agent4(company: dict, opportunities: list[dict], resume: str) -> list[dict]:
    system = """You are a calibrated talent evaluator.
Score each opportunity against the resume (0-100). 80+ strong, 60-79 decent, 40-59 stretch, <40 poor.
Each: title, fit_score (int), fit_reasoning (2-3 sentences).
Respond ONLY with JSON: {"matches": [...]}"""
    opp_text = "\n\n".join(
        f"Title: {o['title']}\nCategory: {o.get('category')}\nDescription: {o.get('description')}\nSkills: {', '.join(o.get('skills_required', []))}"
        for o in opportunities
    )
    prompt = f"Resume:\n{resume}\n\nOpportunities:\n{opp_text}"
    return _safe_json(run_llm(system, prompt), "matches")  # type: ignore


def run_agent5(company: dict, opportunity: dict) -> dict:
    system = """You are a senior engineer designing a proof-of-work project to land a startup role.
Weekend-buildable (8-24 hrs), directly solves the problem, impresses the founder.
Return JSON: name, description (3 bullet strings), rough_structure, estimated_hours, why_impressive.
Respond ONLY with valid JSON (no markdown fences)."""
    prompt = f"""Company: {company['name']} | Stack: {', '.join(company['tech_stack'])}
Opportunity: {opportunity.get('title')}
Description: {opportunity.get('description')}
Impact: {opportunity.get('impact')}
Skills: {', '.join(opportunity.get('skills_required', []))}"""
    return _safe_json(run_llm(system, prompt), "")  # type: ignore


def run_agent6(company: dict) -> dict:
    system = """You are a researcher building a founder profile for cold outreach.
Return JSON: name, role, background (2-3 sentences), complaints (3-5 very specific things
they repeatedly worry about or mention publicly), key_insight (single best outreach hook).
Respond ONLY with valid JSON."""
    prompt = f"Company: {company['name']}\nMission: {company['mission']}\nSector: {company['sector']}, {company['city']}"
    return _safe_json(run_llm(system, prompt), "")  # type: ignore


def run_agent7(company: dict, top_opp: dict, pow_idea: dict, founder: dict, resume: str) -> list[dict]:
    system = """You write founder-specific cold outreach that gets replies. Peer-to-peer, specific, never generic.
Per message: channel, hook (reference founder's real complaint), why_company, why_problem,
why_me, what_i_built (reference PoW), call_to_action, body.
Channels: linkedin (<250 words), email (<400 words), twitter_dm (<100 words).
Respond ONLY with JSON: {"messages": [...]}"""
    prompt = f"""Company: {company['name']} | Focus: {company['current_focus']}
Opportunity: {top_opp.get('title')} — {top_opp.get('description')}
PoW: {json.dumps(pow_idea)}
Founder: {founder.get('name')} | Complaints: {', '.join(founder.get('complaints', []))}
Key insight: {founder.get('key_insight', '')}
Resume: {resume[:1800]}"""
    return _safe_json(run_llm(system, prompt), "messages")  # type: ignore


# ── judge ─────────────────────────────────────────────────────────────────────

JUDGE_SYS = """You are an expert evaluator of an AI pipeline that helps engineers get startup jobs.
Score outputs 1-10 (10=exceptional, 7-9=good, 5-6=mediocre, 1-4=poor).
For each dimension: dimension (str), score (int), reasoning (2-3 sentences), improvement (one fix).
Respond ONLY with JSON: {"scores": [...]}"""

@dataclass
class JudgeScore:
    dimension: str
    score: int
    reasoning: str
    improvement: str

def judge(agent_name: str, output: object, context: dict, dimensions: list[str]) -> list[JudgeScore]:
    dims = "\n".join(f'- "{d}"' for d in dimensions)
    prompt = f"Evaluating: {agent_name}\nContext:\n{json.dumps(context, indent=2)}\nOutput:\n{json.dumps(output, indent=2)}\nScore:\n{dims}"
    raw = run_llm(JUDGE_SYS, prompt, model=JUDGE_MODEL)
    scores = _safe_json(raw, "scores")
    try:
        return [JudgeScore(**s) for s in scores]  # type: ignore
    except Exception:
        return []


# ── display ───────────────────────────────────────────────────────────────────

B = "\033[1m"; G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"
C = "\033[96m"; D = "\033[2m"; RST = "\033[0m"

def cs(n: int) -> str:
    col = G if n >= 8 else Y if n >= 6 else R
    return f"{col}{n}/10{RST}"

def sec(title: str):
    print(f"\n{B}{C}{'═'*62}{RST}\n{B}{C}  {title}{RST}\n{B}{C}{'═'*62}{RST}")

def show(scores: list[JudgeScore]):
    for s in scores:
        print(f"\n  {B}{s.dimension}{RST}: {cs(s.score)}")
        print(f"  {D}{s.reasoning}{RST}")
        print(f"  {Y}↑ {s.improvement}{RST}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{B}OCE — LLM-as-Judge Evaluation{RST}")
    print(f"Provider : {B}{PROVIDER}{RST}  |  Agent: {AGENT_MODEL}  |  Judge: {JUDGE_MODEL}")

    # Show pricing context for this run
    p = _PRICING.get(AGENT_MODEL, {})
    if p.get("input", 0) > 0:
        print(f"Pricing  : ${p['input']}/M input  ${p['output']}/M output  (est. <$0.01 for this run)")
    else:
        print(f"Pricing  : free tier")

    print(f"Company  : {SEED_COMPANY['name']} ({SEED_COMPANY['city']}, {SEED_COMPANY['sector']})")
    print("─" * 62)

    all_scores: dict[str, list[JudgeScore]] = {}
    ctx = {"company": SEED_COMPANY["name"], "sector": SEED_COMPANY["sector"]}

    # Agent 3
    sec("Agent 3 — Opportunity Detection")
    t = time.time()
    opportunities = run_agent3(SEED_COMPANY)
    print(f"  {len(opportunities)} opportunities  ({time.time()-t:.1f}s)  [{_tracker.summary()}]")
    for o in opportunities:
        print(f"  • [{o.get('category','?')}] {o.get('title','?')}")
    s3 = judge("Agent 3", opportunities,
        {**ctx, "tech_stack": SEED_COMPANY["tech_stack"], "current_focus": SEED_COMPANY["current_focus"]},
        ["specificity_to_company", "business_impact", "engineer_actionability", "category_accuracy"])
    show(s3); all_scores["agent3"] = s3

    # Agent 4
    sec("Agent 4 — Skill Match")
    t = time.time()
    matches = run_agent4(SEED_COMPANY, opportunities, RESUME_TEXT)
    print(f"  {len(matches)} matches  ({time.time()-t:.1f}s)  [{_tracker.summary()}]")
    for m in matches:
        print(f"  • {str(m.get('title','?'))[:50]}  →  {m.get('fit_score','?')}/100")
    s4 = judge("Agent 4", matches,
        {**ctx, "resume_summary": "Backend/ML engineer, Indic NLP, Freshworks/Zoho"},
        ["score_calibration", "reasoning_quality", "discrimination_power"])
    show(s4); all_scores["agent4"] = s4

    paired = [(m.get("fit_score", 0), o) for m, o in zip(matches, opportunities) if m.get("fit_score")]
    top_opp = max(paired, default=(0, opportunities[0] if opportunities else {}))[1]

    # Agent 5
    sec(f"Agent 5 — Proof-of-Work  [{top_opp.get('title','top opp')}]")
    t = time.time()
    pow_idea = run_agent5(SEED_COMPANY, top_opp)
    print(f"  {pow_idea.get('name','?')}  ({pow_idea.get('estimated_hours','?')})  ({time.time()-t:.1f}s)  [{_tracker.summary()}]")
    s5 = judge("Agent 5", pow_idea,
        {**ctx, "opportunity": top_opp.get("title"), "tech_stack": SEED_COMPANY["tech_stack"]},
        ["relevance_to_opportunity", "weekend_buildability", "founder_impressiveness", "technical_specificity"])
    show(s5); all_scores["agent5"] = s5

    # Agent 6
    sec("Agent 6 — Founder Research")
    t = time.time()
    founder = run_agent6(SEED_COMPANY)
    print(f"  {founder.get('name','?')} ({founder.get('role','?')})  ({time.time()-t:.1f}s)  [{_tracker.summary()}]")
    for c in founder.get("complaints", []):
        print(f"    – {c}")
    s6 = judge("Agent 6", founder, ctx,
        ["complaint_specificity", "outreach_utility", "background_plausibility"])
    show(s6); all_scores["agent6"] = s6

    # Agent 7
    sec("Agent 7 — Outreach Narrative")
    t = time.time()
    messages = run_agent7(SEED_COMPANY, top_opp, pow_idea, founder, RESUME_TEXT)
    print(f"  {len(messages)} messages  ({time.time()-t:.1f}s)  [{_tracker.summary()}]")
    for msg in messages:
        body = msg.get("body", "")
        print(f"\n  ── {msg.get('channel','?').upper()} ({len(body.split())} words) ──")
        print("  " + body[:280].replace("\n", "\n  ") + ("…" if len(body) > 280 else ""))
    s7 = judge("Agent 7", messages,
        {**ctx, "founder_complaint": (founder.get("complaints") or [""])[0], "pow": pow_idea.get("name")},
        ["hook_specificity", "peer_to_peer_tone", "pow_integration", "cta_effectiveness", "channel_fit"])
    show(s7); all_scores["agent7"] = s7

    # Summary dashboard
    sec("JUDGE SUMMARY DASHBOARD")
    grand_total = grand_count = 0
    for key, scores in all_scores.items():
        if not scores:
            continue
        avg = sum(s.score for s in scores) / len(scores)
        grand_total += sum(s.score for s in scores)
        grand_count += len(scores)
        print(f"\n  {B}{key}{RST}  avg {cs(round(avg))}")
        for s in scores:
            bar = "█" * s.score + "░" * (10 - s.score)
            print(f"    {s.dimension:<40} {bar} {cs(s.score)}")

    if grand_count:
        overall = grand_total / grand_count
        print(f"\n  {B}Overall pipeline quality: {cs(round(overall))} ({overall:.1f}/10){RST}")

    # Cost summary
    print(f"\n  {B}Token usage & cost{RST}")
    print(f"    {_tracker.summary()}")
    if _tracker.cost_usd == 0.0 and PROVIDER != "google":
        print(f"    (pricing not tracked for this provider/model)")
    elif _tracker.cost_usd == 0.0:
        print(f"    (free tier — no cost)")
    else:
        print(f"    Estimated cost: {G}${_tracker.cost_usd:.5f}{RST}  "
              f"({Y}${_tracker.cost_usd * 1000:.4f} per 1000 runs{RST})")

    out = Path(__file__).parent / "eval_results.json"
    out.write_text(json.dumps(
        {k: [vars(s) for s in v] for k, v in all_scores.items()}, indent=2))
    print(f"\n  Results → {out}\n")


if __name__ == "__main__":
    main()
