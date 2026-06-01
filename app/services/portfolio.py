from app.core.config import Settings


class PortfolioService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def load_markdown(self) -> str:
        profile_path = self.settings.resolved_portfolio_path
        if not profile_path.exists():
            raise FileNotFoundError(
                f"Portfolio markdown not found at {profile_path}. "
                "Create the file and keep it concise for proposal prompting."
            )

        markdown = profile_path.read_text(encoding="utf-8").strip()
        if len(markdown) > 20_000:
            raise ValueError(
                f"Portfolio markdown is too large ({len(markdown)} chars). "
                "Use a compact master profile instead of raw exports or HTML."
            )
        return markdown
