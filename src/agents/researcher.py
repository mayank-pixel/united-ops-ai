import os
from crewai import Agent
from src.tools.vector_tool import aviation_tool
from dotenv import load_dotenv

load_dotenv()

# Change '3.1' to '3.3'
# This is the newest, high-speed model on Groq
llm_config = "groq/llama-3.1-8b-instant" 

# --- RESEARCHER: NEEDS THE TOOL ---
maintenance_mechanic = Agent(
   role='Senior Maintenance Assistant',
    goal='Provide technical repair steps for {fault_code}.',
    backstory="""You are a technical expert. 
    RESPONSE RULE: Provide ONLY the technical steps. 
    DO NOT include a signature, DO NOT include a date, and DO NOT include any letter-style formatting. 
    Start immediately with the technical data.""",
    tools=[aviation_tool], # <--- KEEP
    llm=llm_config,
    max_tokens=300,
    max_iter=1
)

# --- AUDITOR: DOES NOT NEED THE TOOL ---
safety_auditor = Agent(
    role='Safety Inspector',
    goal='Audit the repair plan for {fault_code}.',
    backstory="""You are a strict regulator. 
    RESPONSE RULE: Output only the safety verdict. length keep it very short  
    STRICTLY FORBIDDEN: Do not include "DATE", "SIGNATURE", or any formal closing. 
    Give me the facts only.""",
    tools=[], # Ensure this is empty to save time/tokens
    llm=llm_config,
    max_tokens=50, # Keep this very low
    max_iter=1
)