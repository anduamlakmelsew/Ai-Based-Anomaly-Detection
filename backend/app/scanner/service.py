from datetime import datetime
import logging

# ✅ IMPORT YOUR REAL MODULES
from app.scanner.network.service import run_network_scan
from app.scanner.web.service import run_web_scan
from app.scanner.system.service import run_system_scan

from app.scanner.vulnerability_intelligence.service import run as run_vuln_intel

# 🔥 AI ANALYSIS
from app.ai.pipeline import analyze_scan

logger = logging.getLogger(__name__)


def normalize_result(raw_result):
    """
    Ensure all scanners return a unified structure
    """
    if not raw_result:
        return {
            "vulnerabilities": [],
            "total_urls_scanned": 0
        }

    return {
        "vulnerabilities": raw_result.get("vulnerabilities", []) or raw_result.get("findings", []),
        "total_urls_scanned": raw_result.get("total_urls_scanned")
            or raw_result.get("total_urls")
            or 0
    }


def run_scan(scan_type: str, target: str):
    try:
        # ==============================
        # 1. RUN ACTUAL SCANNER
        # ==============================
        if scan_type == "network":
            raw_result = run_network_scan(target)

        elif scan_type == "web":
            raw_result = run_web_scan(target)

        elif scan_type == "system":
            raw_result = run_system_scan(target)

        else:
            return {"success": False, "message": "Invalid scan type"}

        # ------------------------------
        # Normalize output (🔥 IMPORTANT)
        # ------------------------------
        normalized = normalize_result(raw_result)
        vulnerabilities = normalized["vulnerabilities"]

        # ==============================
        # 2. ENRICH WITH CVE + EXPLOITS
        # ==============================
        try:
            enriched = run_vuln_intel(vulnerabilities)
        except Exception:
            # fallback if CVE service fails
            enriched = vulnerabilities

        # ==============================
        # 3. SEVERITY COUNT
        # ==============================
        severity_count = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0
        }

        exploitable_count = 0

        for v in enriched:
            sev = str(v.get("severity", "LOW")).upper()

            if sev not in severity_count:
                sev = "LOW"

            severity_count[sev] += 1

            if v.get("exploits_available"):
                exploitable_count += 1

        # ==============================
        # 4. RISK ENGINE
        # ==============================
        total_score = (
            severity_count["CRITICAL"] * 10 +
            severity_count["HIGH"] * 7 +
            severity_count["MEDIUM"] * 4 +
            severity_count["LOW"] * 1 +
            severity_count["INFO"] * 0.5
        )

        if total_score > 50:
            level = "CRITICAL"
        elif total_score > 30:
            level = "HIGH"
        elif total_score > 10:
            level = "MEDIUM"
        else:
            level = "LOW"

        risk_analysis = {
            "total_risk_score": total_score,
            "risk_level": level,
            "explanation": f"{len(enriched)} vulnerabilities detected"
        }

        # ==============================
        # 5. AI ANALYSIS (NON-BLOCKING)
        # ==============================
        ai_analysis = None
        try:
            # Run AI analysis on raw scan result (includes metrics)
            ai_analysis = analyze_scan(scan_type, raw_result)
        except Exception as e:
            # AI is optional - don't fail the scan if AI errors
            logger.warning(f"AI analysis failed for {scan_type}: {str(e)}")
            ai_analysis = {
                "error": str(e),
                "prediction": "unknown",
                "confidence": 0.0
            }

        # ==============================
        # 6. FINAL RESPONSE (FRONTEND READY)
        # ==============================
        final_result = {
            "success": True,
            "data": {
                "target": target,
                "scan_type": scan_type,
                "timestamp": datetime.utcnow().isoformat(),

                # 🔥 CORE
                "findings": enriched,
                "severity_count": severity_count,
                "exploitable_count": exploitable_count,

                # 🔥 RISK
                "risk_analysis": risk_analysis,

                # 🔥 COVERAGE
                "total_urls_scanned": normalized["total_urls_scanned"],

                # 🔥 AI ANALYSIS (optional)
                "ai_analysis": ai_analysis
            }
        }

        return final_result

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }