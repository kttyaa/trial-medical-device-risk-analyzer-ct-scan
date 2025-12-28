import streamlit as st
import pandas as pd
from llm_helper_qwen import ask_qwen_about_component

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Medical Device Risk Analyzer – CT Scan",
    layout="wide"
)

st.title("Medical Device Risk Analyzer – CT Scan")
st.markdown("""
**LLM-assisted Failure Mode and Effects Analysis (FMEA)**  

**Developed by Group 5**  
- Adonnai Phylosophia Cinta Ngau – 2206060712 
- Kattya Aulia Faharani – 2206030382
- Raisa Shahira Afnan – 2306168971  

Biomedical Artificial Intelligence
""")

# =========================
# SESSION STATE INIT
# =========================
if "fmea_df" not in st.session_state:
    st.session_state.fmea_df = pd.DataFrame(columns=[
        "Component",
        "Failure Mode",
        "Effect of Failure",
        "Potential Cause",
        "Current Controls",
        "Severity (S)",
        "Occurrence (O)",
        "Detectability (D)",
        "RPN"
    ])

if "ai_output" not in st.session_state:
    st.session_state.ai_output = ""

# =========================
# AI ASSISTANT SECTION
# =========================
st.header("AI Assistant 📄")

component_ai = st.text_input(
    "Component (for AI suggestions)",
    placeholder="e.g. X-ray tube, detector array, gantry rotation system"
)

if st.button("Ask AI (Generate Possible Risks)"):
    if component_ai.strip():
        with st.spinner("Generating possible risks..."):
            st.session_state.ai_output = ask_qwen_about_component(component_ai)
    else:
        st.warning("Please enter a component name first.")

if st.session_state.ai_output:
    st.subheader("AI Suggestions")
    st.text_area(
        "AI-generated risk ideas (Copy what you need)",
        st.session_state.ai_output,
        height=320
    )

# =========================
# ADD FMEA ENTRY (MANUAL)
# =========================
st.header("Add New FMEA Entry")

with st.form("add_fmea"):
    col1, col2 = st.columns(2)

    with col1:
        component = st.text_input("Component")
        failure_mode = st.text_input("Failure Mode")
        effect = st.text_input("Effect of Failure")

    with col2:
        cause = st.text_input("Potential Cause")
        controls = st.text_input("Current Controls")

    col3, col4, col5 = st.columns(3)
    with col3:
        S = st.slider("Severity (S)", 1, 10, 5)
    with col4:
        O = st.slider("Occurrence (O)", 1, 10, 5)
    with col5:
        D = st.slider("Detectability (D)", 1, 10, 5)

    submit = st.form_submit_button("Add to FMEA Table")

    if submit:
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

        st.success("FMEA entry added successfully")

# =========================
# DISPLAY TABLE
# =========================
def highlight_rpn(val):
    if val >= 201:
        return "background-color: #f8d7da; color: #721c24;"  # red (critical)
    elif val >= 101:
        return "background-color: #ffe5b4; color: #7a4a00;"  # orange (high)
    elif val >= 51:
        return "background-color: #fff3cd; color: #856404;"  # yellow (moderate)
    else:
        return "background-color: #d4edda; color: #155724;"  # green (low)
        
st.header("FMEA Risk Table")

if not st.session_state.fmea_df.empty:
    styled_df = st.session_state.fmea_df.style.applymap(
        highlight_rpn,
        subset=["RPN"]
    )

    st.dataframe(
        styled_df,
        use_container_width=True
    )
else:
    st.info("No FMEA entries available.")

# =========================
# DELETE ENTRY
# =========================
st.subheader("Delete Entry")

if not st.session_state.fmea_df.empty:
    idx = st.number_input(
        "Row index to delete",
        min_value=0,
        max_value=len(st.session_state.fmea_df) - 1,
        step=1
    )

    if st.button("Delete Selected Row"):
        st.session_state.fmea_df = (
            st.session_state.fmea_df
            .drop(idx)
            .reset_index(drop=True)
        )
        st.success("Entry deleted")

# =========================
# RESET & DOWNLOAD
# =========================
st.subheader("Table Management")

if st.button("Reset FMEA Table"):
    st.session_state.fmea_df = st.session_state.fmea_df.iloc[0:0]
    st.success("FMEA table reset")

csv = st.session_state.fmea_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download FMEA Table (CSV)",
    csv,
    "CT_Scan_FMEA.csv",
    "text/csv"
)

# =========================
# RISK INTERPRETATION
# =========================
st.header("Risk Interpretation 📊")

if not st.session_state.fmea_df.empty:
    critical = (st.session_state.fmea_df["RPN"] >= 201).sum()
    high = (
        (st.session_state.fmea_df["RPN"] >= 101) &
        (st.session_state.fmea_df["RPN"] <= 200)
    ).sum()
    moderate = (
        (st.session_state.fmea_df["RPN"] >= 51) &
        (st.session_state.fmea_df["RPN"] <= 100)
    ).sum()
    low = (st.session_state.fmea_df["RPN"] <= 50).sum()

    if critical > 0:
        st.error(
            f"Critical Risk Detected – "
            f"{critical} Critical, {high} High, {moderate} Moderate, {low} Low"
        )
    elif high > 0:
        st.warning(
            f"High Risk Detected – "
            f"{high} High, {moderate} Moderate, {low} Low"
        )
    elif moderate > 0:
        st.info(
            f"Moderate Risk – "
            f"{moderate} Moderate, {low} Low"
        )
    else:
        st.success(f"Low Risk – {low} Low")
else:
    st.info("No risk data available")
