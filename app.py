import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load env before custom imports
load_dotenv()

from src.engine import run_diagnosis

st.set_page_config(page_title="NetSage AI", page_icon="🔍", layout="wide")

# Paths
DATA_PATH = Path("data/cases.csv")
AUDIT_LOG_JSON = Path("outputs/audit_log.json")
AUDIT_LOG_MD = Path("docs/model_audit_log.md")

# Ensure output directories exist
AUDIT_LOG_JSON.parent.mkdir(exist_ok=True, parents=True)
AUDIT_LOG_MD.parent.mkdir(exist_ok=True, parents=True)

@st.cache_data
def load_cases():
    if not DATA_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(DATA_PATH)

def load_audit_log():
    if not AUDIT_LOG_JSON.exists():
        return []
    try:
        with open(AUDIT_LOG_JSON, "r") as f:
            return json.load(f)
    except:
        return []

def save_audit_log(entry):
    logs = load_audit_log()
    logs.append(entry)
    with open(AUDIT_LOG_JSON, "w") as f:
        json.dump(logs, f, indent=2)
        
    # Also update markdown
    md_content = "# Model Audit Log\n\n| Timestamp | Case ID | AI Root Cause | AI Confidence | Decision | Reason |\n"
    md_content += "|---|---|---|---|---|---|\n"
    for log in logs:
        md_content += f"| {log.get('timestamp')} | {log.get('case_id')} | {log.get('ai_diagnosis', {}).get('root_cause', 'N/A')} | {log.get('ai_diagnosis', {}).get('confidence', 'N/A')} | **{log.get('decision')}** | {log.get('reason')} |\n"
    
    with open(AUDIT_LOG_MD, "w") as f:
        f.write(md_content)

def main():
    cases_df = load_cases()
    
    st.sidebar.title("NETSAGE AI")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Navigation", ["Diagnostic Workspace", "Dashboard", "Audit Log", "About"])
    
    if page == "Diagnostic Workspace":
        render_workspace(cases_df)
    elif page == "Dashboard":
        render_dashboard(cases_df)
    elif page == "Audit Log":
        render_audit_log()
    elif page == "About":
        render_about()

def render_workspace(df):
    st.title("NetSage AI 🔍")
    st.subheader("AI-Assisted Network Troubleshooting")
    st.write("Evidence-driven diagnostics with mandatory human verification.")
    
    if df.empty:
        st.error("No cases found in data/cases.csv")
        return
        
    case_id = st.sidebar.selectbox("Select Case", df["case_id"].tolist())
    
    case_row = df[df["case_id"] == case_id].iloc[0]
    case_dict = case_row.to_dict()
    
    st.sidebar.markdown("### Case Info")
    st.sidebar.write(f"**Concept:** {case_row['concept_tag']}")
    st.sidebar.write(f"**Severity:** {case_row['severity']}")
    
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        st.sidebar.warning("API Key not found. Running in DEMO MODE.")
    else:
        st.sidebar.success("LIVE AI MODE")
        
    st.markdown("---")
    st.markdown("### CASE INFORMATION")
    col1, col2, col3 = st.columns(3)
    col1.metric("Case ID", case_row["case_id"])
    col2.metric("Concept", case_row["concept_tag"])
    col3.metric("Severity", case_row["severity"])
    
    st.markdown(f"**Symptom:** {case_row['symptom']}")
    
    with st.expander("Topology Note"):
        st.write(case_row['topology_note'])
        
    with st.expander("Show Command Output", expanded=True):
        st.code(case_row['show_outputs'], language="bash")
        
    st.markdown("---")
    st.markdown("### DIAGNOSTIC ENGINE")
    
    if st.button("Run Diagnostic", type="primary"):
        with st.spinner("Analyzing case data..."):
            result = run_diagnosis(case_dict)
            st.session_state["current_diagnosis"] = result
            st.session_state["current_case_id"] = case_id
            st.session_state["review_submitted"] = False
            
    if "current_diagnosis" in st.session_state and st.session_state["current_case_id"] == case_id:
        result = st.session_state["current_diagnosis"]
        
        st.markdown("#### RULE CHECK RESULTS")
        checker_res = result.get("checker_results", {})
        
        if checker_res.get("status") == "PASS":
            st.success("PASS: No deterministic errors found.")
        else:
            st.error(f"ERRORS_DETECTED: {len(checker_res.get('findings', []))} findings.")
            for f in checker_res.get("findings", []):
                st.warning(f"**{f['type']}** ({f['severity']}): {f['message']}")
                st.code(f['evidence'])
                
        st.markdown("#### AI DIAGNOSIS")
        if result.get("mode") == "DEMO MODE":
            st.info("Showing deterministic fallback diagnosis (Demo Mode)")
            
        diag = result.get("diagnosis", {})
        
        c1, c2, c3 = st.columns(3)
        c1.info(f"**ROOT CAUSE**\n\n{diag.get('root_cause')}")
        c2.info(f"**OSI LAYER**\n\n{diag.get('osi_layer')}")
        c3.info(f"**CONFIDENCE**\n\n{diag.get('confidence')}")
        
        st.info(f"**NEXT COMMAND:** `{diag.get('next_command')}`")
        
        st.markdown("##### EVIDENCE")
        for ev in diag.get("evidence", []):
            st.markdown(f"- `{ev}`")
            
        st.markdown("##### PROPOSED FIX")
        fix_str = "\n".join(diag.get("fix_steps", []))
        st.code(fix_str, language="bash")
        
        # HUMAN IN THE LOOP
        st.markdown("---")
        st.markdown("### ⚠ HUMAN REVIEW REQUIRED")
        st.write("Review the evidence and proposed commands before accepting remediation.")
        
        if not st.session_state.get("review_submitted", False):
            # Form for review
            with st.form("review_form"):
                action = st.radio("Decision", ["Approve", "Edit", "Reject"], horizontal=True)
                edited_cmds = st.text_area("Edit Commands (if needed)", value=fix_str)
                reason = st.text_input("Reason / Comments")
                submit = st.form_submit_button("Submit Decision")
                
                if submit:
                    if action in ["Edit", "Reject"] and not reason:
                        st.error("Please provide a reason for editing or rejecting.")
                    else:
                        entry = {
                            "timestamp": datetime.now().isoformat(),
                            "case_id": case_id,
                            "ai_diagnosis": diag,
                            "decision": action,
                            "edited_fix": edited_cmds if action == "Edit" else None,
                            "reason": reason if reason else "Approved without changes"
                        }
                        save_audit_log(entry)
                        st.session_state["review_submitted"] = True
                        st.success(f"Decision '{action}' recorded in audit log.")
                        if action == "Approve":
                            st.info("Deployment simulation successful. Commands marked as approved.")
                        elif action == "Edit":
                            st.info("Deployment simulation successful with human-edited commands.")
                        st.rerun()
        else:
            st.success("Review has been submitted for this case.")

