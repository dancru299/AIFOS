import json
import re

from app.services.workers.base import BaseWorker, GeneratedFile, WorkerContext, WorkerResult


class ContentWorker(BaseWorker):
    async def generate(self, context: WorkerContext) -> WorkerResult:
        llm_result = await self.generate_with_llm(CONTENT_SYSTEM_PROMPT, _build_content_prompt(context))
        if llm_result:
            return llm_result

        title = _clean_title(context.job.title)
        keywords = _extract_keywords(context)
        outline = _build_outline(title, keywords)
        article = _build_article(title, keywords, outline, context)
        research_notes = _build_research_notes(title, keywords, outline)
        metadata = {
            "worker": "content",
            "job_id": context.job.id,
            "primary_keyword": keywords[0],
            "keywords": keywords,
            "attempt": context.attempt,
        }
        return WorkerResult(
            files=[
                GeneratedFile("competitor_notes.md", research_notes),
                GeneratedFile("article.md", article),
                GeneratedFile("content_meta.json", json.dumps(metadata, indent=2)),
            ],
            summary=f"Drafted SEO article for '{keywords[0]}' with {len(outline)} sections.",
        )


CONTENT_SYSTEM_PROMPT = """
You are AI-FOS ContentWorker.
Create practical SEO content deliverables from the supplied PM brief.
Return only valid JSON with this shape:
{
  "summary": "short delivery summary",
  "files": [
    {"path": "article.md", "content": "markdown article"},
    {"path": "competitor_notes.md", "content": "keyword and outline notes"}
  ]
}
Rules:
- Write natural, useful Markdown.
- Use clear H1/H2/H3 heading structure.
- Include keyword intent and practical implementation advice.
- Do not invent client results, metrics, or private case studies.
- Do not include markdown fences around the JSON response.
""".strip()


def _build_content_prompt(context: WorkerContext) -> str:
    return (
        f"Job title: {context.job.title}\n"
        f"Job description:\n{context.job.description_raw}\n\n"
        f"Operator instructions:\n{context.instructions or 'None'}\n\n"
        f"Previous QA report:\n{context.previous_qa_report or 'None'}\n\n"
        "Generate article.md and competitor_notes.md for the workspace src directory."
    )


def _clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip().strip(".") or "SEO Article"


def _extract_keywords(context: WorkerContext) -> list[str]:
    haystack = f"{context.job.title} {context.job.description_raw} {context.instructions or ''}".lower()
    candidates = [
        "automation workflow",
        "web scraping",
        "next.js landing page",
        "laravel dashboard",
        "seo content",
    ]
    keywords = [candidate for candidate in candidates if any(part in haystack for part in candidate.split())]
    if not keywords:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+-]{3,}", haystack)
        keywords = list(dict.fromkeys(words[:5])) or ["business workflow"]
    return keywords[:5]


def _build_outline(title: str, keywords: list[str]) -> list[str]:
    primary = keywords[0]
    return [
        f"Why {primary} matters now",
        "Common mistakes to avoid",
        "A practical implementation plan",
        "Tools, workflow, and quality checks",
        "How to measure the result",
    ]


def _build_research_notes(title: str, keywords: list[str], outline: list[str]) -> str:
    return (
        f"# Competitor Structure Notes: {title}\n\n"
        "This lightweight research brief simulates the content structure a ContentWorker should collect before drafting.\n\n"
        "## Keyword Cluster\n"
        + "\n".join(f"- {keyword}" for keyword in keywords)
        + "\n\n## Recommended Article Structure\n"
        + "\n".join(f"- {section}" for section in outline)
        + "\n\n## Differentiation Angle\n"
        "- Prefer practical steps, concrete examples, and a direct technical voice over generic marketing claims.\n"
    )


def _build_article(title: str, keywords: list[str], outline: list[str], context: WorkerContext) -> str:
    primary = keywords[0]
    keyword_line = ", ".join(keywords)
    client_context = context.job.description_raw.strip()
    repair_note = ""
    if context.previous_qa_report:
        repair_note = "\n\n> Revision note: addressed QA feedback from the previous attempt.\n"

    sections = "\n\n".join(
        f"## {heading}\n"
        f"{primary.title()} works best when the requirements are translated into a small, testable workflow. "
        f"For this project, the priority is to keep the output useful, easy to review, and aligned with the client's original request. "
        f"A strong draft should explain the problem, name the trade-offs, and show the reader exactly what to do next."
        for heading in outline
    )
    return (
        f"# {title}\n\n"
        f"Primary keyword: **{primary}**  \n"
        f"Supporting keywords: {keyword_line}\n\n"
        "## Search Intent\n"
        "The reader wants a clear, practical answer without filler. The article should solve the problem directly, "
        "use natural headings, and avoid inflated claims.\n\n"
        "## Client Context\n"
        f"{client_context}\n"
        f"{repair_note}\n\n"
        f"{sections}\n\n"
        "## Final Takeaway\n"
        f"The best way to approach {primary} is to define the expected output, confirm the constraints, build the first version, "
        "and verify the result against the original goal before expanding scope.\n"
    )
