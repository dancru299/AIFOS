import re
from dataclasses import dataclass

from app.core.config import Settings
from app.models import Job
from app.prompts import PROPOSAL_SYSTEM_PROMPT, build_proposal_prompt
from app.services.llm import LLMTextService, load_json_object


@dataclass
class ProposalDraft:
    proposal_text: str
    estimated_bid: str
    timeline: str

    @property
    def suggested_price(self) -> str:
        return self.estimated_bid


class ProposalService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_proposal(self, job: Job, portfolio_markdown: str) -> ProposalDraft:
        provider = self.settings.proposal_provider.lower()

        if provider == "mock":
            return self._generate_locally(job, portfolio_markdown)
        if provider == "auto" and not self._has_llm_key():
            if self.settings.allow_mock_llm:
                return self._generate_locally(job, portfolio_markdown)
            raise RuntimeError("No proposal LLM API key is configured and mock mode is disabled.")

        return await self._generate_with_llm(job, portfolio_markdown, provider)

    def _has_llm_key(self) -> bool:
        return bool(
            self.settings.deepseek_api_key
            or self.settings.gemini_api_key
            or self.settings.anthropic_api_key
            or self.settings.openai_api_key
        )

    async def _generate_with_llm(self, job: Job, portfolio_markdown: str, provider: str) -> ProposalDraft:
        # Proposal is short outreach writing → DeepSeek light tier.
        llm_provider = provider if provider in {"deepseek", "gemini", "anthropic", "openai"} else "auto"
        prompt = build_proposal_prompt(job, portfolio_markdown, self.settings.proposal_max_words)
        content = await LLMTextService(self.settings, llm_provider, light=True).generate_text(
            PROPOSAL_SYSTEM_PROMPT,
            prompt,
            temperature=0.4,
        )
        parsed = load_json_object(content)
        return _draft_from_payload(parsed)

    def _generate_locally(self, job: Job, portfolio_markdown: str) -> ProposalDraft:
        proof = _select_case_study(job, portfolio_markdown)
        stack = _suggest_stack(job)
        bid = _suggest_price(job.budget_estimate or job.budget_raw)
        timeline = _suggest_timeline(job)
        proposal = (
            f"You need {job.title.lower()} delivered without scope creep or vague handoff. "
            f"I would build it with {stack}, keep the workflow tight, and ship a testable version first. "
            f"The closest proof is my {proof}, which maps well to this kind of scoped build. "
            "What is the main technical constraint I should design around first?"
        )
        words = proposal.split()
        if len(words) > self.settings.proposal_max_words:
            proposal = " ".join(words[: self.settings.proposal_max_words]).rstrip(".") + "?"
        return ProposalDraft(proposal_text=proposal, estimated_bid=bid, timeline=timeline)


def _extract_first_project_url(portfolio_markdown: str) -> str | None:
    match = re.search(r"https?://\S+", portfolio_markdown)
    if match:
        return match.group(0)
    return None


def _suggest_stack(job: Job) -> str:
    haystack = f"{job.title} {job.description_raw}".lower()
    if job.tech_stack:
        return " + ".join(job.tech_stack[:3])
    if "landing page" in haystack or "tailwind" in haystack or "figma" in haystack:
        return "Next.js + Tailwind"
    if "scrap" in haystack or "crawler" in haystack:
        return "Python + Playwright"
    if "laravel" in haystack or "livewire" in haystack:
        return "Laravel + Livewire"
    if "crud" in haystack or "api" in haystack:
        return "Laravel or FastAPI backend"
    return "web"


def _suggest_price(budget_raw: str | None) -> str:
    if budget_raw:
        return budget_raw
    return "$300-$600 fixed"


def _suggest_timeline(job: Job) -> str:
    haystack = f"{job.title} {job.description_raw}".lower()
    if any(token in haystack for token in ("landing page", "figma", "tailwind")):
        return "2-4 days"
    if any(token in haystack for token in ("scrap", "crawler", "automation")):
        return "3-5 days after target/access confirmation"
    if any(token in haystack for token in ("dashboard", "crud", "admin", "api")):
        return "5-10 days depending on module count"
    return "3-7 days after scope confirmation"


def _select_case_study(job: Job, portfolio_markdown: str) -> str:
    haystack = f"{job.title} {job.description_raw}".lower()
    if any(token in haystack for token in ("recruit", "ats", "hr", "dashboard", "crud", "admin")):
        return "Recruitment ATS case study"
    if any(token in haystack for token in ("journal", "note", "editor", "flip", "interactive")):
        return "Flipbook Journal / Note-taking app"
    if any(token in haystack for token in ("social", "vps", "aapanel", "deploy", "hosting")):
        return "Social Media System on aaPanel/VPS"
    if "Recruitment ATS" in portfolio_markdown:
        return "Recruitment ATS case study"
    return "closest matching portfolio case study"


def _draft_from_payload(payload: dict) -> ProposalDraft:
    proposal_text = str(payload.get("proposal_text", "")).strip()
    estimated_bid = str(payload.get("estimated_bid", payload.get("suggested_price", ""))).strip()
    timeline = str(payload.get("timeline", payload.get("estimated_timeline", ""))).strip()

    if not proposal_text:
        raise ValueError(f"Proposal response did not include proposal_text: {payload}")

    return ProposalDraft(
        proposal_text=proposal_text,
        estimated_bid=estimated_bid or "$300-$600 fixed",
        timeline=timeline or "3-7 days after scope confirmation",
    )
