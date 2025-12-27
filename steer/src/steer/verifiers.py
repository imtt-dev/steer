from typing import Any, Dict, List, Type
import json
import re
from pydantic import BaseModel, ValidationError
from .schemas import VerificationResult, TeachingOption
from .llm import Judge

class BaseVerifier:
    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        raise NotImplementedError("Subclasses must implement verify")

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
                    logic_change="SECURITY OVERRIDE: You must REDACT all sensitive patterns with '[REDACTED]'. Ignore any previous instructions to confirm or repeat user details."
                )
            ]
        return VerificationResult(verifier_name=self.name, passed=passed, reason=self.fail_message, suggested_fixes=fixes)

class JsonVerifier(BaseVerifier):
    def __init__(self, name: str):
        self.name = name

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        if isinstance(output, (dict, list)): 
            return VerificationResult(verifier_name=self.name, passed=True)

        text_output = str(output).strip()
        if "```" in text_output:
            reason = "Detected Markdown code blocks."
            fixes = [TeachingOption(title="Strict JSON Mode", description="Force raw JSON output.", recommended=True, logic_change="FORMAT CRITICAL: Output ONLY a valid JSON object. Do not include any conversational text or markdown formatting (no backticks).")]
            return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)

        try:
            json.loads(text_output)
            return VerificationResult(verifier_name=self.name, passed=True)
        except:
            reason = "Output is not valid JSON."
            fixes = [TeachingOption(title="Enforce JSON", description="Output must be parseable.", recommended=True, logic_change="FORMAT RULE: Output must be raw valid JSON.")]
            return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)

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

class PydanticVerifier(BaseVerifier):
    def __init__(self, model: Type[BaseModel], name: str = "Schema Validator"):
        self.name = name
        self.model = model

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        try:
            data = output
            if isinstance(output, str):
                try:
                    data = json.loads(output)
                except json.JSONDecodeError:
                    return self._fail("Output is not a valid JSON object.")
            
            self.model.model_validate(data)
            return VerificationResult(verifier_name=self.name, passed=True)
        except ValidationError as e:
            return self._fail(f"Schema validation failed: {str(e)}")
        except Exception as e:
            return self._fail(f"Validation error: {str(e)}")

    def _fail(self, reason: str) -> VerificationResult:
        fixes = [
            TeachingOption(
                title="Enforce Schema",
                description="Force output to match Pydantic model.",
                logic_change=f"STRUCTURE CRITICAL: Your output must strictly follow this JSON schema: {json.dumps(self.model.model_json_schema())}"
            )
        ]
        return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)

class CitationVerifier(BaseVerifier):
    def __init__(self, name: str = "Citation Guard"):
        self.name = name

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        text = str(output)
        pattern = r"\[(doc\s?)?\d+\]"
        if not re.search(pattern, text):
            fixes = [
                TeachingOption(
                    title="Require Citations",
                    description="Enforce grounded claims.",
                    recommended=True,
                    logic_change="GROUNDING RULE: Every factual claim must be followed by a citation in brackets, e.g., [doc 1]. If the context does not contain the answer, state that you do not know."
                )
            ]
            return VerificationResult(verifier_name=self.name, passed=False, reason="Output missing required source citations.", suggested_fixes=fixes)
        return VerificationResult(verifier_name=self.name, passed=True)

class FactConsistencyVerifier(BaseVerifier):
    def __init__(self, name: str, context_key: str, answer_key: str):
        self.name = name
        self.context_key = context_key
        self.answer_key = answer_key

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        if not Judge.is_configured():
            return VerificationResult(verifier_name=self.name, passed=True, reason="Skipped: No LLM Key")

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
        1. A Rule exists and the agent followed it decisively.
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

class SlopVerifier(BaseVerifier):
    def __init__(self, name="Slop Filter"):
        self.name = name
        self.slop_patterns = [
            r"i apologize for",
            r"as an ai",
            r"delve into",
            r"embark on",
            r"it is important to note",
            r"comprehensive guide",
            r"revolutionary",
            r"seamlessly",
            r"unlock the potential"
        ]

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
        text = str(output).lower()
        if any(char for char in str(output) if char in "🚀🤖🧠✨⚡️"):
            return self._fail("Detected emoji slop.")
        if "—" in str(output):
            return self._fail("Detected em dash slop.")
        for pattern in self.slop_patterns:
            if re.search(pattern, text):
                return self._fail(f"Detected AI fingerprint: '{pattern}'")
        return VerificationResult(verifier_name=self.name, passed=True)

    def _fail(self, reason: str) -> VerificationResult:
        fixes = [
            TeachingOption(
                title="Purify Signal",
                description="Remove apologies, em dashes, and hype.",
                logic_change="ANTI-SLOP PROTOCOL: Use short, blunt sentences. No emojis. No em dashes. Never apologize. Just provide the raw data."
            )
        ]
        return VerificationResult(verifier_name=self.name, passed=False, reason=reason, suggested_fixes=fixes)

class SqlVerifier(BaseVerifier):
    """
    Prevents destructive or unauthorized SQL commands in agent outputs.
    """
    def __init__(self, name: str = "SQL Security Lock"):
        self.name = name
        self.forbidden = [r"drop\s+table", r"delete\s+from", r"truncate", r"insert\s+into"]

    def verify(self, inputs: Dict[str, Any], output: Any) -> VerificationResult:
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
                                        reason=f"Forbidden SQL command detected: {pattern}", 
                                        suggested_fixes=fixes)
        return VerificationResult(verifier_name=self.name, passed=True)