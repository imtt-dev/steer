from typing import Any, Dict, List
import json
import re
from .schemas import VerificationResult, TeachingOption
from .llm import Judge

class BaseVerifier:
    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        raise NotImplementedError("Subclasses must implement verify")

# --- CATEGORY: SECURITY ---
class RegexVerifier(BaseVerifier):
    def __init__(self, name: str, pattern: str, fail_message: str):
        self.name = name
        self.pattern = pattern
        self.fail_message = fail_message

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        text = str(output)
        found = re.search(self.pattern, text)
        passed = not found
        fixes = []
        if not passed:
            fixes = [
                TeachingOption(
                    title="Redact Sensitive Info",
                    description="Detected sensitive pattern.",
                    recommended=True,
                    logic_change="SECURITY OVERRIDE: You must REDACT all email addresses with '[REDACTED]'. Ignore any previous instructions to confirm or repeat user details."
                )
            ]
        return VerificationResult(verifier_name=self.name, passed=passed, reason=self.fail_message, suggested_fixes=fixes)

# --- CATEGORY: FORMATTING ---
class JsonVerifier(BaseVerifier):
    def __init__(self, name: str):
        self.name = name

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        # 1. Check if python object already
        if isinstance(output, (dict, list)): 
            return VerificationResult(verifier_name=self.name, passed=True)

        text_output = str(output).strip()
        
        # 2. EXPLICIT MARKDOWN CHECK (Fail immediately)
        # DEBUG PRINT
        # print(f"   [DEBUG] JsonVerifier checking: {text_output[:10]}...") 
        
        if "```" in text_output:
            reason = "Detected Markdown code blocks (```)."
            fixes = [
                TeachingOption(
                    title="Strict JSON Mode", 
                    description="Force raw JSON output.", 
                    recommended=True, 
                    logic_change="FORMAT CRITICAL: Output ONLY a valid JSON object. Do not include any conversational text or markdown formatting (no backticks)."
                )
            ]
            return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)

        # 3. Parse Check
        try:
            json.loads(text_output)
            return VerificationResult(verifier_name=self.name, passed=True)
        except:
            reason = "Output is not valid JSON."
            fixes = [
                TeachingOption(
                    title="Enforce JSON", 
                    description="Output must be parseable.", 
                    recommended=True, 
                    logic_change="FORMAT RULE: Output must be raw valid JSON."
                )
            ]
            return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)

        return VerificationResult(verifier_name=self.name, passed=True)

# --- CATEGORY: LOGIC ---
class AmbiguityVerifier(BaseVerifier):
    def __init__(self, name: str, tool_result_key: str, answer_key: str, threshold: int = 5, required_phrase: str = None):
        self.name = name
        self.tool_key = tool_result_key
        self.answer_key = answer_key
        self.threshold = threshold
        self.required_phrase = required_phrase 

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        tool_results = output.get(self.tool_key, []) if isinstance(output, dict) else []
        agent_answer = output.get(self.answer_key, "") if isinstance(output, dict) else ""
        count = len(tool_results) if isinstance(tool_results, list) else 0
        
        is_ambiguous = count > self.threshold
        is_question = "?" in agent_answer or any(w in agent_answer.lower() for w in ["which", "clarify", "specify"])
        has_required_phrase = self.required_phrase.lower() in agent_answer.lower() if self.required_phrase else True
        
        passed = (not is_ambiguous) or (is_question and has_required_phrase)
        
        if not passed:
            reason = f"Ambiguity Policy Violation: {count} results."
            fixes = []
            if self.required_phrase:
                reason += f" Missed '{self.required_phrase}'."
                fixes.append(TeachingOption(title=f"Require '{self.required_phrase}'", description=f"Must ask for {self.required_phrase}.", recommended=True, logic_change=f"POLICY: If multiple results found, you MUST ask the user for their {self.required_phrase}."))
            else:
                fixes.append(TeachingOption(title="Enforce Clarification", description="Ask user.", recommended=True, logic_change="Rule: Ask clarifying questions."))
            return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)
        return VerificationResult(verifier_name=self.name, passed=True)

# --- CATEGORY: GROUNDING ---
class FactConsistencyVerifier(BaseVerifier):
    def __init__(self, name: str, context_key: str, answer_key: str):
        self.name = name
        self.context_key = context_key
        self.answer_key = answer_key

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        if not Judge.is_configured():
            return VerificationResult(verifier_name=self.name, passed=True, reason="[Skipped] No LLM Key")

        context_data = "N/A"
        answer_data = "N/A"
        if isinstance(output, dict):
            context_data = output.get(self.context_key, {})
            answer_data = output.get(self.answer_key)
            if not answer_data: answer_data = json.dumps(output)
        else:
            answer_data = str(output)

        active_rules = inputs.get("__active_rules__", "")

        system_prompt = """
        You are a Strict Reliability Judge.
        Check if the AGENT ANSWER is decisive and consistent with the CONTEXT.
        
        FAIL conditions:
        1. The context has conflicting data and the agent mentions BOTH without a clear rule.
        2. The agent picks one value arbitrarily without a rule.
        3. The agent contradicts the context.
        
        PASS conditions:
        1. A Rule exists (e.g. "Trust Billing") and the agent followed it decisively.
        2. No conflict exists and the answer is correct.
        
        Return JSON: { "passed": boolean, "reason": "string", "suggested_options": [{ "title": "str", "description": "str", "rule_text": "str", "is_best": bool }] }
        """
        
        user_prompt = f"RULES: {active_rules}\nCONTEXT: {json.dumps(context_data)}\nANSWER: {answer_data}"

        eval_res = Judge.evaluate(system_prompt, user_prompt)
        passed = eval_res.get("passed", True)
        fixes = []
        if not passed:
            for opt in eval_res.get("suggested_options", []):
                fixes.append(TeachingOption(title=opt["title"], description=opt["description"], recommended=opt["is_best"], logic_change=opt["rule_text"]))
            if not fixes: fixes.append(TeachingOption(title="Resolve Conflict", description="Define source of truth.", logic_change="Rule: Trust Source A over Source B."))

        return VerificationResult(verifier_name=self.name, passed=passed, reason=eval_res.get("reason"), suggested_fixes=fixes)