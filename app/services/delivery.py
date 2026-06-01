from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.services.workspace import WorkspacePaths


class DeliveryService:
    def create_zip(self, workspace: WorkspacePaths, version: int = 1) -> Path:
        delivery_path = workspace.root / f"delivery_v{version}.zip"
        src_root = workspace.src.resolve()

        with ZipFile(delivery_path, mode="w", compression=ZIP_DEFLATED) as archive:
            for path in sorted(src_root.rglob("*")):
                if not path.is_file() or "__pycache__" in path.parts:
                    continue
                archive.write(path, arcname=Path("src") / path.relative_to(src_root))

            qa_report = workspace.qa_reports / "qa_report.json"
            if qa_report.exists():
                archive.write(qa_report, arcname=Path("qa_reports") / "qa_report.json")

            pm_brief = workspace.inputs / "pm_brief.md"
            if pm_brief.exists():
                archive.write(pm_brief, arcname=Path("inputs") / "pm_brief.md")

        return delivery_path
