# Model Audit Log

| Timestamp | Case ID | AI Root Cause | AI Confidence | Decision | Reason |
|---|---|---|---|---|---|
| 2026-08-28T19:23:59.303975 | NET-002 | Duplicate IP address on the network. | 0.9 | **Edit** | Shutting down Vlan1 is too disruptive. Need to find the source or change IP. |
| 2026-08-28T19:23:59.303975 | NET-004 | Gateway mismatch on client PC. | 0.85 | **Edit** | PC was statically configured, DHCP renew will not work. |
| 2026-08-28T19:23:59.303975 | NET-006 | Missing route to 10.10.10.0/24. | 0.95 | **Reject** | Next-hop 192.168.1.1 is the local router, need the ISP next hop. |
| 2026-08-28T19:23:59.303975 | NET-008 | ACL denying HTTP traffic. | 0.9 | **Edit** | Deleting the entire ACL is a security risk. Modified sequence 10 to permit instead. |
| 2026-08-28T19:23:59.303975 | NET-016 | VTY lines missing SSH. | 0.9 | **Edit** | Transport input all allows telnet which is insecure. Restricted to ssh only. |
