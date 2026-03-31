import nmap

def run_port_scan(target):
    scanner = nmap.PortScanner()

    scanner.scan(target, arguments="-F")

    open_ports = []

    for host in scanner.all_hosts():
        for proto in scanner[host].all_protocols():
            ports = scanner[host][proto].keys()
            for port in ports:
                if scanner[host][proto][port]["state"] == "open":
                    open_ports.append(port)

    return open_ports