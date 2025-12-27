import streamlit as st
import pandas as pd
from llm_helper import generate_fmea_with_llm

st.set_page_config(
    page_title="CT Scan Risk Analyzer",
    layout="wide"
)

st.title("Medical Device Risk Analyzer – CT Scan")
st.caption("LLM-assisted Failure Mode and Effects Analysis (FMEA)")

# -----------------------------
# INIT TABLE
# -----------------------------
if "fmea_df" not in st.session_state:
    st.session_state.fmea_df = pd.DataFrame(
        columns=[
            "Component",
            "Failure Mode",
            "Effect of Failure",
            "Potential Cause",
            "Current Controls",
            "Severity (S)",
            "Occurrence (O)",
            "Detectability (D)",
            "RPN"
        ]
    )

if "ai_failure_mode" not in st.session_state:
    st.session_state.ai_failure_mode = ""
    st.session_state.ai_effect = ""
    st.session_state.ai_cause = ""
    st.session_state.ai_controls = ""

# -----------------------------
# ADD NEW ROW FORM
# -----------------------------
st.subheader("Add New FMEA Entry")

# --- AI ASSIST SECTION (OUTSIDE FORM) ---
use_ai = st.checkbox("Use AI to generate failure analysis")

component = st.text_input(
    "Component",
    placeholder="e.g. X-ray tube, gantry rotation system"
)

if use_ai and component:
    if st.button("Generate with AI"):
        with st.spinner("Generating FMEA using AI..."):
            ai_text = generate_fmea_with_llm(component)
            lines = ai_text.split("\n")

            for line in lines:
                if line.startswith("Failure Mode:"):
                    st.session_state.ai_failure_mode = line.replace(
                        "Failure Mode:", ""
                    ).strip()
                elif line.startswith("Effect of Failure:"):
                    st.session_state.ai_effect = line.replace(
                        "Effect of Failure:", ""
                    ).strip()
                elif line.startswith("Potential Cause:"):
                    st.session_state.ai_cause = line.replace(
                        "Potential Cause:", ""
                    ).strip()
                elif line.startswith("Current Controls:"):
                    st.session_state.ai_controls = line.replace(
                        "Current Controls:", ""
                    ).strip()

            st.success("AI-generated fields populated. Please review before submitting.")

# --- FORM (ONLY FOR SUBMITTING DATA) ---
with st.form("fmea_form"):
    failure_mode = st.text_input(
        "Failure Mode",
        value=st.session_state.ai_failure_mode
    )

    effect = st.text_input(
        "Effect of Failure",
        value=st.session_state.ai_effect
    )

    cause = st.text_input(
        "Potential Cause",
        value=st.session_state.ai_cause
    )

    controls = st.text_input(
        "Current Controls",
        value=st.session_state.ai_controls
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        S = st.slider("Severity (S)", 1, 10, 5)
    with col2:
        O = st.slider("Occurrence (O)", 1, 5, 3)
    with col3:
        D = st.slider("Detectability (D)", 1, 5, 3)

    submit_entry = st.form_submit_button("Add to FMEA Table")

    if submit_entry:
        RPN = S * O * D

        new_row = {
            "Component": component,
            "Failure Mode": failure_mode,
            "Effect of Failure": effect,
            "Potential Cause": cause,
            "Current Controls": controls,
            "Severity (S)": S,
            "Occurrence (O)": O,
            "Detectability (D)": D,
            "RPN": RPN
        }

        st.session_state.fmea_df = pd.concat(
            [st.session_state.fmea_df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.success("Entry successfully added to FMEA table")

# -----------------------------
# DISPLAY TABLE
# -----------------------------
st.subheader("FMEA Risk Table")

st.dataframe(
    st.session_state.fmea_df,
    use_container_width=True
)

st.subheader("Delete Specific Entry")

if not st.session_state.fmea_df.empty:
    index_to_delete = st.number_input(
        "Select row index to delete",
        min_value=0,
        max_value=len(st.session_state.fmea_df) - 1,
        step=1
    )

    if st.button("Delete Selected Row"):
        st.session_state.fmea_df = st.session_state.fmea_df.drop(index_to_delete).reset_index(drop=True)
        st.success(f"Row {index_to_delete} deleted successfully")
else:
    st.info("No entries available to delete")

# -----------------------------
# DOWNLOAD SECTION
# -----------------------------
st.subheader("Download Results")

csv = st.session_state.fmea_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download FMEA Table (CSV)",
    data=csv,
    file_name="CT_Scan_FMEA_Risk_Analysis.csv",
    mime="text/csv"
)

st.subheader("Table Management")

if st.button("Reset FMEA Table"):
    st.session_state.fmea_df = st.session_state.fmea_df.iloc[0:0]
    st.success("FMEA table has been reset")

# -----------------------------
# RPN INTERPRETATION
# -----------------------------
st.subheader("Risk Interpretation")

if not st.session_state.fmea_df.empty:
    max_rpn = st.session_state.fmea_df["RPN"].max()

    if max_rpn >= 150:
        st.error("High Risk Detected – Immediate Mitigation Required")
    elif max_rpn >= 75:
        st.warning("Medium Risk – Risk Reduction Recommended")
    else:
        st.success("Low Risk – Acceptable Risk Level")
else:
    st.info("No risk data available")