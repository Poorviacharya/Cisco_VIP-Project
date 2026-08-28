# NetSage AI
**AI-Assisted Cisco Network Troubleshooting with Human-in-the-Loop Verification**

## Problem Statement
Network troubleshooting in Cisco environments often involves combing through extensive show-command outputs. While generative AI can assist, it is prone to hallucination and cannot be blindly trusted to make configuration changes to production or lab networks.

## Objectives
NetSage AI bridges the gap by combining deterministic rule checking (Python regex) with an AI diagnostic engine (LLM). It forces a mandatory **human-in-the-loop** review process before any fix is approved, ensuring safety and accountability. This project is built for the Cisco AICTE Virtual Internship 2026.

## Features
- **Deterministic Rule Checker:** Instantly detects common Cisco CLI faults (e.g., administratively down, native VLAN mismatches).
- **AI Diagnostic Engine:** Parses context and provides a structured JSON diagnosis (Root cause, OSI layer, Confidence, Evidence, Next command, Fix steps).
- **Human-in-the-Loop Gate:** Mandatory review screen allowing users to Approve, Edit, or Reject AI proposals.
- **Audit Logging:** Every decision is recorded to `outputs/audit_log.json` and `docs/model_audit_log.md`.
- **Analytics Dashboard:** Visualizes cases, severities, and AI-human agreement statistics.

## Architecture
Data (cases.csv) -> Rule Checker -> AI Engine (Gemini) -> Structured Diagnosis -> Streamlit UI -> Human Review -> Audit Log

## Folder Structure
```text
NetSage-AI/
├── app.py                   # Main Streamlit UI
├── requirements.txt         # Dependencies
├── README.md                # Project documentation
├── .env.example             # Environment variable template
├── data/
│   └── cases.csv            # 30-case dataset
├── src/
│   ├── checker.py           # Deterministic rule checker
│   └── engine.py            # AI orchestration
├── prompts/
│   └── diagnose_prompt.md   # System prompt for LLM
├── docs/
│   └── model_audit_log.md   # Markdown audit log
├── outputs/
│   └── audit_log.json       # JSON audit log
└── tests/
    └── test_checker.py      # Unit tests for rule checker
```

## Technologies Used
- **Python 3**
- **Streamlit** (Frontend Dashboard)
- **Pandas** (Data manipulation)
- **Google Generative AI (Gemini)** (LLM Diagnostics)
- **Pytest** (Unit testing)

## Installation
1. Clone the repository or extract the project files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Copy `.env.example` to `.env` and add your Gemini API Key.
```bash
GEMINI_API_KEY=your_api_key_here
```
*(If no API key is provided, the application safely defaults to a Deterministic Demo Mode).*

## Running the Application
```bash
streamlit run app.py
```

## Demo Workflow (NET-001)
1. Open the application.
2. Select **NET-001** from the sidebar.
3. Observe the symptom (PC1 cannot reach Server1 in VLAN 30).
4. Click **Run Diagnostic**.
5. The rule checker instantly flags `GigabitEthernet0/0.30` as administratively down.
6. The AI outputs the root cause, OSI Layer (1/2), and safe `no shutdown` commands.
7. Under **HUMAN REVIEW REQUIRED**, the operator reviews the proposed fix.
8. Click **Approve & Deploy Fix** (simulates deployment).
9. Navigate to the **Audit Log** tab to see the decision recorded.
10. Navigate to the **Dashboard** to see updated AI agreement metrics.

## Rule Checker
The checker uses Python regular expressions to scan Cisco show commands. It looks for exact string matches like `%IP-4-DUPADDR`, `administratively down`, and `Native VLAN mismatch` to provide ground truth evidence to the LLM.

## AI Prompt
The prompt forces the LLM to act as a Cisco assistant, reasoning *only* on provided evidence, outputting strictly valid JSON, and mapping the fault to the OSI model.

## Human-in-the-Loop
An AI must not autonomously modify networks. NetSage requires human intervention. You can Approve the exact commands, Edit them (if they are destructive or suboptimal), or Reject them entirely.

## Audit Logging
Records are stored in JSON and Markdown, ensuring traceability of who approved what commands, and whether the AI was correct.

## Testing
Run tests using:
```bash
python -m pytest tests/test_checker.py
```

## Limitations & Future Improvements
- The checker rules currently only cover 10-15 common scenarios. This can be expanded.
- It relies on static show outputs rather than real-time SSH (Paramiko/Netmiko) polling, which would be the next step for a production tool.
