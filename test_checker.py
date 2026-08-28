import pytest
from src.checker import check_case

def test_admin_down():
    output = "GigabitEthernet0/0.30  192.168.30.1    YES manual administratively down down"
    res = check_case(output)
    assert res["status"] == "ERRORS_DETECTED"
    assert len(res["findings"]) == 1
    assert res["findings"][0]["type"] == "INTERFACE_DOWN"
    assert res["findings"][0]["interface"] == "GigabitEthernet0/0.30"

def test_duplicate_ip():
    output = "%IP-4-DUPADDR: Duplicate address 192.168.1.10 on Vlan1, sourced by 0000.3333.4444"
    res = check_case(output)
    assert res["status"] == "ERRORS_DETECTED"
    assert res["findings"][0]["type"] == "DUPLICATE_IP"
    assert "192.168.1.10" in res["findings"][0]["message"]

def test_clean_output():
    output = "GigabitEthernet0/0.10  192.168.10.1    YES manual up                    up"
    res = check_case(output)
    assert res["status"] == "PASS"
    assert len(res["findings"]) == 0

def test_missing_route():
    output = "Gateway of last resort is not set\nC 192.168.1.0/24 is directly connected"
    res = check_case(output)
    assert res["status"] == "ERRORS_DETECTED"
    assert res["findings"][0]["type"] == "MISSING_DEFAULT_ROUTE"
