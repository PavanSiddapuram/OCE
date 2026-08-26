"""
Resume tailoring utility.

Loads master_resume.json and selects only the bullet blocks whose tags
overlap with a given set of skills/domains. Always includes pinned blocks.
Returns a plain-text resume string ready to drop into an LLM prompt.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_RESUME_PATH = Path(__file__).parent.parent.parent / "data" / "resume" / "master_resume.json"
_resume_data: dict | None = None


def _load() -> dict:
    global _resume_data
    if _resume_data is None:
        try:
            _resume_data = json.loads(_RESUME_PATH.read_text())
        except Exception as exc:
            logger.warning("Could not load master_resume.json: %s", exc)
            _resume_data = {}
    return _resume_data


def tailor_resume(skills: list[str], domains: list[str] | None = None, max_bullets: int = 20) -> str:
    """
    Return a trimmed resume string keeping only bullets relevant to the given
    skills and domains.  Pinned blocks always appear.  Falls back to the full
    summary when the JSON is unavailable.

    Args:
        skills:      list of skill strings (e.g. ["react", "python", "ml"])
        domains:     list of domain strings (e.g. ["3d", "ai", "web"])
        max_bullets: safety cap so prompts don't blow up for giant resumes
    """
    data = _load()
    if not data:
        return ""

    skills_lower  = {s.lower() for s in skills}
    domains_lower = {d.lower() for d in (domains or [])}
    target = skills_lower | domains_lower

    lines: list[str] = []

    # ── basics ────────────────────────────────────────────────────────────────
    basics = data.get("basics", {})
    name   = basics.get("name", "")
    if name:
        lines.append(f"Name: {name}")

    # ── summary ───────────────────────────────────────────────────────────────
    summary = data.get("summary", {})
    if summary.get("text"):
        lines += ["", "Summary:", summary["text"]]

    # ── experience bullets ────────────────────────────────────────────────────
    bullet_count = 0
    lines.append("\nExperience:")
    for exp in data.get("experience", []):
        exp_header_added = False
        for bullet in exp.get("bullets", []):
            if bullet_count >= max_bullets:
                break
            tags = bullet.get("tags", {})
            b_skills  = {s.lower() for s in tags.get("skills",  [])}
            b_domains = {d.lower() for d in tags.get("domains", [])}
            b_titles  = {t.lower() for t in tags.get("titles",  [])}
            relevant  = bool(target & (b_skills | b_domains | b_titles))
            pinned    = exp.get("pinned", False) or bullet.get("pinned", False)

            if pinned or relevant:
                if not exp_header_added:
                    lines.append(
                        f"\n{exp.get('company', '')} — {exp.get('title', '')} ({exp.get('period', '')})"
                    )
                    exp_header_added = True
                lines.append(f"  • {bullet['text']}")
                bullet_count += 1

    # ── projects ──────────────────────────────────────────────────────────────
    projects = data.get("projects", [])
    if projects:
        lines.append("\nProjects:")
    for proj in projects:
        tags      = proj.get("tags", {})
        p_skills  = {s.lower() for s in tags.get("skills",  [])}
        p_domains = {d.lower() for d in tags.get("domains", [])}
        p_titles  = {t.lower() for t in tags.get("titles",  [])}
        relevant  = bool(target & (p_skills | p_domains | p_titles))
        pinned    = proj.get("pinned", False)
        if pinned or relevant:
            lines.append(f"  • {proj.get('name', '')}: {proj.get('description', '')}")

    # ── skills section ────────────────────────────────────────────────────────
    skill_groups = data.get("skills", {})
    if skill_groups:
        lines.append("\nSkills:")
        for group, items in skill_groups.items():
            if isinstance(items, list):
                lines.append(f"  {group}: {', '.join(items)}")

    return "\n".join(lines).strip()
