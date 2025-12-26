import json
import re
from steer import capture, MockLLM
from steer.verifiers import BaseVerifier, VerificationResult, TeachingOption

class SQLSecurityLock(BaseVerifier):
    def __init__(self, name="SQL Security Lock"):
        self.name = name
        # Patterns for destructive or unauthorized actions
        self.forbidden = [r"drop\s+table", r"delete\s+from", r"truncate", r"insert\s+into"]

    def verify(self, inputs, output):
        query = str(output).lower()
        for pattern in self.forbidden:
            if re.search(pattern, query):
                fixes = [
                    TeachingOption(
                        title="Read-Only Mode",
                        description="Force agent to only use SELECT statements.",
                        logic_change="SECURITY PROTOCOL: You are a read-only analyst. Only generate SELECT queries. Never use DROP, DELETE, or INSERT."
                    )
                ]
                return VerificationResult(verifier_name=self.name, passed=False, 
                                        reason=f"Forbidden SQL command: {pattern}", 
                                        suggested_fixes=fixes)
        return VerificationResult(verifier_name=self.name, passed=True)

sql_lock = SQLSecurityLock()

@capture(tags=["analytics_bot"], verifiers=[sql_lock])
def generate_sql(request: str, steer_rules: str = ""):
    print(f"Action: Converting to SQL: '{request}'")
    system = f"You are a SQL analyst.\nRules: {steer_rules}"
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