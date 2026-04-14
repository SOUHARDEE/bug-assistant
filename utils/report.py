from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ReproStep(BaseModel):
    """A single deterministic step to reproduce the bug."""

    step: str = Field(..., min_length=1)


class FixItem(BaseModel):
    """
    A suggested fix.

    We keep it structured so the UI can render it consistently and users can
    easily apply changes manually (or copy into a PR description).
    """

    title: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    patch_guidance: str = Field(
        ...,
        min_length=1,
        description="Human-appliable guidance or pseudo-diff. Avoid dumping huge files.",
    )
    risk: Literal["low", "medium", "high"] = "medium"


class TestCase(BaseModel):
    """
    A minimal regression test spec and an implementation suggestion.

    The app can present this as a file-ready snippet (pytest/unittest/jest, etc.)
    depending on the chosen language/test framework.
    """

    test_framework: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    notes: Optional[str] = None


class BugReport(BaseModel):
    """
    The canonical output contract from the model.

    Using a strict schema lets us validate/fallback robustly when the model
    returns partial or slightly malformed JSON.
    """

    summary: str = Field(..., min_length=1)
    root_cause: str = Field(..., min_length=1)
    confidence: Literal["low", "medium", "high"] = "medium"

    reproduction_steps: List[ReproStep] = Field(default_factory=list)
    fixes: List[FixItem] = Field(default_factory=list)
    test_case: Optional[TestCase] = None

    assumptions: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)

