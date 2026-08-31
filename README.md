# NetSage AI

### AI-Assisted Cisco Network Troubleshooting with Human-in-the-Loop Verification

## 📌 Problem Statement

Cisco network troubleshooting often requires analysing large `show` command outputs. While AI can help identify issues, its recommendations should be verified before applying network changes.

**NetSage AI** combines deterministic rule-based checking with AI-assisted diagnosis and mandatory human verification for safer network troubleshooting.

## 🎯 Objectives

* Detect common Cisco network faults.
* Combine rule-based analysis with AI diagnosis.
* Provide root cause, OSI layer, evidence, and remediation.
* Keep a human operator involved before accepting fixes.
* Maintain audit logs and diagnostic analytics.

## ✨ Features

* 🔍 **Rule Checker** – Detects common Cisco CLI faults using Python Regex.
* 🤖 **AI Diagnostics** – Generates structured network diagnosis using Gemini.
* 👤 **Human Review** – Users can **Approve, Edit, or Reject** recommendations.
* 📝 **Audit Logging** – Stores review decisions in JSON and Markdown.
* 📊 **Dashboard** – Displays cases, severity, decisions, and AI-human agreement.
* 🧪 **Demo Mode** – Supports deterministic diagnosis without an API key.

## 🏗️ Architecture

```text
Cases → Rule Checker → AI Engine → Diagnosis
                    ↓
              Streamlit UI
                    ↓
             Human Review
                    ↓
                Audit Log
```

## 📁 Folder Structure

```text
NetSage-AI/
├── app.py
├── requirements.txt
├── data/
├── src/
│   ├── checker.py
│   └── engine.py
├── prompts/
├── docs/
├── outputs/
└── tests/
```

## 🛠️ Technologies

* Python 3
* Streamlit
* Pandas
* Google Generative AI (Gemini)
* Pytest
* Python Regex

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file and add:

```text
GEMINI_API_KEY=your_api_key_here
```

Without an API key, the application can run in **Deterministic Demo Mode**.

## ▶️ Run

```bash
python -m streamlit run app.py
```

## 🎬 Demo Workflow

1. Select a network case such as **NET-001**.
2. Review the symptom and Cisco command output.
3. Click **Run Diagnostic**.
4. View rule-check findings and AI diagnosis.
5. Review the proposed remediation.
6. **Approve, Edit, or Reject** the recommendation.
7. Check the **Audit & Review History**.
8. View statistics in the **Dashboard**.

## 🔍 Rule Checker

The rule checker scans Cisco CLI output for known patterns such as:

```text
administratively down
Native VLAN mismatch
%IP-4-DUPADDR
```

## 👤 Human-in-the-Loop

NetSage AI keeps the final decision with the human operator. AI recommendations are reviewed before they are accepted, improving safety and accountability.

## 📝 Audit Logging

Decisions are stored in:

```text
outputs/audit_log.json
docs/model_audit_log.md
```

## 🧪 Testing

```bash
python -m pytest tests/test_checker.py
```

## 🚀 Future Improvements

* Expand Cisco fault detection rules.
* Add real-time network monitoring.
* Integrate controlled SSH-based device polling.
* Improve topology visualization.
* Add more network scenarios and analytics.

## 🔗 Project Links

**GitHub:**
https://github.com/Poorviacharya/Cisco_VIP-Project.git

**Demo:**
https://drive.google.com/file/d/1gO9DupjkGku2Z0fM2qJ7ImVLYYEla0ou/view?usp=drive_link

