import autogen

def run_cockpit_simulation(fault_description: str):
    """
    Uses AutoGen to simulate a Pilot-to-Engineer conversation.
    """
    config_list = [{"model": "llama3.2", "base_url": "http://localhost:11434", "api_key": "ollama"}]

    pilot = autogen.AssistantAgent(
        name="Pilot",
        llm_config={"config_list": config_list},
        system_message="You are a United Airlines Captain. Report a technical fault clearly."
    )

    maintenance_bot = autogen.UserProxyAgent(
        name="Maintenance_AI",
        human_input_mode="NEVER",
        code_execution_config=False
    )

    # This creates a 'chat' that you can record for your LinkedIn demo!
    pilot.initiate_chat(maintenance_bot, message=f"Tower, we have a code: {fault_description}")