"""
Unified AI Analysis Module
Integrates the unified security ML service with the scanning pipeline
and stores results in the database.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app import db
from app.models.ai_detection_event_model import AIDetectionEvent

# Import the unified AI service
from app.ai.services.unified_security_ml_service import (
    get_service,
    predict_network,
    predict_system,
    predict_web,
    predict_all
)

logger = logging.getLogger(__name__)


def store_ai_detection_event(
    user_id: int,
    source_type: str,
    target: str,
    prediction_result: Dict[str, Any],
    scan_id: Optional[int] = None,
    input_data: Optional[Dict] = None
) -> AIDetectionEvent:
    """
    Store AI detection event in database.
    
    Args:
        user_id: User who initiated the scan/analysis
        source_type: network, system, web, or unified
        target: Target being analyzed
        prediction_result: AI prediction result dictionary
        scan_id: Optional reference to scan record
        input_data: Optional raw input data (sanitized)
    
    Returns:
        AIDetectionEvent: Created event record
    """
    try:
        # Extract risk information
        risk_level = "LOW"
        risk_score = 0.0
        global_status = None
        
        # Handle unified result
        if "global_status" in prediction_result:
            global_status = prediction_result.get("global_status")
            risk_level = global_status if global_status else "LOW"
            risk_score = prediction_result.get("global_risk_score", 0)
        
        # Extract individual predictions
        network_pred = prediction_result.get("network")
        system_pred = prediction_result.get("system")
        web_pred = prediction_result.get("web")
        
        # Determine attack type from predictions
        attack_type = None
        attack_category = None
        vulnerability_type = None
        confidence = 0.0
        attack_probability = None
        anomaly_score = None
        
        if network_pred:
            attack_type = "network_attack" if network_pred.get("is_attack") else "normal"
            attack_category = network_pred.get("attack_category")
            attack_probability = network_pred.get("attack_probability")
            confidence = max(confidence, network_pred.get("attack_confidence", 0))
        
        if system_pred:
            attack_type = system_pred.get("risk_level", attack_type)
            anomaly_score = system_pred.get("anomaly_score")
            confidence = max(confidence, system_pred.get("risk_score", 0) / 100.0)
        
        if web_pred:
            if web_pred.get("is_vulnerable"):
                attack_type = "web_vulnerability"
                vulnerability_type = web_pred.get("vulnerability_type")
            confidence = max(confidence, web_pred.get("confidence", 0))
        
        # Create event record
        event = AIDetectionEvent(
            scan_id=scan_id,
            source_type=source_type,
            target=target,
            risk_level=risk_level,
            risk_score=risk_score,
            global_status=global_status,
            attack_type=attack_type,
            attack_category=attack_category,
            vulnerability_type=vulnerability_type,
            confidence=confidence,
            attack_probability=attack_probability,
            anomaly_score=anomaly_score,
            network_prediction=network_pred,
            system_prediction=system_pred,
            web_prediction=web_pred,
            unified_result=prediction_result,
            input_data=input_data,
            model_status=prediction_result.get("model_status", "ok"),
            degraded_mode=prediction_result.get("degraded_mode", False),
            missing_inputs=prediction_result.get("missing_inputs", {}),
            user_id=user_id
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"[AI] Stored detection event #{event.id}: {source_type} on {target} = {risk_level}")
        
        return event
        
    except Exception as e:
        logger.error(f"[AI] Failed to store detection event: {e}")
        db.session.rollback()
        raise


def analyze_with_unified_ai(
    scan_type: str,
    scan_data: Dict[str, Any],
    user_id: int,
    scan_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyze scan data using the unified AI service.
    
    Args:
        scan_type: network, system, or web
        scan_data: Raw scan results
        user_id: User who initiated the scan
        scan_id: Optional scan record ID
    
    Returns:
        Dict with AI analysis results
    """
    target = scan_data.get("target", "unknown")
    
    try:
        # Prepare input bundle based on scan type
        input_bundle = {}
        
        if scan_type == "network":
            # Extract network features from scan data
            network_input = _extract_network_features(scan_data)
            input_bundle["network"] = network_input
            
        elif scan_type == "system":
            # Extract system features from scan data
            system_input = _extract_system_features(scan_data)
            input_bundle["system"] = system_input
            
        elif scan_type == "web":
            # Extract web features from scan data
            web_input = _extract_web_features(scan_data)
            input_bundle["web"] = web_input
        
        # Run unified prediction
        unified_result = predict_all(input_bundle)
        
        # Convert to dictionary
        result_dict = unified_result.to_dict()
        
        # Store in database
        store_ai_detection_event(
            user_id=user_id,
            source_type=scan_type,
            target=target,
            prediction_result=result_dict,
            scan_id=scan_id,
            input_data=input_bundle
        )
        
        # Return simplified analysis result
        return {
            "prediction": "anomaly" if result_dict.get("global_status") in ["CRITICAL", "HIGH"] else "normal",
            "confidence": result_dict.get("global_risk_score", 0) / 100.0,
            "risk_level": result_dict.get("global_status", "LOW"),
            "risk_score": result_dict.get("global_risk_score", 0),
            "degraded_mode": result_dict.get("degraded_mode", False),
            "details": result_dict
        }
        
    except Exception as e:
        logger.error(f"[AI] Unified analysis failed for {scan_type}: {e}")
        
        # Return error result but don't crash
        return {
            "prediction": "error",
            "confidence": 0.0,
            "risk_level": "UNKNOWN",
            "risk_score": 0,
            "error": str(e),
            "details": {}
        }


