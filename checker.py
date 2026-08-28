import re

def check_case(show_output: str) -> dict:
    """
    Deterministic rule checker for Cisco show command outputs.
    Returns structured findings.
    """
    findings = []
    
    # 1. Administratively down interfaces
    admin_down_pattern = re.compile(r'([A-Za-z0-9/\.]+)\s+.*?administratively down', re.IGNORECASE)
    for match in admin_down_pattern.finditer(show_output):
        interface = match.group(1)
        findings.append({
            "type": "INTERFACE_DOWN",
            "interface": interface,
            "severity": "HIGH",
            "message": "Interface is administratively down",
            "evidence": f"{interface} is administratively down"
        })

    # 2. Duplicate IP addresses
    dup_ip_pattern = re.compile(r'%IP-4-DUPADDR.*?Duplicate address (\d+\.\d+\.\d+\.\d+)', re.IGNORECASE)
    for match in dup_ip_pattern.finditer(show_output):
        ip = match.group(1)
        findings.append({
            "type": "DUPLICATE_IP",
            "interface": "Unknown",
            "severity": "HIGH",
            "message": f"Duplicate IP address detected: {ip}",
            "evidence": match.group(0)
        })

    # 3. Native VLAN Mismatch
    native_vlan_pattern = re.compile(r'%CDP-4-NATIVE_VLAN_MISMATCH.*?Native VLAN mismatch discovered on ([A-Za-z0-9/\.]+) \(\d+\), with.*?([A-Za-z0-9/\.]+) \((\d+)\)', re.IGNORECASE)
    for match in native_vlan_pattern.finditer(show_output):
        interface = match.group(1)
        findings.append({
            "type": "NATIVE_VLAN_MISMATCH",
            "interface": interface,
            "severity": "MEDIUM",
            "message": "Native VLAN mismatch detected via CDP",
            "evidence": match.group(0)
        })

    # 4. Missing ip nat inside/outside (Simple detection if NAT is configured but inside/outside is missing)
    if "ip nat" in show_output.lower():
        if "ip nat inside" not in show_output.lower() and "ip nat outside" in show_output.lower():
            findings.append({
                "type": "NAT_MISCONFIG",
                "interface": "Unknown",
                "severity": "HIGH",
                "message": "NAT configured but 'ip nat inside' may be missing",
                "evidence": "Missing 'ip nat inside' configuration"
            })

    # 5. Missing ip helper-address (if dhcp issue)
    if "encapsulation dot1Q" in show_output and "ip helper-address" not in show_output and "ip address" in show_output:
        # Just a heuristic for the specific cases
        findings.append({
            "type": "MISSING_DHCP_RELAY",
            "interface": "Unknown",
            "severity": "HIGH",
            "message": "Subinterface might be missing 'ip helper-address'",
            "evidence": "Missing 'ip helper-address' on interface with dot1Q"
        })

    # 6. Wrong subnet mask / gateway on PC
    if "Default Gateway" in show_output and "0.0.0.0" in show_output:
        pass # Handle specific bad gateways if needed
        
    # PC DNS missing
    if "DNS Servers . . . . . . . . . . . : 0.0.0.0" in show_output:
        findings.append({
            "type": "DNS_MISSING",
            "interface": "Unknown",
            "severity": "HIGH",
            "message": "PC DNS server is not configured (0.0.0.0)",
            "evidence": "DNS Servers . . . . . . . . . . . : 0.0.0.0"
        })

    # ACL deny matches
    acl_deny_pattern = re.compile(r'deny\s+.*?\(\d+\s+matches\)', re.IGNORECASE)
    for match in acl_deny_pattern.finditer(show_output):
        findings.append({
            "type": "ACL_DENY_MATCH",
            "interface": "Unknown",
            "severity": "HIGH",
            "message": "Traffic is being blocked by an ACL deny statement",
            "evidence": match.group(0)
        })
        
    # Gateway of last resort not set
    if "Gateway of last resort is not set" in show_output and "0.0.0.0/0" not in show_output:
        findings.append({
            "type": "MISSING_DEFAULT_ROUTE",
            "interface": "Unknown",
            "severity": "HIGH",
            "message": "Gateway of last resort is not set (Missing default route)",
            "evidence": "Gateway of last resort is not set"
        })
        
    # DHCP Pool Exhausted
    if "Current index        IP address range                    Leased addresses" in show_output:
        lines = show_output.split('\n')
        for line in lines:
            if '-' in line and re.search(r'\d+\s+$', line):
                parts = line.split()
                try:
                    leased = int(parts[-1])
                    if leased >= 250: # arbitrary heuristic
                        findings.append({
                            "type": "DHCP_POOL_EXHAUSTED",
                            "interface": "Unknown",
                            "severity": "HIGH",
                            "message": "DHCP Pool appears to be exhausted or highly utilized",
                            "evidence": line.strip()
                        })
                except:
                    pass

    # Line protocol down
    protocol_down_pattern = re.compile(r'([A-Za-z0-9/\.]+)\s+.*?up\s+down', re.IGNORECASE)
    for match in protocol_down_pattern.finditer(show_output):
        interface = match.group(1)
        findings.append({
            "type": "PROTOCOL_DOWN",
            "interface": interface,
            "severity": "HIGH",
            "message": "Interface is up but line protocol is down",
            "evidence": match.group(0)
        })
        
    status = "ERRORS_DETECTED" if len(findings) > 0 else "PASS"
    
    return {
        "status": status,
        "findings": findings
    }
