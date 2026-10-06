from __future__ import annotations

from backend.config import Settings, get_settings
from backend.utils.text_utils import parse_terms, sanitize_text


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini cannot be initialized because configuration is missing."""


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini fails to generate a usable document."""


class GeminiDocumentGenerator:
    def __init__(self, settings: Settings | None = None, client=None):
        self.settings = settings or get_settings()
        if client is not None:
            self.client = client
            self._types = None
            return
        if not self.settings.gemini_api_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not configured. Add it to .env before generating a document."
            )
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise GeminiConfigurationError(
                "The google-genai package is not installed. Run: pip install -r requirements.txt"
            ) from exc
        self._types = types
        self.client = genai.Client(api_key=self.settings.gemini_api_key)

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:
        term_lines = "\n".join(f"- {item}" for item in parse_terms(terms)) or "- No additional terms supplied."
        prompt = f"""
You are the legal drafting engine for LegalEase.

Create a professional legal document draft from the user's supplied information.
Do not invent material facts, names, amounts, dates, addresses, governing law, or obligations.
If a material field is absent, use a clearly marked placeholder such as [GOVERNING LAW].
Preserve the user's requested terms and do not contradict them.
Use neutral, professional legal language and clear section headings.
The result is a draft for review, not legal advice.

DOCUMENT TYPE:
{sanitize_text(document_type)}

PARTIES:
{sanitize_text(parties)}

EFFECTIVE DATE:
{sanitize_text(effective_date)}

USER-SUPPLIED TERMS:
{term_lines}

OUTPUT REQUIREMENTS:
1. Start with a concise document title.
2. Include an introductory section identifying the parties and effective date.
3. Organize the agreement into numbered sections with meaningful headings.
4. Include definitions only when useful.
5. Include the supplied business terms accurately.
6. Include standard boilerplate only where appropriate, and mark missing jurisdiction-specific information as placeholders.
7. End with signature blocks appropriate to the parties.
8. Do not include Markdown code fences.
9. Do not claim that the document is legally valid in a particular jurisdiction.
10. Keep the output directly usable as a document draft.
""".strip()
        if len(prompt) > self.settings.max_prompt_chars:
            raise ValueError("Input is too large. Shorten the parties or terms and try again.")
        return prompt

    def generate_document(self, document_type: str, parties: str, terms: str, effective_date: str) -> str:
        prompt = self.build_prompt(document_type, parties, terms, effective_date)
        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=self._types.GenerateContentConfig(
                    temperature=0.25,
                    max_output_tokens=8_000,
                    candidate_count=1,
                ),
            )
        except Exception as exc:  # SDK exception classes vary by version/provider.
            raise GeminiGenerationError(f"Gemini request failed: {exc}") from exc

        text = getattr(response, "text", None)
        text = sanitize_text(text or "")
        if not text:
            raise GeminiGenerationError("Gemini returned an empty document.")
        return text
