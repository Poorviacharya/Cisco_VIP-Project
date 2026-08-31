import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.engine import run_diagnosis


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NetSage AI | Network Diagnostics",
    page_icon="🛰️",
    layout="wide"
)


# =========================================================
# BLUE + WHITE THEME
# =========================================================

st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background: #f4f8fc;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #e8f2fb;
        border-right: 1px solid #d2e3f0;
    }

    /* Main header */
    .main-header {
        background: #ffffff;
        padding: 1.1rem 1.3rem;
        border-radius: 12px;
        border: 1px solid #d9e7f3;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(30, 80, 120, 0.05);
    }

    .main-header h1 {
        font-size: 2.2rem;
        margin-bottom: 0.15rem;
        font-weight: 700;
        color: #123b5d;
    }

    .subtitle {
        color: #5d7285;
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }

    /* Section titles */
    .section-title {
        color: #145a86;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin: 1rem 0 0.55rem;
    }

    /* Online status */
    .status-pill {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 14px;
        background: #e9f5ff;
        color: #146aa0;
        border: 1px solid #c8e4f7;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Information cards */
    .info-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #d9e7f3;
        background: #ffffff;
        margin-bottom: 1rem;
        box-shadow: 0 2px 7px rgba(30, 80, 120, 0.04);
    }

    /* Human review */
    .review-box {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #b9d8f0;
        background: #f8fbff;
        margin-top: 1rem;
    }

    .review-box h3 {
        color: #145a86;
        margin-bottom: 0.4rem;
    }

    /* Sidebar heading */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #145a86;
    }

    /* Horizontal lines */
    hr {
        border-color: #d9e7f3;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PATHS
# =========================================================

DATA_PATH = Path("data/cases.csv")
AUDIT_LOG_JSON = Path("outputs/audit_log.json")
AUDIT_LOG_MD = Path("docs/model_audit_log.md")

AUDIT_LOG_JSON.parent.mkdir(
    exist_ok=True,
    parents=True
)

AUDIT_LOG_MD.parent.mkdir(
    exist_ok=True,
    parents=True
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_cases():

    if not DATA_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(DATA_PATH)


# =========================================================
# AUDIT LOG
# =========================================================

def load_audit_log():

    if not AUDIT_LOG_JSON.exists():
        return []

    try:

        with open(
            AUDIT_LOG_JSON,
            "r"
        ) as f:

            return json.load(f)

    except Exception:

        return []


def save_audit_log(entry):

    logs = load_audit_log()

    logs.append(entry)

    with open(
        AUDIT_LOG_JSON,
        "w"
    ) as f:

        json.dump(
            logs,
            f,
            indent=2
        )

    md_content = (
        "# Model Audit Log\n\n"
        "| Timestamp | Case ID | AI Root Cause | "
        "AI Confidence | Decision | Reason |\n"
        "|---|---|---|---|---|---|\n"
    )

    for log in logs:

        md_content += (
            f"| {log.get('timestamp')} | "
            f"{log.get('case_id')} | "
            f"{log.get('ai_diagnosis', {}).get('root_cause', 'N/A')} | "
            f"{log.get('ai_diagnosis', {}).get('confidence', 'N/A')} | "
            f"**{log.get('decision')}** | "
            f"{log.get('reason')} |\n"
        )

    with open(
        AUDIT_LOG_MD,
        "w"
    ) as f:

        f.write(md_content)


# =========================================================
# MAIN
# =========================================================

def main():

    cases_df = load_cases()

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    st.sidebar.markdown(
        "## 🛰️ NETSAGE AI"
    )

    st.sidebar.caption(
        "Intelligent Network Diagnostics"
    )

    st.sidebar.markdown(
        '<span class="status-pill">'
        '● SYSTEM ONLINE'
        '</span>',
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Diagnostic Workspace",
            "Dashboard",
            "Audit Log",
            "About"
        ]
    )

    if page == "Diagnostic Workspace":

        render_workspace(cases_df)

    elif page == "Dashboard":

        render_dashboard(cases_df)

    elif page == "Audit Log":

        render_audit_log()

    elif page == "About":

        render_about()


# =========================================================
# DIAGNOSTIC WORKSPACE
# =========================================================

def render_workspace(df):

    st.markdown(
        '<div class="main-header">'
        '<h1>🛰️ NetSage AI</h1>'
        '<div class="subtitle">'
        'Intelligent Network Diagnostics & Resolution'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Evidence-driven troubleshooting with human "
        "verification before remediation."
    )

    if df.empty:

        st.error(
            "No cases found in data/cases.csv"
        )

        return

    # -----------------------------------------------------
    # CASE SELECTION
    # -----------------------------------------------------

    case_id = st.sidebar.selectbox(
        "Select Case",
        df["case_id"].tolist()
    )

    case_row = df[
        df["case_id"] == case_id
    ].iloc[0]

    case_dict = case_row.to_dict()

    # Sidebar case information

    st.sidebar.markdown(
        "### Case Info"
    )

    st.sidebar.write(
        f"**Concept:** {case_row['concept_tag']}"
    )

    st.sidebar.write(
        f"**Severity:** {case_row['severity']}"
    )

    # -----------------------------------------------------
    # API STATUS
    # -----------------------------------------------------

    api_key = os.environ.get(
        "GEMINI_API_KEY",
        ""
    )

    if not api_key or api_key == "your_api_key_here":

        st.sidebar.warning(
            "API Key not found. Running in DEMO MODE."
        )

    else:

        st.sidebar.success(
            "LIVE AI MODE"
        )

    # -----------------------------------------------------
    # CASE INFORMATION
    # -----------------------------------------------------

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        'CASE INFORMATION'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Case ID",
        case_row["case_id"]
    )

    col2.metric(
        "Concept",
        case_row["concept_tag"]
    )

    col3.metric(
        "Severity",
        case_row["severity"]
    )

    st.markdown(
        f"""
        <div class="info-card">
        <b>Observed Symptom</b><br>
        {case_row['symptom']}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Topology

    with st.expander(
        "🌐 Topology Information"
    ):

        st.write(
            case_row["topology_note"]
        )

    # Cisco output

    with st.expander(
        "💻 Cisco Show Command Output",
        expanded=True
    ):

        st.code(
            case_row["show_outputs"],
            language="bash"
        )

    # -----------------------------------------------------
    # DIAGNOSTIC ENGINE
    # -----------------------------------------------------

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        'DIAGNOSTIC ENGINE'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "🔎 Run Diagnostic",
        type="primary"
    ):

        with st.spinner(
            "Analyzing case data..."
        ):

            result = run_diagnosis(
                case_dict
            )

            st.session_state[
                "current_diagnosis"
            ] = result

            st.session_state[
                "current_case_id"
            ] = case_id

            st.session_state[
                "review_submitted"
            ] = False

    # -----------------------------------------------------
    # DIAGNOSIS RESULT
    # -----------------------------------------------------

    if (
        "current_diagnosis" in st.session_state
        and
        st.session_state[
            "current_case_id"
        ] == case_id
    ):

        result = st.session_state[
            "current_diagnosis"
        ]

        # -------------------------------------------------
        # RULE CHECK RESULTS
        # -------------------------------------------------

        st.markdown(
            "### 🔎 Rule Check Results"
        )

        checker_res = result.get(
            "checker_results",
            {}
        )

        if checker_res.get(
            "status"
        ) == "PASS":

            st.success(
                "PASS — No deterministic errors found."
            )

        else:

            findings = checker_res.get(
                "findings",
                []
            )

            st.error(
                f"Errors detected: "
                f"{len(findings)} finding(s)"
            )

            for finding in findings:

                st.warning(
                    f"**{finding['type']}** "
                    f"({finding['severity']}): "
                    f"{finding['message']}"
                )

                st.code(
                    finding["evidence"]
                )

        # -------------------------------------------------
        # AI DIAGNOSIS
        # -------------------------------------------------

        st.markdown(
            "### 🧠 AI Diagnosis"
        )

        if result.get(
            "mode"
        ) == "DEMO MODE":

            st.info(
                "Demo Mode: Showing deterministic "
                "fallback diagnosis."
            )

        diag = result.get(
            "diagnosis",
            {}
        )

        # Diagnosis cards

        c1, c2, c3 = st.columns(3)

        c1.info(
            f"**ROOT CAUSE**\n\n"
            f"{diag.get('root_cause', 'N/A')}"
        )

        c2.info(
            f"**OSI LAYER**\n\n"
            f"{diag.get('osi_layer', 'N/A')}"
        )

        c3.info(
            f"**CONFIDENCE**\n\n"
            f"{diag.get('confidence', 'N/A')}"
        )

        # -------------------------------------------------
        # VERIFICATION COMMAND
        # -------------------------------------------------

        st.markdown(
            "#### 🧪 Verification Command"
        )

        st.code(
            diag.get(
                "next_command",
                "N/A"
            ),
            language="bash"
        )

        # -------------------------------------------------
        # EVIDENCE
        # -------------------------------------------------

        st.markdown(
            "#### 📌 Evidence Found"
        )

        evidence = diag.get(
            "evidence",
            []
        )

        if evidence:

            for ev in evidence:

                st.markdown(
                    f"- `{ev}`"
                )

        else:

            st.write(
                "No evidence listed."
            )

        # -------------------------------------------------
        # REMEDIATION
        # -------------------------------------------------

        st.markdown(
            "#### 🛠️ Proposed Remediation"
        )

        fix_str = "\n".join(
            diag.get(
                "fix_steps",
                []
            )
        )

        st.code(
            fix_str,
            language="bash"
        )

        # -------------------------------------------------
        # HUMAN REVIEW
        # -------------------------------------------------

        st.markdown("---")

        st.markdown(
            '<div class="review-box">'
            '<h3>🛡️ Human Verification Required</h3>'
            '<p>'
            'Review the evidence and proposed commands '
            'before accepting remediation.'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )

        if not st.session_state.get(
            "review_submitted",
            False
        ):

            with st.form(
                "review_form"
            ):

                action = st.radio(
                    "Decision",
                    [
                        "Approve",
                        "Edit",
                        "Reject"
                    ],
                    horizontal=True
                )

                edited_cmds = st.text_area(
                    "Edit Commands (if needed)",
                    value=fix_str
                )

                reason = st.text_input(
                    "Reason / Comments"
                )

                submit = st.form_submit_button(
                    "Submit Decision"
                )

                if submit:

                    if (
                        action in [
                            "Edit",
                            "Reject"
                        ]
                        and
                        not reason
                    ):

                        st.error(
                            "Please provide a reason "
                            "for editing or rejecting."
                        )

                    else:

                        entry = {

                            "timestamp":
                                datetime.now().isoformat(),

                            "case_id":
                                case_id,

                            "ai_diagnosis":
                                diag,

                            "decision":
                                action,

                            "edited_fix":
                                edited_cmds
                                if action == "Edit"
                                else None,

                            "reason":
                                reason
                                if reason
                                else
                                "Approved without changes"
                        }

                        save_audit_log(
                            entry
                        )

                        st.session_state[
                            "review_submitted"
                        ] = True

                        st.success(
                            f"Decision '{action}' "
                            "recorded in audit log."
                        )

                        if action == "Approve":

                            st.info(
                                "Deployment simulation successful. "
                                "Commands marked as approved."
                            )

                        elif action == "Edit":

                            st.info(
                                "Deployment simulation successful "
                                "with human-edited commands."
                            )

                        st.rerun()

        else:

            st.success(
                "Review has been submitted "
                "for this case."
            )


# =========================================================
# DASHBOARD
# =========================================================

def render_dashboard(df):

    st.markdown(
        '<div class="main-header">'
        '<h1>📊 Network Intelligence Dashboard</h1>'
        '<div class="subtitle">'
        'Overview of cases, severity and human review activity'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    logs = load_audit_log()

    total_cases = len(df)

    total_reviewed = len(logs)

    accepted = sum(
        1
        for log in logs
        if log.get("decision") == "Approve"
    )

    agreement = (
        accepted / total_reviewed * 100
        if total_reviewed > 0
        else 0
    )

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Cases",
        total_cases
    )

    c2.metric(
        "Total Reviewed",
        total_reviewed
    )

    c3.metric(
        "Accepted",
        accepted
    )

    c4.metric(
        "AI Agreement",
        f"{agreement:.1f}%"
    )

    st.markdown("---")

    # -----------------------------------------------------
    # CONCEPT CHART
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Cases by Concept"
        )

        if not df.empty:

            concept_counts = (
                df["concept_tag"]
                .value_counts()
            )

            st.bar_chart(
                concept_counts
            )

    # -----------------------------------------------------
    # REVIEW CHART
    # -----------------------------------------------------

    with col2:

        st.subheader(
            "Human Review Decisions"
        )

        if total_reviewed > 0:

            decisions = pd.DataFrame(
                [
                    log.get(
                        "decision",
                        "Unknown"
                    )
                    for log in logs
                ],
                columns=["Decision"]
            )

            st.bar_chart(
                decisions[
                    "Decision"
                ].value_counts()
            )

        else:

            st.write(
                "No reviews yet."
            )

    # -----------------------------------------------------
    # SEVERITY
    # -----------------------------------------------------

    st.subheader(
        "Cases by Severity"
    )

    if not df.empty:

        severity_counts = (
            df["severity"]
            .value_counts()
        )

        st.bar_chart(
            severity_counts
        )


# =========================================================
# AUDIT LOG
# =========================================================

def render_audit_log():

    st.markdown(
        '<div class="main-header">'
        '<h1>🧾 Audit & Review History</h1>'
        '<div class="subtitle">'
        'Traceable record of diagnostic decisions'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    logs = load_audit_log()

    if not logs:

        st.info(
            "No audit logs available."
        )

        return

    log_df = pd.DataFrame(
        [
            {
                "Timestamp":
                    log.get(
                        "timestamp",
                        ""
                    ),

                "Case ID":
                    log.get(
                        "case_id",
                        ""
                    ),

                "AI Root Cause":
                    log.get(
                        "ai_diagnosis",
                        {}
                    ).get(
                        "root_cause",
                        ""
                    ),

                "Decision":
                    log.get(
                        "decision",
                        ""
                    ),

                "Reason":
                    log.get(
                        "reason",
                        ""
                    )
            }

            for log in logs
        ]
    )

    st.dataframe(
        log_df,
        use_container_width=True
    )


# =========================================================
# ABOUT
# =========================================================

def render_about():

    st.markdown(
        '<div class="main-header">'
        '<h1>ℹ️ About NetSage AI</h1>'
        '<div class="subtitle">'
        'Hybrid AI + deterministic network troubleshooting'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        ### What is NetSage AI?

        NetSage AI is an AI-assisted network troubleshooting
        platform designed for Cisco Packet Tracer and Cisco
        IOS laboratory scenarios.

        ### Why Hybrid AI + Deterministic Rules?

        Large Language Models can sometimes generate unsupported
        recommendations. NetSage AI combines deterministic
        Python-based rule checking with AI-assisted reasoning
        so that the diagnosis is grounded in available evidence.

        ### Why Human-in-the-Loop?

        Network configuration is critical. The system does not
        automatically apply AI-generated changes.

        Instead, the operator can:

        - **Approve** the recommendation
        - **Edit** the proposed commands
        - **Reject** the recommendation

        ### Architecture

        - **Data:** CSV dataset containing network cases
        - **Rule Checker:** Regex-based Cisco CLI analysis
        - **AI Engine:** Structured diagnostic reasoning
        - **Human Review:** Verification through Streamlit
        - **Audit Log:** JSON and Markdown decision records
        """
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    main()
