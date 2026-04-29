import time
from .service_detection import detect_services
from .vulnerability import scan_vulnerabilities


def calculate_risk(vulnerabilities):
    score = 0

    weights = {
        "CRITICAL": 10,
        "HIGH": 7,
        "MEDIUM": 4,
        "LOW": 2,
        "INFO": 1
    }

    for v in vulnerabilities:
        severity = v.get("severity", "INFO").upper()
        score += weights.get(severity, 1)

    if score > 20:
        level = "HIGH"
    elif score > 10:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": score,
        "level": level
    }


def run_network_scan(target):
    start_time = time.time()

    try:
        # -----------------------------
        # 1. Detect services
        # -----------------------------
        result = detect_services(target)

        if not result.get("success"):
            return {
                "target": target,
                "vulnerabilities": [],
                "findings": [],
                "total_urls": 0,
                "total_urls_scanned": 0,
                "risk": {
                    "score": 0,
                    "level": "LOW"
                },
                "error": result.get("error")
            }

        services = result.get("services", [])

        # Calculate duration
        duration = time.time() - start_time

        # Calculate raw metrics for AI analysis
        # Estimate bytes based on protocol handshakes
        total_src_bytes = 0
        total_dst_bytes = 0
        protocol_counts = {"icmp": 0, "tcp": 0, "udp": 0}

        for svc in services:
            port = svc.get("port", 0)
            protocol = svc.get("protocol", "tcp").lower()

            # Count protocols
            if protocol in protocol_counts:
                protocol_counts[protocol] += 1

            # Estimate bytes based on service type (handshake sizes)
            if port in [80, 443, 8080, 8443]:  # HTTP/HTTPS
                total_src_bytes += 1024
                total_dst_bytes += 2048
            elif port == 22:  # SSH
                total_src_bytes += 512
                total_dst_bytes += 1024
            elif port in [21, 23]:  # FTP, Telnet
                total_src_bytes += 256
                total_dst_bytes += 512
            elif port == 53:  # DNS
                total_src_bytes += 128
                total_dst_bytes += 256
            elif port == 25:  # SMTP
                total_src_bytes += 512
                total_dst_bytes += 1024
            else:
                total_src_bytes += 200
                total_dst_bytes += 400

        raw_metrics = {
            "duration_seconds": round(duration, 2),
            "src_bytes": total_src_bytes,
            "dst_bytes": total_dst_bytes,
            "protocol_counts": protocol_counts,
            "service_count": len(services)
        }

        # -----------------------------
        # 2. Vulnerability scan
        # -----------------------------
        vulnerabilities = scan_vulnerabilities(services)

        # -----------------------------
        # 3. Normalize vulnerabilities
        # -----------------------------
        normalized = []
        for v in vulnerabilities:
            normalized.append({
                "type": v.get("type", "Network Issue"),
                "category": v.get("category", "Network"),
                "severity": v.get("severity", "LOW").upper(),
                "url": target,
                "confidence": v.get("confidence", "MEDIUM"),
                "evidence": v.get("evidence", ""),
                "exploits_available": v.get("exploits_available", [])
            })

        # -----------------------------
        # 4. Risk scoring
        # -----------------------------
        risk = calculate_risk(normalized)

        # -----------------------------
        # 5. Final Output (UNIFIED)
        # -----------------------------
        return {
            "target": target,

            "services": services,

            # ✅ unified
            "vulnerabilities": normalized,
            "findings": normalized,

            "total_urls": 0,
            "total_urls_scanned": 0,

            "risk": risk,

            # 🔥 Raw metrics for AI analysis
            "raw_metrics": raw_metrics
        }

    except Exception as e:
        return {
            "target": target,
            "vulnerabilities": [],
            "findings": [],
            "total_urls": 0,
            "total_urls_scanned": 0,
            "risk": {
                "score": 0,
                "level": "LOW"
            },
            "error": str(e),
            "raw_metrics": {
                "duration_seconds": 0,
                "src_bytes": 0,
                "dst_bytes": 0,
                "protocol_counts": {"icmp": 0, "tcp": 0, "udp": 0},
                "service_count": 0
            }
        }