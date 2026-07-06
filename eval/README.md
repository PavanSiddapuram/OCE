# OCE — LLM-as-Judge Evaluation Harness

Runs OCE agents 3–7 against a seeded company profile (Sarvam AI) and scores
each output using a second LLM judge call. No Tavily or Firecrawl required.

## Provider pricing comparison

| Provider | Model | Input | Output | Est. cost / run |
|----------|-------|-------|--------|-----------------|
| **DeepSeek** | deepseek-chat (V3) | $0.27/M | $1.10/M | **~$0.001** ← cheapest |
| Google | gemini-2.0-flash | free tier | free tier | $0.00 (rate-limited) |
| Anthropic | claude-haiku-4-5 (agents) + sonnet-4-6 (judge) | $0.80–3.00/M | $4–15/M | ~$0.05 |

## Setup

```bash
# DeepSeek (recommended — best value)
pip install openai
echo "DEEPSEEK_API_KEY=sk-..." > eval/.env

# Google Gemini (free tier)
pip install google-generativeai
echo "GOOGLE_API_KEY=AIza..." > eval/.env

# Anthropic Claude
pip install anthropic
echo "ANTHROPIC_API_KEY=sk-ant-..." > eval/.env
```

Get keys:
- DeepSeek → platform.deepseek.com
- Google   → aistudio.google.com/app/apikey
- Anthropic → console.anthropic.com

## Run

```bash
python eval/judge.py
```

## What gets evaluated

| Agent | Dimensions |
|-------|------------|
| Agent 3 — Opportunity Detection | specificity_to_company, business_impact, engineer_actionability, category_accuracy |
| Agent 4 — Skill Match | score_calibration, reasoning_quality, discrimination_power |
| Agent 5 — Proof-of-Work | relevance_to_opportunity, weekend_buildability, founder_impressiveness, technical_specificity |
| Agent 6 — Founder Research | complaint_specificity, outreach_utility, background_plausibility |
| Agent 7 — Outreach Narrative | hook_specificity, peer_to_peer_tone, pow_integration, cta_effectiveness, channel_fit |

Each run prints token usage, per-call latency, and exact cost. Results saved to `eval/eval_results.json`.
