import re
from dataclasses import dataclass

from app.core.config import Settings
from app.models import Job
from app.prompts import build_analyst_prompt
from app.services.llm import LLMTextService, load_json_object

ANALYST_SYSTEM_PROMPT = """
You are the Analyst Agent for AI Freelancer OS.

Your job is to filter for profitable, bounded freelance work. Be strict.

Return only a valid JSON object with this schema:
{
  "roi_score": 8.5,
  "is_good_job": true,
  "budget_estimate": "$400 fixed",
  "tech_stack": ["Next.js", "Tailwind CSS"],
  "client_country": "United States",
  "reasoning": "Short, specific reasoning. Mention why the scope is profitable or risky."
}

Scoring rules:
- 9-10: clear fixed-price, strong tech match, verified/high-signal client, narrow deliverable, low scope risk.
- 7-8.9: worth human review; clear enough and likely profitable.
- 5-6.9: maybe useful later but do not alert.
- 1-4.9: reject; vague, underpriced, risky, or outside target work.

Good patterns: fixed-price landing pages, Next.js/React/Tailwind builds, Laravel/PHP CRUD, admin dashboards, Python scraping, automation, REST APIs, small backend systems, SEO/blog content with clear scope.
Bad patterns: "build an app like Uber/Airbnb/Facebook", vague platform builds, brand/logo-only design, complex mobile apps, unclear stakeholders, equity-only, unrealistic budget, long discovery before scope is known.

Set is_good_job=true only when the job deserves a Telegram alert for human review.
""".strip()


GOOD_PATTERNS = (
    "next.js",
    "nextjs",
    "react",
    "landing page",
    "tailwind",
    "figma",
    "scraping",
    "crawler",
    "python",
    "crud",
    "backend api",
    "blog post",
    "seo article",
    "automation",
    "api",
    "laravel",
)

BAD_PATTERNS = (
    "uber",
    "airbnb",
    "multi-vendor",
    "stakeholder",
    "brand identity",
    "logo",
    "mobile app",
    "ios and android",
    "social network",
)


@dataclass
class AnalystDecision:
    score: float
    is_good_job: bool
    reasoning: str
    budget_estimate: str | None = None
    tech_stack: list[str] | None = None
    client_country: str | None = None


class AnalystService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def analyze_job(self, job: Job) -> AnalystDecision:
        provider = self.settings.analyst_provider.lower()

        if provider == "mock":
            return self._analyze_with_heuristics(job)
        if provider == "auto" and not self._has_llm_key():
            if self.settings.allow_mock_llm:
                return self._analyze_with_heuristics(job)
            raise RuntimeError("No analyst LLM API key is configured and mock mode is disabled.")

        return await self._analyze_with_llm(job, provider)

    def _has_llm_key(self) -> bool:
        return bool(
            self.settings.deepseek_api_key
            or self.settings.gemini_api_key
            or self.settings.openai_api_key
            or self.settings.anthropic_api_key
        )

    async def _analyze_with_llm(self, job: Job, provider: str) -> AnalystDecision:
        # Analyst does analysis → DeepSeek heavy tier (default light=False).
        llm_provider = provider if provider in {"deepseek", "gemini", "openai", "anthropic"} else "auto"
        prompt = build_analyst_prompt(job)
        content = await LLMTextService(self.settings, llm_provider).generate_text(
            ANALYST_SYSTEM_PROMPT,
            prompt,
            temperature=0.2,
        )
        parsed = load_json_object(content)
        return _decision_from_payload(parsed)

    def _analyze_with_heuristics(self, job: Job) -> AnalystDecision:
        haystack = f"{job.title} {job.description_raw}".lower()
        score = 5.0
        reasons: list[str] = []

        for pattern in GOOD_PATTERNS:
            if pattern in haystack:
                score += 0.8
                reasons.append(f"matched good pattern: {pattern}")

        for pattern in BAD_PATTERNS:
            if pattern in haystack:
                score -= 1.5
                reasons.append(f"matched bad pattern: {pattern}")

        if job.budget_raw and any(token in job.budget_raw.lower() for token in ("$", "usd", "fixed")):
            score += 0.4
            reasons.append("budget is explicit")

        if job.client_location:
            score += 0.2
            reasons.append("client location is available")

        score = max(1.0, min(10.0, round(score, 1)))
        tech_stack = _extract_tech_stack(haystack)
        budget_estimate = job.budget_raw or _extract_budget(haystack)
        client_country = job.client_location or _extract_country(haystack)
        is_good_job = score >= self.settings.analyst_threshold

        if not reasons:
            reasons.append("default heuristic score based on limited metadata")

        return AnalystDecision(
            score=score,
            is_good_job=is_good_job,
            reasoning="; ".join(reasons),
            budget_estimate=budget_estimate,
            tech_stack=tech_stack,
            client_country=client_country,
        )


def _decision_from_payload(payload: dict) -> AnalystDecision:
    score = payload.get("roi_score", payload.get("score"))
    if score is None:
        raise ValueError(f"Analyst response did not include roi_score: {payload}")

    reasoning = str(payload.get("reasoning", "")).strip()
    tech_stack = payload.get("tech_stack")
    if isinstance(tech_stack, str):
        tech_stack = [item.strip() for item in tech_stack.split(",") if item.strip()]
    if tech_stack is not None and not isinstance(tech_stack, list):
        tech_stack = None

    return AnalystDecision(
        score=float(score),
        is_good_job=_as_bool(payload.get("is_good_job"), default=float(score) >= 7.0),
        reasoning=reasoning or "No reasoning returned.",
        budget_estimate=_clean_optional_string(payload.get("budget_estimate")),
        tech_stack=[str(item).strip() for item in tech_stack if str(item).strip()] if tech_stack else None,
        client_country=_clean_optional_string(payload.get("client_country")),
    )


def _clean_optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_bool(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    return bool(value)


def _extract_tech_stack(haystack: str) -> list[str]:
    stack_map = {
        "next.js": "Next.js",
        "nextjs": "Next.js",
        "react": "React",
        "tailwind": "Tailwind CSS",
        "laravel": "Laravel",
        "php": "PHP",
        "python": "Python",
        "scraping": "Python scraping",
        "playwright": "Playwright",
        "node": "Node.js",
        "mongodb": "MongoDB",
        "mysql": "MySQL",
        "postgres": "PostgreSQL",
        "api": "REST API",
    }
    result: list[str] = []
    for token, label in stack_map.items():
        if token in haystack and label not in result:
            result.append(label)
    return result


def _extract_budget(haystack: str) -> str | None:
    match = re.search(r"(\$\s?\d[\d,]*(?:\s?-\s?\$?\d[\d,]*)?)", haystack, re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "")
    return None


def _extract_country(haystack: str) -> str | None:
    for country in ("united states", "usa", "canada", "uk", "united kingdom", "australia", "germany", "france"):
        if country in haystack:
            return "United States" if country in {"united states", "usa"} else country.title()
    return None
