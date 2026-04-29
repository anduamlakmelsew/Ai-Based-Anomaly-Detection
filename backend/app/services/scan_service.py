import logging
from app.models.scan_model import Scan
from app import db, socketio
from app.services.alert_service import create_alert
from datetime import datetime

logger = logging.getLogger(__name__)

# =========================
# 🔥 SCANNER MODULES
# =========================
try:
    from app.scanner.network.port_scan import run_port_scan
    from app.scanner.network.enhanced_port_scan import run_enhanced_port_scan
except ImportError:
    run_port_scan = None
    run_enhanced_port_scan = None

try:
    from app.scanner.network.service_detection import detect_services
except:
    detect_services = None

try:
    from app.scanner.system.service import run_system_scan
except:
    run_system_scan = None

try:
    from app.scanner.web.service import run_web_scan
except:
    run_web_scan = None

# Import fallback scanner
try:
    from app.scanner.fallback_scanner import run_fallback_scan
except:
    run_fallback_scan = None

# Import AI pipeline
try:
    from app.ai.pipeline import analyze_scan
except:
    analyze_scan = None


# =========================
# 🧠 SAFE EMIT
# =========================
def emit_progress(scan, progress, stage="", status="running"):
    try:
        socketio.emit("scan_progress", {
            "scan_id": scan.id,
            "progress": progress,
            "status": status,
            "stage": stage,
            # Provide context so the UI can show which scan is running.
            "target": getattr(scan, "target", None),
            "scan_type": getattr(scan, "scan_type", None),
        })
    except Exception as e:
        logger.warning(f"Socket emit failed: {str(e)}")


# =========================
# 🧠 UPDATE PROGRESS
# =========================
def update_progress(scan, progress, stage=None, status=None):
    scan.progress = progress

    if status:
        scan.status = status

    db.session.commit()

    emit_progress(
        scan,
        progress,
        stage or "",
        scan.status
    )


