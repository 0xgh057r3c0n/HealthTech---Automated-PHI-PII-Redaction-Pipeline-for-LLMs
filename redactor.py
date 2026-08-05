import re

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
except ImportError:
    AnalyzerEngine = None
    AnonymizerEngine = None


email_pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
phone_pattern = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b")
date_pattern = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})\b")
name_pattern = re.compile(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b")


analyzer = None
anonymizer = None


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


def redact_text(text: str):
    if not analyzer or not anonymizer:
        _instantiate_presidio()

    if analyzer and anonymizer:
        try:
            results = analyzer.analyze(text=text, language="en")
            anonymized = anonymizer.anonymize(  # type: ignore[arg-type]
                text=text,
                analyzer_results=results
            )
            entities = [result.entity_type for result in results]
            return anonymized.text, entities
        except Exception:
            pass

    return _fallback_redact(text)