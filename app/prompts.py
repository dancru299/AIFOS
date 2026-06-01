from textwrap import dedent

from app.models import Job

PROPOSAL_SYSTEM_PROMPT = """
You are the Proposal Agent for AI Freelancer OS.

Write high-converting freelance proposals using only the supplied job and master profile.
Do not invent experience, metrics, client names, or project details.

Anti-AI odor rules:
- Do not use: "Dear Hiring Manager"
- Do not use: "I am thrilled to apply"
- Do not use: "As a seasoned developer"
- Do not use: "Upon reading your job description"
- Do not use: "I hope this finds you well"
- Do not use generic self-introductions.

Proposal structure:
1. Pain: address the client's concrete problem in 1-2 sentences.
2. Solution and proof: name the stack or execution plan and cite one matching case study from the profile.
3. CTA: end with one technical question that makes the client reply.

Hard limits:
- Max 120 words for proposal_text.
- Plain text only inside proposal_text.
- Confident, direct, technical, no fluff.
- Return only valid JSON, no markdown.
""".strip()


def build_analyst_prompt(job: Job) -> str:
    return dedent(
        f"""
        Analyze this freelance lead for a solo AI-assisted freelancer.

        Extract:
        - budget estimate, even if it is inferred from text
        - required tech stack as a short string array
        - client country or region if available

        Score ROI from 1 to 10 using strict dollar-focused filtering.

        Good jobs:
        - fixed-price landing pages
        - Next.js, React, Tailwind CSS implementation
        - Laravel/PHP CRUD or admin systems
        - Python scraping or automation with clear target/output
        - clear backend/API/database tasks with bounded scope

        Bad jobs:
        - vague "build a platform like Uber/Airbnb/Facebook"
        - brand identity/logo-only work
        - complex mobile apps with low budgets
        - unclear multi-stakeholder requirements
        - unpaid, equity-only, or "cheap quick job" language

        Return only JSON, no markdown:
        {{
          "roi_score": 8.5,
          "is_good_job": true,
          "budget_estimate": "$400 fixed",
          "tech_stack": ["Next.js", "Tailwind CSS"],
          "client_country": "United States",
          "reasoning": "US client, clear Next.js/Tailwind landing page, fixed-price scope, no scope creep signals."
        }}

        Job:
        source: {job.source}
        title: {job.title}
        budget: {job.budget_raw or "unknown"}
        location: {job.client_location or "unknown"}
        metadata: {job.client_metadata or {}}
        description:
        {job.description_raw}
        """
    ).strip()


def build_proposal_prompt(job: Job, portfolio_markdown: str, max_words: int) -> str:
    return dedent(
        f"""
        Create a proposal for this job.
        The proposal_text must be no more than {max_words} words.

        Return only JSON with:
        {{
          "proposal_text": "<proposal>",
          "estimated_bid": "<fixed bid or range>",
          "timeline": "<delivery timeline>"
        }}

        Job:
        id: {job.id}
        title: {job.title}
        source: {job.source}
        budget raw: {job.budget_raw or "unknown"}
        budget estimate: {job.budget_estimate or "unknown"}
        client location: {job.client_location or "unknown"}
        client country: {job.client_country or "unknown"}
        tech stack: {", ".join(job.tech_stack or []) or "unknown"}
        analyst reasoning: {job.analysis_reasoning or "unknown"}
        description:
        {job.description_raw}

        Master profile:
        {portfolio_markdown}
        """
    ).strip()
