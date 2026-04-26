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

# --- 2. CORE EXECUTION FUNCTION ---
def run_analysis(user_query, aircraft_type):
    """
    Triggers the Agentic Workflow. 
    Uses a context-aware injection to prevent 'tell me more' errors.
    """
    # 1. Add current query to history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.last_error = None

    try:
        with st.status("🤖 Consulting manuals and history...", expanded=True) as status:
            app_workflow = create_maintenance_workflow()
            
            # SLIDING WINDOW: We send last 3 turns so it remembers what 'it' or 'that' refers to.
            managed_messages = st.session_state.chat_history[-3:] 
            
            initial_input = {
                "messages": managed_messages,
                "aircraft_model": aircraft_type,
                "fault_code": user_query, # The agent uses this + messages history
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
        
        # Safety Parser
        if "{" in safety_raw and "findings" in safety_raw:
            try:
                start, end = safety_raw.find("{"), safety_raw.rfind("}") + 1
                json_data = json.loads(safety_raw[start:end])
                safety_clean = f"**Status:** {json_data.get('test_result', 'N/A')} | **Risk:** {json_data.get('risk_assessment', 'N/A')}\n\n**Findings:** {json_data.get('findings', [''])[0]}"
            except:
                safety_clean = safety_raw.split("</function>")[-1].strip()
        else:
            safety_clean = safety_raw.split("</function>")[-1].strip()

        # Save assistant response
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

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(page_title="United Ops AI", page_icon="✈️", layout="wide")
st.title("✈️ United Airlines: Agentic Maintenance Engine")

# --- 4. PERSISTENT ERROR DISPLAY ---
if st.session_state.last_error:
    st.error(st.session_state.last_error)
    if st.button("Clear Notification"):
        st.session_state.last_error = None
        st.rerun()

# --- 5. ONE-CLICK SAMPLES ---
st.subheader("📋 Select a Sample Fault")
aircraft = st.selectbox("Current Aircraft Model", ["Boeing 737-800", "Boeing 777-200"])
col1, col2, col3 = st.columns(3)
samples = {"737": "Hydraulic leakage in left engine.", "777": "Fuel imbalance cross-feed valve.", "Gen": "Stabilizer skin corrosion."}

with col1:
    if st.button("🔧 737 Hydraulic"): run_analysis(samples["737"], aircraft)
with col2:
    if st.button("⛽ 777 Fuel"): run_analysis(samples["777"], aircraft)
with col3:
    if st.button("🛠️ Corrosion"): run_analysis(samples["Gen"], aircraft)

st.divider()

# --- 6. CHAT HISTORY DISPLAY ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. MANUAL INPUT ---
user_query = st.chat_input("Ask a follow-up (e.g., 'Tell me more in detail') or enter a fault...")
if user_query:
    run_analysis(user_query, aircraft)