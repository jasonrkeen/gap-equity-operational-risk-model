"""Project configuration and reusable path helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    input_dir: Path
    output_data_dir: Path
    chart_dir: Path
    pdf_dir: Path

    @classmethod
    def from_root(cls, root: Path) -> "ProjectPaths":
        return cls(
            root=root,
            input_dir=root / "data" / "pinned",
            output_data_dir=root / "outputs" / "data",
            chart_dir=root / "outputs" / "charts",
            pdf_dir=root / "output" / "pdf",
        )

    def ensure_output_directories(self) -> None:
        self.output_data_dir.mkdir(parents=True, exist_ok=True)
        self.chart_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)


MODEL_VERSION = "1.0.1"
VALUATION_BLEND = {"earnings": 0.70, "dcf": 0.30}
