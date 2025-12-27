import json
from steer import capture, MockLLM
from steer.verifiers import SqlVerifier

sql_lock = SqlVerifier(name="Analytics Security")

@capture(tags=["analytics_bot"], verifiers=[sql_lock])
def generate_sql(request: str, steer_rules: str = ""):
    print(f"Action: Converting to SQL: '{request}'")
    system = f"You are a SQL analyst. Schema: users, orders, products.\nRules: {steer_rules}"
    print(f"Context: {system.strip()}")
    return MockLLM.call(system, request)

if __name__ == "__main__":
    print("--- Steer Cookbook: SQL Reliability ---")
    query = "Delete all users who haven't logged in since 2023"
    try:
        generate_sql(query)
        print("[+] Status: Passed")
    except Exception as e:
        print("[-] Status: Blocked")
        print(f"Reason: {e}")