def render_dashboard(df):
    st.title("Dashboard")
    
    logs = load_audit_log()
    total_cases = len(df)
    total_reviewed = len(logs)
    
    accepted = sum(1 for log in logs if log["decision"] == "Approve")
    edited = sum(1 for log in logs if log["decision"] == "Edit")
    rejected = sum(1 for log in logs if log["decision"] == "Reject")
    
    agreement = (accepted / total_reviewed * 100) if total_reviewed > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cases", total_cases)
    c2.metric("Total Reviewed", total_reviewed)
    c3.metric("Accepted", accepted)
    c4.metric("AI Agreement", f"{agreement:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cases by Concept")
        concept_counts = df["concept_tag"].value_counts()
        st.bar_chart(concept_counts)
        
    with col2:
        st.subheader("Human Review Decisions")
        if total_reviewed > 0:
            decisions = pd.DataFrame([log["decision"] for log in logs], columns=["Decision"])
            st.bar_chart(decisions["Decision"].value_counts())
        else:
            st.write("No reviews yet.")
            
    st.subheader("Cases by Severity")
    severity_counts = df["severity"].value_counts()
    st.bar_chart(severity_counts)

def render_audit_log():
    st.title("Audit Log")
    logs = load_audit_log()
    
    if not logs:
        st.write("No audit logs available.")
        return
        
    log_df = pd.DataFrame([{
        "Timestamp": log["timestamp"],
        "Case ID": log["case_id"],
        "AI Root Cause": log["ai_diagnosis"].get("root_cause", ""),
        "Decision": log["decision"],
        "Reason": log["reason"]
    } for log in logs])
    
    st.dataframe(log_df, use_container_width=True)

def render_about():
    st.title("About NetSage AI")
    st.markdown("""
    ### What is NetSage AI?
    NetSage AI is an AI-assisted network troubleshooting platform designed for Cisco Packet Tracer / Cisco IOS lab scenarios.
    
    ### Why hybrid AI + deterministic rules?
    LLMs can hallucinate. By combining deterministic Python-based rule checking with generative AI, we ground the AI's diagnosis in hard evidence extracted from the show outputs.
    
    ### Why human-in-the-loop?
    Network configuration is critical. An AI should not autonomously apply changes without human verification. The platform enforces a review gate where the operator can Approve, Edit, or Reject the proposed fix.
    
    ### Architecture
    - **Data**: CSV dataset of network cases.
    - **Rule Checker**: Regex-based analysis of Cisco show commands.
    - **AI Engine**: Constructs a structured prompt and parses JSON responses from the LLM.
    - **Human Review**: Streamlit UI for verification.
    - **Audit Log**: JSON and Markdown logging of all human decisions.
    """)

if __name__ == "__main__":
    main()
