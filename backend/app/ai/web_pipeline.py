"""
Web AI Pipeline - TF-IDF + RandomForest model inference
Processes web content using vectorized text features
"""
import logging
from .loader import get_web_model, get_web_vectorizer

logger = logging.getLogger(__name__)


def extract_web_content(scan_result):
    """
    Extract web content for AI analysis.
    Combines findings evidence, headers info, and response content.
    """
    content_parts = []

    # Extract from findings/evidence
    findings = scan_result.get("findings", [])
    for finding in findings:
        evidence = finding.get("evidence", "")
        finding_type = finding.get("type", "")
        category = finding.get("category", "")
        if evidence:
            content_parts.append(f"{finding_type} {category} {evidence}")

    # Extract from vulnerability details
    vulnerabilities = scan_result.get("vulnerabilities", [])
    for vuln in vulnerabilities:
        vuln_type = vuln.get("type", "")
        evidence = vuln.get("evidence", "")
        if vuln_type:
            content_parts.append(f"{vuln_type} {evidence}")

    # Add target URL as context
    target = scan_result.get("target", "")
    if target:
        content_parts.append(f"Target: {target}")

    # Join all content
    combined_content = " ".join(content_parts)

    # Fallback if no content extracted
    if not combined_content.strip():
        combined_content = "web scan no vulnerabilities"

    return combined_content.lower()


def analyze_web(scan_result):
    """
    Run AI analysis on web scan results.
    Uses TF-IDF vectorizer + RandomForest classifier.
    Returns dict with prediction and confidence.
    """
    model = get_web_model()
    vectorizer = get_web_vectorizer()

    if model is None:
        return {
            "error": "Web model not available",
            "prediction": "unknown",
            "confidence": 0.0
        }

    if vectorizer is None:
        return {
            "error": "Web vectorizer not available",
            "prediction": "unknown",
            "confidence": 0.0
        }

    try:
        # Extract text content from scan
        content = extract_web_content(scan_result)

        # Vectorize content
        features = vectorizer.transform([content])

        # Run prediction
        prediction = model.predict(features)[0]

        # Get probability if available
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 1.0

        # Map prediction (assuming: 0=safe/normal, 1=vulnerable/at-risk)
        # This mapping depends on your training labels
        prediction_label = "vulnerable" if prediction == 1 else "safe"

        return {
            "prediction": prediction_label,
            "confidence": round(confidence, 3),
            "content_length": len(content),
            "model_type": "RandomForest + TF-IDF"
        }

    except Exception as e:
        logger.error(f"Web AI analysis failed: {str(e)}")
        return {
            "error": str(e),
            "prediction": "error",
            "confidence": 0.0
        }
