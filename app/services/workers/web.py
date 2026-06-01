from html import escape

from app.services.workers.base import BaseWorker, GeneratedFile, WorkerContext, WorkerResult


class WebWorker(BaseWorker):
    async def generate(self, context: WorkerContext) -> WorkerResult:
        llm_result = await self.generate_with_llm(WEB_SYSTEM_PROMPT, _build_web_prompt(context))
        if llm_result:
            return llm_result

        html = _build_html(context)
        css = _build_css()
        readme = _build_readme(context)
        return WorkerResult(
            files=[
                GeneratedFile("index.html", html),
                GeneratedFile("styles.css", css),
                GeneratedFile("README.md", readme),
            ],
            summary="Generated isolated landing page starter files.",
        )


WEB_SYSTEM_PROMPT = """
You are AI-FOS WebWorker.
Generate isolated web or landing-page deliverables for operator review.
Return only valid JSON with this shape:
{
  "summary": "short delivery summary",
  "files": [
    {"path": "index.html", "content": "HTML code"},
    {"path": "styles.css", "content": "CSS code"},
    {"path": "README.md", "content": "review and integration notes"}
  ]
}
Rules:
- Keep files small, reviewable, and isolated.
- Do not require a build step unless the job explicitly asks for framework components.
- If generating Python/PHP/JS, keep syntax valid.
- Do not invent client assets or testimonials.
- Do not include markdown fences around the JSON response.
""".strip()


def _build_web_prompt(context: WorkerContext) -> str:
    stack = ", ".join(context.job.tech_stack or []) or "HTML/CSS"
    return (
        f"Job title: {context.job.title}\n"
        f"Stack hints: {stack}\n"
        f"Job description:\n{context.job.description_raw}\n\n"
        f"Operator instructions:\n{context.instructions or 'None'}\n\n"
        f"Previous QA report:\n{context.previous_qa_report or 'None'}\n\n"
        "Generate isolated source files for the workspace src directory."
    )


def _build_html(context: WorkerContext) -> str:
    title = escape(context.job.title)
    stack = escape(", ".join(context.job.tech_stack or ["HTML", "CSS"]))
    pain = escape((context.job.analysis_reasoning or context.job.description_raw).strip()[:280])
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body>
    <main class="page">
      <section class="hero">
        <p class="eyebrow">AI-FOS WebWorker</p>
        <h1>{title}</h1>
        <p class="lead">{pain}</p>
        <div class="actions">
          <a href="#scope">Review scope</a>
          <a href="#delivery">Delivery plan</a>
        </div>
      </section>

      <section id="scope" class="panel">
        <h2>Technical Scope</h2>
        <p>Recommended stack: {stack}.</p>
        <ul>
          <li>Ship a small, reviewable first version.</li>
          <li>Keep styles and content isolated for client review.</li>
          <li>Prepare integration notes before moving into a production repo.</li>
        </ul>
      </section>

      <section id="delivery" class="panel">
        <h2>Delivery Plan</h2>
        <p>Confirm assets, content, and final deployment target before production handoff.</p>
      </section>
    </main>
  </body>
</html>
"""


def _build_css() -> str:
    return """* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #18202a;
  background: #f6f8fb;
}

.page {
  width: min(1040px, calc(100% - 32px));
  margin: 0 auto;
  padding: 48px 0;
}

.hero,
.panel {
  background: #ffffff;
  border: 1px solid #d9e1ec;
  border-radius: 8px;
  padding: 28px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #0f766e;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2 {
  margin: 0 0 14px;
  line-height: 1.08;
}

h1 {
  font-size: clamp(2rem, 5vw, 4.25rem);
}

.lead {
  max-width: 720px;
  color: #4b5563;
  font-size: 1.08rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.actions a {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  padding: 0 16px;
  border-radius: 8px;
  color: #ffffff;
  background: #2563eb;
  text-decoration: none;
  font-weight: 700;
}
"""


def _build_readme(context: WorkerContext) -> str:
    return (
        f"# Web Worker Output\n\n"
        f"Job: {context.job.title}\n\n"
        "Open `index.html` in a browser to review the isolated landing page starter.\n"
        "Move the markup into Next.js/Laravel only after the operator approves the direction.\n"
    )
