print("🔄 DEBUG: Starting to load nodes.py...")

from crewai import Task, Crew
print("🔄 DEBUG: CrewAI imported")

from src.agents.researcher import maintenance_mechanic, safety_auditor
print("🔄 DEBUG: Agents imported successfully")

from src.graph.state import AgentState
print("🔄 DEBUG: State imported")

def research_and_audit_node(state: AgentState):
    print(f"🚀 Node Execution Started for: {state['fault_code']}")
    
    research_task = Task(
        description=(
            f"Research the technical repair steps for fault: {state['fault_code']} "
            f"on aircraft {state['aircraft_model']}. Use the Airframe Handbook."
        ),
        expected_output="A detailed step-by-step repair guide with torque and pressure specs.",
        agent=maintenance_mechanic
    )

    safety_task = Task(
        description=(
            f"Verify the proposed repair steps for {state['fault_code']} "
            "against FAA regulations in the General Handbook. Check for AOG risks."
        ),
        expected_output="A safety clearance report. It MUST include the word 'CLEAR' if the plan is safe.",
        agent=safety_auditor,
        context=[research_task] 
    )

    maintenance_crew = Crew(
        agents=[maintenance_mechanic, safety_auditor],
        tasks=[research_task, safety_task],
        verbose=True
    )

    result = maintenance_crew.kickoff()

    return {
        "technical_steps": research_task.output.raw,
        "safety_warnings": safety_task.output.raw,
        "is_safety_cleared": "CLEAR" in safety_task.output.raw.upper()
    }