from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

from src.config.prompts import SYSTEM_PROMPT
from src.config.settings import Settings


@dataclass
class EmailContent:
    subject: str
    body: str


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json_object(text: str) -> dict:
    """Extract and parse the first JSON object found in `text`."""
    text = (text or "").strip()

    # Fast path: whole string is JSON
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Fallback: find first {...} block
    m = _JSON_OBJECT_RE.search(text)
    if not m:
        raise ValueError("Model output enthält kein JSON-Objekt.")

    candidate = m.group(0).strip()
    obj = json.loads(candidate)
    if not isinstance(obj, dict):
        raise ValueError("Model JSON ist kein Objekt (dict).")
    return obj


def _validate_email_content(subject: str, body: str) -> EmailContent:
    subject = (subject or "").strip()
    body = (body or "").strip()

    if not subject:
        raise ValueError('"subject" ist leer.')
    if not body:
        raise ValueError('"body" ist leer.')

    # Hard limits (passt zu deinem Prompt und verhindert Header-Probleme)
    if len(subject) > 80:
        subject = subject[:80].rstrip()

    # Optional: Body nicht unendlich wachsen lassen
    if len(body) > 4000:
        body = body[:4000].rstrip() + "\n\n[gekürzt]"

    return EmailContent(subject=subject, body=body)


def generate_email_content(
    settings: Settings,
    *,
    iteration: Optional[int] = None,
    extra_instruction: Optional[str] = None,
) -> EmailContent:
    """Generiert Subject + Body via OpenAI (Responses API) und liefert EmailContent.

    - `iteration`: optional, um Variation zu erzwingen (z.B. Mail #3)
    - `extra_instruction`: optional, um situativen Kontext zu geben
    """

    client = OpenAI(api_key=settings.openai_api_key)

    # User-Input: kleiner Kontext, damit jede Mail anders wird
    user_input_parts = []
    if iteration is not None:
        user_input_parts.append(f"Generiere eine neue Test-E-Mail. Nummer: {iteration}.")
    else:
        user_input_parts.append("Generiere eine neue Test-E-Mail.")

    if extra_instruction:
        user_input_parts.append(extra_instruction)

    user_input_parts.append(
        'Gib ausschließlich JSON zurück, z.B. {"subject":"...","body":"..."}.'
    )

    user_input = "\n".join(user_input_parts)

    resp = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )

    # Laut Docs: output_text enthält den zusammengefassten Text-Output
    raw_text = (resp.output_text or "").strip()

    obj = _extract_json_object(raw_text)
    subject = obj.get("subject", "")
    body = obj.get("body", "")

    return _validate_email_content(subject, body)
