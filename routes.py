from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    """Request payload for legal document generation."""

    document_type: str = Field(..., min_length=1)
    parties: str = Field(..., min_length=1)
    terms: str = Field(..., min_length=1)
    dates: str = Field(..., min_length=1)

    @field_validator("document_type", "parties", "terms", "dates", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        if value is None:
            raise ValueError("This field is required.")
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("This field cannot be empty.")
        return cleaned


@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    """Generate a custom legal document using Gemini."""
    try:
        response = gemini_generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"Generation request failed: {exc}") from exc
    except Exception as exc:  # pragma: no cover - normal fallback path
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc
    return {"document": response}
