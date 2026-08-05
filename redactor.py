import json
import os
import re
import urllib.error
import urllib.request

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
except ImportError:
    AnalyzerEngine = None
    AnonymizerEngine = None


email_pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
phone_pattern = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
date_pattern = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})\b")
name_pattern = re.compile(r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b")


analyzer = None
anonymizer = None

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _instantiate_presidio():
    global analyzer, anonymizer

    if AnalyzerEngine is None or AnonymizerEngine is None:
        return False

    try:
        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()
        return True
    except Exception:
        analyzer = None
        anonymizer = None
        return False


def _fallback_redact(text: str):
    entities = []
    redacted = text

    def replace_email(match):
        entities.append("EMAIL_ADDRESS")
        return "<EMAIL_ADDRESS>"

    def replace_phone(match):
        entities.append("PHONE_NUMBER")
        return "<PHONE_NUMBER>"

    def replace_date(match):
        entities.append("DATE_TIME")
        return "<DATE_TIME>"

    def replace_name(match):
        entities.append("PERSON")
        return "<PERSON>"

    redacted = email_pattern.sub(replace_email, redacted)
    redacted = phone_pattern.sub(replace_phone, redacted)
    redacted = date_pattern.sub(replace_date, redacted)
    redacted = name_pattern.sub(replace_name, redacted)

    return redacted, entities


def _llm_review(text: str):
    if not GROQ_API_KEY:
        return None

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a privacy redaction helper. Return JSON only with keys "
                    "'redacted_text' and 'entities'. Mask PHI/PII in the text using placeholders "
                    "<PERSON>, <EMAIL_ADDRESS>, <PHONE_NUMBER>, <DATE_TIME>, <HOSPITAL_NAME>, "
                    "<LOCATION>."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }

    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    try:
        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        redacted_text = parsed.get("redacted_text") or text
        return redacted_text, parsed.get("entities", [])
    except Exception:
        return None


def get_redaction_details(text: str):
    if not analyzer or not anonymizer:
        _instantiate_presidio()

    primary_result = None

    if analyzer and anonymizer:
        try:
            results = analyzer.analyze(text=text, language="en")
            anonymized = anonymizer.anonymize(  # type: ignore[arg-type]
                text=text,
                analyzer_results=results
            )
            entities = [result.entity_type for result in results]
            primary_result = (anonymized.text, entities)
        except Exception:
            pass

    fallback_result = _fallback_redact(text)

    if primary_result is None:
        primary_result = fallback_result

    llm_result = _llm_review(text)
    ai_review_enabled = bool(GROQ_API_KEY)

    selected_redacted_text, selected_entities = primary_result
    if llm_result and llm_result[0] != text:
        selected_redacted_text, selected_entities = llm_result

    return {
        "redacted_text": selected_redacted_text,
        "entities": selected_entities,
        "fallback_redacted_text": fallback_result[0],
        "fallback_entities": fallback_result[1],
        "llm_redacted_text": text,
        "llm_entities": llm_result[1] if llm_result else [],
        "ai_review_enabled": ai_review_enabled,
    }


def redact_text(text: str):
    details = get_redaction_details(text)
    return details["redacted_text"], details["entities"]