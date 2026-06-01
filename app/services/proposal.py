import json
import re
from dataclasses import dataclass

import httpx

from app.core.config import Settings
from app.models import Job
from app.prompts import PROPOSAL_SYSTEM_PROMPT, build_proposal_prompt
from app.services.gemini import GeminiService


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

        if provider == "gemini":
            return await self._generate_with_gemini(job, portfolio_markdown)
        if provider == "anthropic":
            return await self._generate_with_anthropic(job, portfolio_markdown)
        if provider == "openai":
            return await self._generate_with_openai(job, portfolio_markdown)
        if provider == "mock":
            return self._generate_locally(job, portfolio_markdown)

        if self.settings.gemini_api_key:
            return await self._generate_with_gemini(job, portfolio_markdown)
        if self.settings.anthropic_api_key:
            return await self._generate_with_anthropic(job, portfolio_markdown)
        if self.settings.openai_api_key:
            return await self._generate_with_openai(job, portfolio_markdown)
        if self.settings.allow_mock_llm:
            return self._generate_locally(job, portfolio_markdown)
        raise RuntimeError("No proposal LLM API key is configured and mock mode is disabled.")

    async def _generate_with_gemini(self, job: Job, portfolio_markdown: str) -> ProposalDraft:
        if not self.settings.gemini_api_key:
            raise RuntimeError("Gemini API key is not configured.")
        prompt = build_proposal_prompt(job, portfolio_markdown, self.settings.proposal_max_words)
        content = await GeminiService(self.settings).generate_text(
            prompt,
            system_instruction=PROPOSAL_SYSTEM_PROMPT,
            temperature=0.4,
        )
        parsed = _load_json_object(content)
        return _draft_from_payload(parsed)

    async def _generate_with_openai(self, job: Job, portfolio_markdown: str) -> ProposalDraft:
        if not self.settings.openai_api_key:
            raise RuntimeError("OpenAI API key is not configured.")

        prompt = build_proposal_prompt(job, portfolio_markdown, self.settings.proposal_max_words)
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": PROPOSAL_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = _load_json_object(content)
        return _draft_from_payload(parsed)

    async def _generate_with_anthropic(self, job: Job, portfolio_markdown: str) -> ProposalDraft:
        if not self.settings.anthropic_api_key:
            raise RuntimeError("Anthropic API key is not configured.")
        prompt = build_proposal_prompt(job, portfolio_markdown, self.settings.proposal_max_words)
        payload = {
            "model": self.settings.anthropic_model,
            "max_tokens": 450,
            "system": PROPOSAL_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
        content = "\n".join(text_blocks).strip()
        parsed = _load_json_object(content)
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


def _load_json_object(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))
