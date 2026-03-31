import ipaddress
import datetime


def validate_target(target):
    """
    Validate IP or network target
    """

    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        try:
            ipaddress.ip_network(target)
            return True
        except ValueError:
            return False


def timestamp():
    """
    Return UTC timestamp
    """

    return datetime.datetime.utcnow().isoformat()


def unique_ports(port_list):
    """
    Remove duplicate ports
    """

    return list(set(port_list))


def service_risk(service):
    """
    Assign risk value for known services
    """

    risky_services = {
        "ftp": 7,
        "telnet": 9,
        "smb": 8,
        "rdp": 7,
        "mysql": 6,
        "postgres": 6
    }

    return risky_services.get(service.lower(), 2)


def normalize_services(services):
    """
    Normalize service names
    """

    normalized = []

    for s in services:
        normalized.append(s.lower())

    return normalized