def _extract_network_features(scan_data: Dict) -> Dict[str, Any]:
    """Extract network features from scan data for AI analysis."""
    open_ports = scan_data.get("open_ports", [])
    services = scan_data.get("services", [])
    findings = scan_data.get("findings", [])
    
    return {
        "duration": scan_data.get("duration", 1.0),
        "src_bytes": scan_data.get("src_bytes", 1000),
        "dst_bytes": scan_data.get("dst_bytes", 2000),
        "packet_count": len(open_ports) * 10,
        "protocol": "tcp",
        "src_port": 54321,
        "dst_port": open_ports[0] if open_ports else 80,
        "syn_flag": 1,
        "ack_flag": 1,
        "rst_flag": 0,
        "fin_flag": 0
    }


def _extract_system_features(scan_data: Dict) -> Dict[str, Any]:
    """Extract system features from scan data for AI analysis."""
    system_data = scan_data.get("system_data", {})
    services = scan_data.get("services", [])
    findings = scan_data.get("findings", [])
    
    return {
        "cpu_usage": system_data.get("cpu_usage", 50.0),
        "memory_usage": system_data.get("memory_usage", 50.0),
        "disk_usage": system_data.get("disk_usage", 50.0),
        "open_ports": len(scan_data.get("open_ports", [])),
        "process_count": system_data.get("process_count", 100),
        "suspicious_processes": len([f for f in findings if "process" in f.get("type", "").lower()]),
        "user_count": system_data.get("user_count", 1),
        "admin_count": system_data.get("admin_count", 1),
        "service_count": len(services),
        "exposed_services": len([s for s in services if s.get("port") in [21, 23, 3306, 5432]]),
        "total_vulns": len(findings),
        "critical_vulns": len([f for f in findings if f.get("severity") == "CRITICAL"]),
        "high_vulns": len([f for f in findings if f.get("severity") == "HIGH"]),
        "firewall_enabled": system_data.get("firewall_enabled", 1)
    }


def _extract_web_features(scan_data: Dict) -> Dict[str, Any]:
    """Extract web features from scan data for AI analysis."""
    web_scan = scan_data.get("web_scan", {})
    findings = scan_data.get("findings", [])
    
    # Get payload/response from web scan or findings
    payload = ""
    for finding in findings:
        if "payload" in finding:
            payload = finding.get("payload", "")
            break
    
    if not payload and web_scan:
        # Try to get from web scan data
        payloads = web_scan.get("payloads", [])
        if payloads:
            payload = payloads[0]
    
    return {
        "url": scan_data.get("target", "/"),
        "payload": payload,
        "method": "GET",
        "headers": {},
        "status_code": 200
    }


def manual_ai_test(
    user_id: int,
    network_data: Optional[Dict] = None,
    system_data: Optional[Dict] = None,
    web_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Run manual AI test from the AI Security Lab.
    
    Args:
        user_id: User running the test
        network_data: Optional network input data
        system_data: Optional system input data
        web_data: Optional web input data
    
    Returns:
        Unified prediction result
    """
    input_bundle = {}
    target_parts = []
    
    if network_data:
        input_bundle["network"] = network_data
        target_parts.append("network")
    
    if system_data:
        input_bundle["system"] = system_data
        target_parts.append("system")
    
    if web_data:
        input_bundle["web"] = web_data
        target_parts.append("web")
    
    target = "manual_test_" + "_".join(target_parts) if target_parts else "manual_test"
    
    # Run unified prediction
    unified_result = predict_all(input_bundle)
    result_dict = unified_result.to_dict()
    
    # Store in database
    store_ai_detection_event(
        user_id=user_id,
        source_type="unified",
        target=target,
        prediction_result=result_dict,
        scan_id=None,
        input_data=input_bundle
    )
    
    return result_dict
