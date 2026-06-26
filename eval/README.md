# OCE — LLM-as-Judge Evaluation Harness

Runs OCE agents 3–7 against a seeded company profile and scores the outputs using a second LLM judge call.

**No Tavily or Firecrawl key required** — uses a hardcoded seed company (Sarvam AI).

## Setup

```bash
pip install anthropic          # if using Claude
pip install google-generativeai  # if using Gemini (free tier)
```

Create `eval/.env` with **one** of:

```env
# Option A — Claude (console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-...

# Option B — Gemini 2.0 Flash, free tier (aistudio.google.com/app/apikey)
GOOGLE_API_KEY=AIza...
```

## Run

```bash
python eval/judge.py
```

## What it evaluates

| Agent | Dimensions scored |
|-------|-------------------|
| Agent 3 — Opportunity Detection | specificity_to_company, business_impact, engineer_actionability, category_accuracy |
| Agent 4 — Skill Match | score_calibration, reasoning_quality, discrimination_power |
| Agent 5 — Proof-of-Work | relevance_to_opportunity, weekend_buildability, founder_impressiveness, technical_specificity |
| Agent 6 — Founder Research | complaint_specificity, outreach_utility, background_plausibility |
| Agent 7 — Outreach Narrative | hook_specificity, peer_to_peer_tone, pow_integration, cta_effectiveness, channel_fit |

Results are printed with a colour-coded dashboard and saved to `eval/eval_results.json`.