# =========================
# 🚀 MAIN SCAN FUNCTION (🔥 FIXED)
# =========================
def run_scan(target, scan_type, user_id):
    # =========================
    # 🆕 CREATE SCAN (FIXED)
    # =========================
    scan = Scan(
        target=target,
        scan_type=scan_type,
        status="running",
        progress=0,
        user_id=user_id  # ✅ FIXED CORE ISSUE
    )
    db.session.add(scan)
    db.session.commit()

    emit_progress(scan, 0, "Initializing scan", "running")

    result = {
        "target": target,
        "scan_type": scan_type,
        # Include the DB record id so the frontend can fetch
        # the canonical findings from the database after completion.
        "scan_id": scan.id,
        "open_ports": [],
        "services": [],
        "os_info": {},
        "web_scan": {},
        "vulnerabilities": [],
        "findings": [],
        "risk": {
            "score": 0,
            "level": "LOW",
            "explanation": ""
        }
    }

    try:
        scan_type = scan_type.lower()

        # =========================
        # 🌐 NETWORK SCAN
        # =========================
        if scan_type == "network":

            update_progress(scan, 10, "Scanning network ports")

            # Use enhanced port scan for detailed results
            if run_enhanced_port_scan:
                network_data = run_enhanced_port_scan(target)
                result["open_ports"] = network_data.get("open_ports", [])
                result["services"] = network_data.get("services", [])
                result["findings"] = network_data.get("findings", [])
            elif run_port_scan:
                # Fallback to basic port scan
                ports = run_port_scan(target)
                result["open_ports"] = ports
                result["services"] = []
                result["findings"] = []
            else:
                # Use fallback scanner
                update_progress(scan, 20, "Using fallback network scanner")
                fallback_data = run_fallback_scan(target, "network") if run_fallback_scan else {"open_ports": [], "services": [], "findings": []}
                result.update(fallback_data)

            update_progress(scan, 70, "Analyzing network services")

            if detect_services:
                svc = detect_services(target)

                if isinstance(svc, dict):
                    result["services"] = svc.get("services", [])
                elif isinstance(svc, list):
                    result["services"] = svc

            update_progress(scan, 70, "Network analysis")

        # =========================
        # 🖥 SYSTEM SCAN
        # =========================
        elif scan_type == "system":

            update_progress(scan, 10, "Collecting system data")

            if run_system_scan:
                system_data = run_system_scan(target)

                if isinstance(system_data, dict):
                    result["os_info"] = system_data.get("system_data", {}).get("os_info", {})
                    result["services"] = system_data.get("system_data", {}).get("services", [])
                    result["findings"] = system_data.get("findings", [])
                    # Add system-specific data for better reporting
                    result["system_data"] = system_data.get("system_data", {})
            else:
                # Use fallback scanner
                update_progress(scan, 20, "Using fallback system scanner")
                fallback_data = run_fallback_scan(target, "system") if run_fallback_scan else {"findings": [], "system_data": {}}
                result.update(fallback_data)

            update_progress(scan, 70, "Analyzing system configuration")

        # =========================
        # 🌍 WEB SCAN
        # =========================
        elif scan_type == "web":

            update_progress(scan, 5, "Initializing web scan")

            if run_web_scan:
                update_progress(scan, 20, "Crawling application")

                web_data = run_web_scan(target)

                update_progress(scan, 60, "Running OWASP checks")

                result["web_scan"] = web_data
                result["findings"] = web_data.get("findings", [])
                result["vulnerabilities"] = web_data.get("vulnerabilities", [])
                result["risk"] = web_data.get("risk", {
                    "score": 0,
                    "level": "LOW",
                    "explanation": ""
                })
                # Add web-specific data
                result["total_urls_scanned"] = web_data.get("total_urls_scanned", 0)
            else:
                # Use fallback scanner
                update_progress(scan, 20, "Using fallback web scanner")
                fallback_data = run_fallback_scan(target, "web") if run_fallback_scan else {"findings": [], "risk": {"score": 0, "level": "LOW"}}
                result.update(fallback_data)

            update_progress(scan, 85, "Analyzing vulnerabilities")

        else:
            result["error"] = "Invalid scan type"

        # =========================
        # 🔥 FALLBACK RISK
        # =========================
        if scan_type != "web":
            risk_score = 0

            if len(result["open_ports"]) > 5:
                risk_score += 20

            if len(result["services"]) > 10:
                risk_score += 10

            if len(result["findings"]) > 0:
                risk_score += 30

            level = "LOW"
            if risk_score >= 70:
                level = "CRITICAL"
            elif risk_score >= 50:
                level = "HIGH"
            elif risk_score >= 30:
                level = "MEDIUM"

            result["risk"] = {
                "score": risk_score,
                "level": level,
                "explanation": "Calculated from system/network exposure"
            }

        # =========================
        # 🧠 AI ANALYSIS INTEGRATION (Enhanced with Unified AI Service)
        # =========================
        update_progress(scan, 90, "Running AI analysis")
        
        ai_analysis = None
        if analyze_scan:
            try:
                # Prepare scan data for AI analysis
                scan_data_for_ai = {
                    "target": target,
                    "scan_type": scan_type,
                    "open_ports": result.get("open_ports", []),
                    "services": result.get("services", []),
                    "findings": result.get("findings", []),
                    "risk_score": result.get("risk", {}).get("score", 0),
                    "web_scan": result.get("web_scan", {}),
                    "system_data": result.get("system_data", {}),
                    "duration": result.get("duration", 1.0)
                }
                
                # Pass user_id and scan_id for event storage
                ai_analysis = analyze_scan(scan_type, scan_data_for_ai, user_id=user_id, scan_id=scan.id)
                result["ai_analysis"] = ai_analysis
                
                # Log AI detection results
                risk_level = ai_analysis.get('risk_level', 'UNKNOWN')
                risk_score = ai_analysis.get('risk_score', 0)
                logger.info(f"AI Analysis for scan {scan.id}: Risk={risk_level} (score: {risk_score}, confidence: {ai_analysis.get('confidence', 0):.2f})")
                
            except Exception as e:
                logger.warning(f"AI analysis failed for scan {scan.id}: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
                result["ai_analysis"] = {
                    "error": str(e),
                    "prediction": "error",
                    "confidence": 0.0,
                    "risk_level": "UNKNOWN",
                    "risk_score": 0
                }
        else:
            logger.warning(f"AI pipeline not available for scan {scan.id}")
            result["ai_analysis"] = {
                "prediction": "unavailable",
                "confidence": 0.0,
                "risk_level": "UNKNOWN",
                "risk_score": 0
            }

        # =========================
        # 🚨 AUTO-CREATE ALERTS FOR CRITICAL FINDINGS
        # =========================
        critical_findings = [
            f for f in result.get("findings", [])
            if str(f.get("severity", "")).upper() == "CRITICAL"
        ]

        for f in critical_findings:
            vuln_type = f.get("type", "Critical vulnerability")
            url = f.get("url") or result.get("target")
            message = f"{vuln_type} detected on {url}"

            try:
                create_alert(message=message, severity="critical")
            except Exception as e:
                logger.warning(f"Failed to create alert: {str(e)}")

        # Create AI anomaly alert if anomaly detected with high confidence
        if ai_analysis and ai_analysis.get("prediction") == "anomaly" and ai_analysis.get("confidence", 0) > 0.7:
            try:
                create_alert(
                    message=f"AI anomaly detected on {target} (confidence: {ai_analysis.get('confidence', 0):.1%})",
                    severity="warning"
                )
            except Exception as e:
                logger.warning(f"Failed to create AI alert: {str(e)}")

        # =========================
        # ✅ COMPLETE SCAN
        # =========================
        scan.open_ports = result["open_ports"]
        scan.services = result["services"]
        scan.os_info = result["os_info"]
        scan.vulnerabilities = result["vulnerabilities"]
        scan.findings = result["findings"]
        scan.risk_score = result["risk"]["score"]
        scan.result = result

        update_progress(scan, 100, "Scan completed", "completed")

        # Commit to database before emitting
        try:
            db.session.commit()
            logger.info(f"Scan {scan.id} committed to database")
        except Exception as commit_error:
            logger.error(f"Database commit error: {commit_error}")
            db.session.rollback()

        # ✅ FINAL STEP: EMIT COMPLETION FOR REAL-TIME UPDATES
        socketio.emit("scan_completed", {
            "scan_id": scan.id,
            "target": target,
            "scan_type": scan_type,
            "status": "completed",
            "progress": 100,
            "findings": result.get("findings", []),
            "risk": result.get("risk", {}),
            "timestamp": scan.created_at.isoformat() if scan.created_at else datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Scan error: {str(e)}")

        scan.status = "failed"
        db.session.commit()

        emit_progress(scan, scan.progress, "Scan failed", "failed")

        result["error"] = str(e)

    return result


# =========================
# � HISTORY (READY FOR USER FILTER)
# =========================
def get_scan_history(user_id=None):
    try:
        query = Scan.query

        if user_id:
            query = query.filter_by(user_id=user_id)  # ✅ FILTER BY USER

        scans = query.order_by(Scan.created_at.desc()).all()

        result = []

        for scan in scans:
            data = scan.result or {}
            findings = data.get("findings", [])
            risk = data.get("risk", {
                "score": scan.risk_score,
                "level": "LOW",
                "explanation": "Calculated from stored scan result",
            })

            result.append({
                "id": scan.id,
                "target": scan.target,
                "scan_type": scan.scan_type,
                "status": scan.status,
                "progress": scan.progress,
                "risk": risk,
                "findings": findings,
                "total_findings": len(findings),
                "timestamp": scan.created_at.isoformat(),
            })

        return result

    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return []


# =========================
# 🚀 CELERY ASYNC HELPERS
# =========================

def emit_scan_progress(scan_id, progress, status, stage):
    """
    Emit scan progress via WebSocket (for use from Celery workers).
    This is a standalone function that doesn't require a Scan object.
    """
    try:
        socketio.emit("scan_progress", {
            "scan_id": scan_id,
            "progress": progress,
            "status": status,
            "stage": stage,
        })
    except Exception as e:
        logger.warning(f"Socket emit failed from worker: {str(e)}")


def run_network_scan_task(scan_id, target, user_id, celery_task=None):
    """
    Run network scan from Celery worker.
    Called by the Celery task to execute the actual network scan.
    """
    logger.info(f"[Celery Worker] Running network scan {scan_id} on {target}")
    
    # Update progress
    emit_scan_progress(scan_id, 10, "running", "Scanning network ports")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 10, 'stage': 'Scanning network ports'})
    
    # Import here to ensure Flask app context
    from app.scanner.network.enhanced_port_scan import run_enhanced_port_scan
    from app.scanner.network.service_detection import detect_services
    
    result = {
        "target": target,
        "scan_type": "network",
        "scan_id": scan_id,
        "open_ports": [],
        "services": [],
        "os_info": {},
        "vulnerabilities": [],
        "findings": [],
        "risk": {"score": 0, "level": "LOW", "explanation": ""},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Run port scan
    try:
        if run_enhanced_port_scan:
            network_data = run_enhanced_port_scan(target)
            result["open_ports"] = network_data.get("open_ports", [])
            result["services"] = network_data.get("services", [])
            result["findings"] = network_data.get("findings", [])
    except Exception as e:
        logger.error(f"Network scan error: {e}")
    
    # Service detection
    emit_scan_progress(scan_id, 50, "running", "Analyzing network services")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 50, 'stage': 'Analyzing network services'})
    
    try:
        if detect_services:
            svc = detect_services(target)
            if isinstance(svc, dict):
                result["services"] = svc.get("services", [])
            elif isinstance(svc, list):
                result["services"] = svc
    except Exception as e:
        logger.error(f"Service detection error: {e}")
    
    # Risk calculation
    risk_score = 0
    if len(result["open_ports"]) > 5:
        risk_score += 20
    if len(result["services"]) > 10:
        risk_score += 10
    if len(result["findings"]) > 0:
        risk_score += 30
    
    level = "LOW"
    if risk_score >= 70:
        level = "CRITICAL"
    elif risk_score >= 50:
        level = "HIGH"
    elif risk_score >= 30:
        level = "MEDIUM"
    
    result["risk"] = {
        "score": risk_score,
        "level": level,
        "explanation": f"Found {len(result['open_ports'])} open ports, {len(result['services'])} services, {len(result['findings'])} vulnerabilities"
    }
    
    # AI Analysis
    emit_scan_progress(scan_id, 80, "running", "Running AI analysis")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 80, 'stage': 'Running AI analysis'})
    
    try:
        from app.ai.pipeline import analyze_scan
        if analyze_scan:
            scan_data_for_ai = {
                "target": target,
                "scan_type": "network",
                "open_ports": result.get("open_ports", []),
                "services": result.get("services", []),
                "findings": result.get("findings", []),
                "risk_score": result.get("risk", {}).get("score", 0),
            }
            ai_analysis = analyze_scan("network", scan_data_for_ai, user_id=user_id, scan_id=scan_id)
            result["ai_analysis"] = ai_analysis
    except Exception as e:
        logger.warning(f"AI analysis failed: {e}")
        result["ai_analysis"] = {"error": str(e), "prediction": "error", "confidence": 0.0}
    
    return result


