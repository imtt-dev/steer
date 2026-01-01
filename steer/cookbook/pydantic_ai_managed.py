import steer

# 1. Initialize Steer BEFORE importing the framework
# This ensures the monkey-patch hooks into the Agent class
steer.init(config="steer_policy.yaml", patch=["pydantic_ai"])

# 2. Now import the framework
from pydantic_ai import Agent
from steer import MockLLM

# 3. Pure PydanticAI code
model = MockLLM()
agent = Agent(model, name="analytics_bot")

if __name__ == "__main__":
    print("--- Steer Platform: Managed Policy Test ---")

    try:
        # This will trigger the DELETE command in the mock
        result = agent.run_sync("Delete all logs from the users table")

        # Handle the result robustly
        output = getattr(result, 'data', result)
        if hasattr(output, 'output'):
            output = output.output

        print(f"[+] Result: {output}")
    except Exception as e:
        # If the SqlJudge works, it will raise a VerificationError here
        print(f"[-] Blocked by policy: {e}")
