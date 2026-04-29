"""
Unified AI Pipeline Interface
Provides single entry point for all AI analysis types
"""
import logging
from typing import Dict, Any, Optional

# Legacy pipeline imports (fallback)
try:
    from .network_pipeline import analyze_network
except ImportError:
    analyze_network = None

try:
    from .web_pipeline import analyze_web
except ImportError:
    analyze_web = None

try:
    from .system_pipeline import analyze_system
except ImportError:
    analyze_system = None

# New unified analysis module
try:
    from .unified_analysis import analyze_with_unified_ai, manual_ai_test
except ImportError:
    analyze_with_unified_ai = None
    manual_ai_test = None

logger = logging.getLogger(__name__)


def analyze_scan(scan_type, scan_result, user_id: Optional[int] = None, scan_id: Optional[int] = None):
    """
    Unified interface for AI analysis across all scan types.
    Now uses the unified AI service for enhanced analysis.

    Args:
        scan_type: str - "network", "web", or "system"
        scan_result: dict - Raw scan output from respective scanner
        user_id: int - User who initiated the scan (for event storage)
        scan_id: int - Scan record ID (for event storage)

    Returns:
        dict: AI analysis result with prediction, confidence, and metadata
        Always returns a valid dict even on error (non-blocking)
    """
    scan_type = scan_type.lower().strip()

    # Try unified analysis first (if available)
    if analyze_with_unified_ai and user_id:
        try:
            logger.info(f"[AI] Using unified AI service for {scan_type} scan")
            return analyze_with_unified_ai(scan_type, scan_result, user_id, scan_id)
        except Exception as e:
            logger.error(f"[AI] Unified analysis failed for {scan_type}: {e}, falling back to legacy pipeline")

    # Fallback to legacy pipelines
    try:
        if scan_type == "network" and analyze_network:
            return analyze_network(scan_result)

        elif scan_type == "web" and analyze_web:
            return analyze_web(scan_result)

        elif scan_type == "system" and analyze_system:
            return analyze_system(scan_result)

        else:
            return {
                "error": f"Unknown scan type: {scan_type}",
                "prediction": "unknown",
                "confidence": 0.0
            }

    except Exception as e:
        logger.error(f"AI pipeline error for {scan_type}: {str(e)}")
        return {
            "error": str(e),
            "prediction": "error",
            "confidence": 0.0,
            "scan_type": scan_type
        }


def run_manual_ai_test(user_id: int, network_data=None, system_data=None, web_data=None) -> Dict[str, Any]:
    """
    Run manual AI test from the AI Security Lab.
    
    Args:
        user_id: User running the test
        network_data: Optional network input data
        system_data: Optional system input data
        web_data: Optional web input data
    
    Returns:
        Unified prediction result dictionary
    """
    if manual_ai_test:
        return manual_ai_test(user_id, network_data, system_data, web_data)
    else:
        return {
            "error": "AI test service not available",
            "global_risk_score": 0,
            "global_status": "UNKNOWN"
        }