def run_web_scan_task(scan_id, target, user_id, celery_task=None):
    """
    Run web scan from Celery worker.
    Called by the Celery task to execute the actual web scan.
    """
    logger.info(f"[Celery Worker] Running web scan {scan_id} on {target}")
    
    # Update progress
    emit_scan_progress(scan_id, 10, "running", "Initializing web scan")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 10, 'stage': 'Initializing web scan'})
    
    from app.scanner.web.service import run_web_scan
    
    result = {
        "target": target,
        "scan_type": "web",
        "scan_id": scan_id,
        "web_scan": {},
        "vulnerabilities": [],
        "findings": [],
        "risk": {"score": 0, "level": "LOW", "explanation": ""},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        if run_web_scan:
            emit_scan_progress(scan_id, 30, "running", "Crawling application")
            if celery_task:
                celery_task.update_state(state='PROGRESS', meta={'progress': 30, 'stage': 'Crawling application'})
            
            web_data = run_web_scan(target)
            
            emit_scan_progress(scan_id, 60, "running", "Running security checks")
            if celery_task:
                celery_task.update_state(state='PROGRESS', meta={'progress': 60, 'stage': 'Running security checks'})
            
            result["web_scan"] = web_data
            result["findings"] = web_data.get("findings", [])
            result["vulnerabilities"] = web_data.get("vulnerabilities", [])
            result["risk"] = web_data.get("risk", {"score": 0, "level": "LOW"})
            result["total_urls_scanned"] = web_data.get("total_urls_scanned", 0)
    except Exception as e:
        logger.error(f"Web scan error: {e}")
        result["error"] = str(e)
    
    # AI Analysis
    emit_scan_progress(scan_id, 80, "running", "Running AI analysis")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 80, 'stage': 'Running AI analysis'})
    
    try:
        from app.ai.pipeline import analyze_scan
        if analyze_scan:
            scan_data_for_ai = {
                "target": target,
                "scan_type": "web",
                "findings": result.get("findings", []),
                "risk_score": result.get("risk", {}).get("score", 0),
                "web_scan": result.get("web_scan", {}),
            }
            ai_analysis = analyze_scan("web", scan_data_for_ai, user_id=user_id, scan_id=scan_id)
            result["ai_analysis"] = ai_analysis
    except Exception as e:
        logger.warning(f"AI analysis failed: {e}")
        result["ai_analysis"] = {"error": str(e), "prediction": "error", "confidence": 0.0}
    
    return result


