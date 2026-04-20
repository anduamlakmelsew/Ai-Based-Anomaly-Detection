import nmap

def run_enhanced_port_scan(target):
    """
    Enhanced port scanner that provides detailed service information
    and security findings for open ports and services.
    """
    scanner = nmap.PortScanner()

    # Use more comprehensive scan for service detection
    scanner.scan(target, arguments="-sV -sC -O --version-intensity 5")

    findings = []
    services = []
    open_ports = []

    for host in scanner.all_hosts():
        for proto in scanner[host].all_protocols():
            ports = scanner[host][proto].keys()
            for port in ports:
                if scanner[host][proto][port]["state"] == "open":
                    open_ports.append(port)
                    
                    # Get service information
                    service_info = scanner[host][proto][port]
                    service = {
                        "host": host,
                        "port": port,
                        "protocol": proto,
                        "state": service_info["state"],
                        "service": service_info.get("name", "unknown"),
                        "version": service_info.get("version", ""),
                        "product": service_info.get("product", ""),
                        "extrainfo": service_info.get("extrainfo", ""),
                        "cpe": service_info.get("cpe", "")
                    }
                    services.append(service)

                    # Generate security findings based on service
                    findings.extend(generate_service_findings(service))

    # Add OS detection findings
    if host in scanner.all_hosts() and 'osmatch' in scanner[host]:
        for osmatch in scanner[host]['osmatch']:
            accuracy = osmatch.get('accuracy', '0')
            try:
                accuracy_int = int(accuracy)
                if accuracy_int > 80:
                    findings.append({
                        "type": "OS Detection",
                        "category": "Information Disclosure",
                        "severity": "LOW",
                        "url": target,
                        "confidence": "HIGH",
                        "evidence": f"OS detected: {osmatch.get('name', 'Unknown')} (Accuracy: {accuracy}%)",
                        "exploits_available": [],
                        "remediation": "Consider masking OS information through network hardening"
                    })
            except (ValueError, TypeError):
                # Skip if accuracy is not a valid number
                pass

    return {
        "open_ports": open_ports,
        "services": services,
        "findings": findings
    }

def generate_service_findings(service):
    """Generate security findings based on detected services"""
    findings = []
    port = service["port"]
    service_name = service["service"].lower()
    version = service.get("version", "").lower()
    
    # Common vulnerable services and versions
    vulnerable_services = {
        "ssh": {
            "ports": [22],
            "vulnerable_versions": ["openssh_7.2", "openssh_7.3", "openssh_7.4"],
            "findings": [
                {
                    "type": "SSH Service Detected",
                    "category": "A05: Security Misconfiguration",
                    "severity": "MEDIUM",
                    "confidence": "HIGH",
                    "evidence": f"SSH service running on port {port}",
                    "remediation": "Ensure SSH is properly configured with key-based authentication and disable password auth if possible"
                }
            ]
        },
        "http": {
            "ports": [80, 8080, 8000, 3000, 5000],
            "findings": [
                {
                    "type": "HTTP Service Detected",
                    "category": "A05: Security Misconfiguration", 
                    "severity": "LOW",
                    "confidence": "HIGH",
                    "evidence": f"HTTP service running on port {port}",
                    "remediation": "Consider using HTTPS and implementing proper security headers"
                }
            ]
        },
        "mysql": {
            "ports": [3306],
            "findings": [
                {
                    "type": "MySQL Database Service",
                    "category": "A02: Cryptographic Failures",
                    "severity": "HIGH",
                    "confidence": "HIGH", 
                    "evidence": f"MySQL service exposed on port {port}",
                    "remediation": "Restrict database access to trusted networks only and use strong authentication"
                }
            ]
        },
        "postgresql": {
            "ports": [5432],
            "findings": [
                {
                    "type": "PostgreSQL Database Service",
                    "category": "A02: Cryptographic Failures",
                    "severity": "HIGH",
                    "confidence": "HIGH", 
                    "evidence": f"PostgreSQL service exposed on port {port}",
                    "remediation": "Restrict database access to trusted networks only and implement proper access controls"
                }
            ]
        },
        "ftp": {
            "ports": [21],
            "findings": [
                {
                    "type": "FTP Service Detected",
                    "category": "A05: Security Misconfiguration",
                    "severity": "MEDIUM",
                    "confidence": "HIGH",
                    "evidence": f"FTP service running on port {port}",
                    "remediation": "Use SFTP instead of FTP and disable anonymous access"
                }
            ]
        },
        "telnet": {
            "ports": [23],
            "findings": [
                {
                    "type": "Telnet Service Detected",
                    "category": "A02: Cryptographic Failures",
                    "severity": "CRITICAL",
                    "confidence": "HIGH",
                    "evidence": f"Telnet service running on port {port} - unencrypted communication",
                    "remediation": "Disable Telnet immediately and use SSH instead"
                }
            ]
        },
        "rdp": {
            "ports": [3389],
            "findings": [
                {
                    "type": "RDP Service Detected",
                    "category": "A05: Security Misconfiguration", 
                    "severity": "HIGH",
                    "confidence": "HIGH", 
                    "evidence": f"RDP service exposed on port {port}",
                    "remediation": "Restrict RDP access to trusted IPs and use strong authentication"
                }
            ]
        },
        "vnc": {
            "ports": [5900, 5901],
            "findings": [
                {
                    "type": "VNC Service Detected",
                    "category": "A05: Security Misconfiguration",
                    "severity": "HIGH",
                    "confidence": "HIGH",
                    "evidence": f"VNC service exposed on port {port}",
                    "remediation": "Restrict VNC access to trusted networks and use strong passwords"
                }
            ]
        }
    }
    
    # Check for privileged ports
    privileged_ports = [1, 7, 8, 9, 11, 13, 15, 17, 19, 20, 21, 22, 23, 25, 37, 53, 79, 111, 123, 139, 389, 445, 512, 513, 514, 1023, 1433, 1521, 1900, 2000, 2049, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151, 3152, 3153, 3154, 3155, 3156, 3157, 3158, 3159, 3160, 3161, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3349, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3358, 3359, 3360, 3361, 3362, 3363, 3364, 3365, 3366, 3367, 3368, 3369, 3370, 3371, 3372, 3373, 3374, 3375, 3376, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3385, 3386, 3387, 3388, 3389, 3390, 3391, 3392, 3393, 3394, 3395, 3396, 3397, 3398, 3399, 3400]
    
    if port in privileged_ports:
        findings.append({
            "type": "Privileged Port Open",
            "category": "A05: Security Misconfiguration",
            "severity": "LOW",
            "url": f"{service['host']}:{port}",
            "confidence": "HIGH",
            "evidence": f"Privileged port {port} is open with service {service_name}",
            "remediation": "Ensure this service is required and properly secured"
        })
    
    # Check for specific service vulnerabilities
    if service_name in vulnerable_services:
        service_config = vulnerable_services[service_name]
        if port in service_config["ports"]:
            for base_finding in service_config["findings"]:
                finding = base_finding.copy()
                finding["url"] = f"{service['host']}:{port}"
                findings.append(finding)
    
    # Check for vulnerable versions
    vulnerable_versions = service_config.get("vulnerable_versions", [])
    if vulnerable_versions and any(vuln_ver in version for vuln_ver in vulnerable_versions):
        finding["severity"] = "HIGH"
        finding["evidence"] += f" - Potentially vulnerable version: {service.get('version', 'Unknown')}"
        
    return findings
