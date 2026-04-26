import streamlit as st
import os
import re
import time
import json
from dotenv import load_dotenv
from src.graph.workflow import create_maintenance_workflow

# Load environment variables
load_dotenv()

# --- 1. INITIALIZE SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] 
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# --- 2. CORE EXECUTION FUNCTION (Original Logic preserved) ---
def run_analysis(user_query, aircraft_type):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.last_error = None

    try:
        with st.status("🤖 Consulting manuals and safety history...", expanded=True) as status:
            app_workflow = create_maintenance_workflow()
            
            # SLIDING WINDOW: Context preservation
            managed_messages = st.session_state.chat_history[-3:] 
            
            initial_input = {
                "messages": managed_messages,
                "aircraft_model": aircraft_type,
                "fault_code": user_query,
                "technical_steps": "",
                "safety_warnings": "",
                "is_safety_cleared": False
            }
            
            final_result = app_workflow.invoke(initial_input)
            status.update(label="Analysis Complete!", state="complete")

        # --- OUTPUT CLEANING ---
        tech_raw = final_result.get("technical_steps", "No data found.")
        safety_raw = final_result.get("safety_warnings", "No data found.")
        tech_clean = tech_raw.split("</function>")[-1].strip()
        
        if "{" in safety_raw and "findings" in safety_raw:
            try:
                start, end = safety_raw.find("{"), safety_raw.rfind("}") + 1
                json_data = json.loads(safety_raw[start:end])
                safety_clean = f"**Status:** {json_data.get('test_result', 'N/A')} | **Risk:** {json_data.get('risk_assessment', 'N/A')}\n\n**Findings:** {json_data.get('findings', [''])[0]}"
            except:
                safety_clean = safety_raw.split("</function>")[-1].strip()
        else:
            safety_clean = safety_raw.split("</function>")[-1].strip()

        combined = f"### 🛠️ Repair Steps\n{tech_clean}\n\n---\n### 🛡️ Safety Audit\n{safety_clean}"
        st.session_state.chat_history.append({"role": "assistant", "content": combined})

    except Exception as e:
        error_msg = str(e)
        if "rate_limit_exceeded" in error_msg.lower():
            wait_match = re.search(r"try again in (\d+\.?\d*)s", error_msg)
            wait_time = wait_match.group(1) if wait_match else "10"
            st.session_state.last_error = f"⚠️ **Groq Limit:** Please wait {wait_time}s before your next request."
        else:
            st.session_state.last_error = f"🚨 **System Error:** {error_msg}"
    
    st.rerun()

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="AeroIntel Engine", page_icon="✈️", layout="wide")

# --- 4. TOP SECTION: BRANDING & SYSTEM INFO ---
st.title("✈️ AeroIntel: Agentic Maintenance Engine")

# This is the info block you requested to explain what the app is doing
st.info("""
**What is this system doing?** This is an autonomous **Multi-Agent RAG** (Retrieval-Augmented Generation) engine. When a fault is entered, it triggers a specialized workflow:
1. **Researcher Agent:** Performs a semantic search across FAA Technical Handbooks via a FAISS Vector Database.
2. **Technical Analyst:** Synthesizes the raw manual data into a step-by-step repair procedure.
3. **Safety Auditor:** Conducts a final audit to ensure all steps comply with standard aviation safety protocols.
""")

st.markdown("---")

# --- 5. CONFIG & SAMPLES (Front and Center) ---
col_cfg, col_samples = st.columns([1, 2])

with col_cfg:
    st.subheader("⚙️ System Configuration")
    aircraft = st.selectbox("Current Aircraft Model", ["Boeing 737-800", "Boeing 777-200", "Airbus A320"])
    
    # Enhanced question help (The "three dots" functionality)
    with st.expander("💡 How to enhance your technical query"):
        st.write("""
        Include these details for higher precision:
        * **Component:** (e.g., 'Hydraulic Pump')
        * **Observation:** (e.g., 'pressure fluctuations')
        * **Environment:** (e.g., 'during ground test')
        """)

with col_samples:
    st.subheader("📋 Select a Sample Fault")
    c1, c2, c3 = st.columns(3)
    samples = {"737": "Hydraulic leakage in left engine.", "777": "Fuel imbalance cross-feed valve.", "Gen": "Stabilizer skin corrosion."}
    
    with c1:
        if st.button("🔧 737 Hydraulic Leak"): run_analysis(samples["737"], aircraft)
    with c2:
        if st.button("⛽ 777 Fuel Imbalance"): run_analysis(samples["777"], aircraft)
    with c3:
        if st.button("🛠️ Stabilizer Corrosion"): run_analysis(samples["Gen"], aircraft)

st.divider()

# --- 6. PERSISTENT ERROR DISPLAY ---
if st.session_state.last_error:
    st.error(st.session_state.last_error)
    if st.button("Clear Notification"):
        st.session_state.last_error = None
        st.rerun()

# --- 7. CHAT HISTORY DISPLAY ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. MANUAL INPUT ---
user_query = st.chat_input("Enter a fault code or ask a follow-up...")
if user_query:
    run_analysis(user_query, aircraft)