def run_system_scan_task(scan_id, target, user_id, celery_task=None):
    """
    Run system scan from Celery worker.
    Called by the Celery task to execute the actual system scan.
    """
    logger.info(f"[Celery Worker] Running system scan {scan_id} on {target}")
    
    # Update progress
    emit_scan_progress(scan_id, 10, "running", "Collecting system data")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 10, 'stage': 'Collecting system data'})
    
    from app.scanner.system.service import run_system_scan
    
    result = {
        "target": target,
        "scan_type": "system",
        "scan_id": scan_id,
        "os_info": {},
        "services": [],
        "findings": [],
        "risk": {"score": 0, "level": "LOW", "explanation": ""},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        if run_system_scan:
            emit_scan_progress(scan_id, 40, "running", "Analyzing system configuration")
            if celery_task:
                celery_task.update_state(state='PROGRESS', meta={'progress': 40, 'stage': 'Analyzing system configuration'})
            
            system_data = run_system_scan(target)
            
            if isinstance(system_data, dict):
                result["os_info"] = system_data.get("system_data", {}).get("os_info", {})
                result["services"] = system_data.get("system_data", {}).get("services", [])
                result["findings"] = system_data.get("findings", [])
                result["system_data"] = system_data.get("system_data", {})
    except Exception as e:
        logger.error(f"System scan error: {e}")
        result["error"] = str(e)
    
    # Risk calculation
    risk_score = 0
    if len(result.get("findings", [])) > 0:
        risk_score = min(30 + len(result["findings"]) * 10, 100)
    
    level = "LOW"
    if risk_score >= 70:
        level = "CRITICAL"
    elif risk_score >= 50:
        level = "HIGH"
    elif risk_score >= 30:
        level = "MEDIUM"
    
    result["risk"] = {
        "score": risk_score,
        "level": level,
        "explanation": f"Found {len(result.get('findings', []))} security issues"
    }
    
    # AI Analysis
    emit_scan_progress(scan_id, 80, "running", "Running AI analysis")
    if celery_task:
        celery_task.update_state(state='PROGRESS', meta={'progress': 80, 'stage': 'Running AI analysis'})
    
    try:
        from app.ai.pipeline import analyze_scan
        if analyze_scan:
            scan_data_for_ai = {
                "target": target,
                "scan_type": "system",
                "findings": result.get("findings", []),
                "risk_score": result.get("risk", {}).get("score", 0),
                "system_data": result.get("system_data", {}),
            }
            ai_analysis = analyze_scan("system", scan_data_for_ai, user_id=user_id, scan_id=scan_id)
            result["ai_analysis"] = ai_analysis
    except Exception as e:
        logger.warning(f"AI analysis failed: {e}")
        result["ai_analysis"] = {"error": str(e), "prediction": "error", "confidence": 0.0}
    
    return result


def get_celery_task_status(celery_task_id: str):
    """
    Get the status of a Celery task by its ID.
    
    Returns:
        dict with task state, progress, and result if available
    """
    from celery.result import AsyncResult
    from app.celery_config import celery_app
    
    result = AsyncResult(celery_task_id, app=celery_app)
    
    response = {
        "celery_task_id": celery_task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
    }
    
    if result.state == 'PROGRESS' and result.info:
        response["progress"] = result.info.get("progress", 0)
        response["stage"] = result.info.get("stage", "")
    
    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = str(result.result)
    
    return response