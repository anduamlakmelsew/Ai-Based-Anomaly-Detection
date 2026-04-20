import platform
import subprocess
from ..ssh_client import SSHClient


def get_os_info(ssh=None):
    """
    Collect OS information.
    Works for both local and remote scans.
    """

    # Remote host
    if ssh:
        try:
            system = ssh.execute("uname -s")
            release = ssh.execute("uname -r")
            version = ssh.execute("uname -v")
            architecture = ssh.execute("uname -m")

            # Get additional OS details
            os_details = {}
            
            # Try to get OS distribution info
            try:
                if "Linux" in system:
                    # Check for different Linux distributions
                    distro_files = [
                        "/etc/os-release",
                        "/etc/lsb-release", 
                        "/etc/redhat-release",
                        "/etc/debian_version"
                    ]
                    
                    for distro_file in distro_files:
                        try:
                            content = ssh.execute(f"cat {distro_file} 2>/dev/null")
                            if content and content.strip():
                                os_details[distro_file.split('/')[-1]] = content.strip()
                                break
                        except:
                            continue
                            
                    # Get kernel version details
                    try:
                        kernel_info = ssh.execute("uname -a")
                        os_details["kernel_full"] = kernel_info.strip()
                    except:
                        pass
                        
                elif "Darwin" in system:
                    # macOS specific info
                    try:
                        macos_version = ssh.execute("sw_vers -productVersion")
                        os_details["macos_version"] = macos_version.strip()
                    except:
                        pass
                        
            except Exception as e:
                print(f"Error getting additional OS details: {e}")

            return {
                "system": system.strip(),
                "release": release.strip(),
                "version": version.strip(),
                "architecture": architecture.strip(),
                "details": os_details
            }
            
        except Exception as e:
            print(f"Error getting remote OS info: {e}")
            return {"error": str(e)}

    # Local host
    local_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine()
    }
    
    # Add local OS details
    try:
        if local_info["system"] == "Linux":
            try:
                with open("/etc/os-release", "r") as f:
                    os_release = f.read()
                local_info["details"] = {"os-release": os_release.strip()}
            except:
                try:
                    with open("/etc/lsb-release", "r") as f:
                        lsb_release = f.read()
                    local_info["details"] = {"lsb-release": lsb_release.strip()}
                except:
                    pass
    except Exception as e:
        print(f"Error getting local OS details: {e}")
    
    return local_info


def detect_os_vulnerabilities(os_info):
    """
    Detect OS-specific vulnerabilities and misconfigurations
    """
    findings = []
    
    if not os_info or "error" in os_info:
        return findings
    
    system = os_info.get("system", "").lower()
    release = os_info.get("release", "")
    
    # Check for outdated OS versions
    if system == "linux":
        # Check for very old kernel versions
        try:
            kernel_version = release.split(".")
            if len(kernel_version) >= 2:
                major = int(kernel_version[0])
                minor = int(kernel_version[1])
                
                if major < 4 or (major == 4 and minor < 15):
                    findings.append({
                        "type": "Outdated Kernel Version",
                        "category": "A02: Cryptographic Failures",
                        "severity": "HIGH",
                        "url": "system",
                        "confidence": "HIGH",
                        "evidence": f"Kernel version {release} is outdated and may contain known vulnerabilities",
                        "exploits_available": []
                    })
        except:
            pass
            
    elif system == "darwin":
        # Check for old macOS versions
        try:
            version_parts = release.split(".")
            if len(version_parts) >= 2:
                major = int(version_parts[0])
                minor = int(version_parts[1])
                
                if major < 10 or (major == 10 and minor < 14):
                    findings.append({
                        "type": "Outdated macOS Version",
                        "category": "A02: Cryptographic Failures", 
                        "severity": "MEDIUM",
                        "url": "system",
                        "confidence": "HIGH",
                        "evidence": f"macOS version {release} is outdated and may contain security vulnerabilities",
                        "exploits_available": []
                    })
        except:
            pass
    
    return findings