import functools
import inspect
from datetime import datetime, timezone
from typing import Callable, List, Any

from .schemas import Incident, TraceStep, TeachingOption
from .worker import get_worker
from .verifiers import BaseVerifier
from .storage import rulebook 

class VerificationError(Exception):
    def __init__(self, message, result):
        super().__init__(message)
        self.result = result

def capture(
    name: str = "Agent Workflow", 
    verifiers: List[BaseVerifier] = None,
    severity: str = "Medium",
    tags: List[str] = None,
    halt_on_failure: bool = True 
):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now(timezone.utc)
            current_agent = tags[0] if tags and len(tags) > 0 else "default_agent"
            
            # 1. Dependency Injection
            sig = inspect.signature(func)
            if "steer_rules" in sig.parameters:
                if "steer_rules" not in kwargs:
                    active_rules = rulebook.get_rules_text(current_agent)
                    kwargs["steer_rules"] = active_rules

            # 2. Capture Input (Raw String)
            display_input = "-"
            if args:
                display_input = str(args[0])
            elif kwargs:
                clean_kwargs = [str(v) for k, v in kwargs.items() if k != 'steer_rules']
                display_input = ", ".join(clean_kwargs)

            trace_steps: List[TraceStep] = []
            trace_steps.append(TraceStep(type="user", title="User Input", content=display_input))
            trace_steps.append(TraceStep(type="agent", title="Reasoning", content=f"Executing {func.__name__}..."))

            # 3. Execution
            error_msg = None
            result = None
            try:
                result = func(*args, **kwargs)
                display_output = str(result)
                if isinstance(result, dict):
                    display_output = result.get("final_answer") or result.get("answer") or result.get("response") or str(result)
                trace_steps.append(TraceStep(type="success", title="Output Generated", content=display_output))
            except Exception as e:
                error_msg = str(e)
                trace_steps.append(TraceStep(type="error", title="Runtime Exception", content=f"❌ {error_msg}"))
            
            # 4. Verification
            detected_failure = None
            verification_label = "Runtime Monitor"
            smart_fixes = [] 

            if verifiers and error_msg is None:
                flat_inputs = {}
                if kwargs: flat_inputs.update(kwargs)
                flat_inputs['__active_rules__'] = rulebook.get_rules_text(current_agent)
                
                for v in verifiers:
                    v_result = v.verify(flat_inputs, result)
                    if not v_result.passed:
                        # CRITICAL FIX: We set content=str(result) to show the raw bad output
                        trace_steps.append(TraceStep(
                            type="error",
                            title=f"BLOCKED: {v_result.reason}", 
                            content=str(result) 
                        ))
                        detected_failure = v_result
                        verification_label = v_result.verifier_name
                        smart_fixes = v_result.suggested_fixes 
                        break 
            
            # 5. Logging
            is_failure = error_msg is not None or detected_failure is not None
            
            if is_failure:
                log_status = "Active"
                log_title = f"{verification_label} Failure" if detected_failure else "Runtime Error"
                if not smart_fixes:
                    smart_fixes = [TeachingOption(title="Suppress", description="Ignore rule.", logic_change="None")]
            else:
                log_status = "Resolved"
                log_title = "Execution Success"
                smart_fixes = []

            safe_args = [str(a) for a in args]
            safe_kwargs = {k:str(v) for k,v in kwargs.items() if k != 'steer_rules'}

            incident = Incident(
                title=log_title,
                agent_name=current_agent, 
                status=log_status,
                detection_source="FAST_PATH",
                detection_label=verification_label if detected_failure else "System",
                severity=severity if is_failure else "Low",
                timestamp=start_time,
                trace=trace_steps,
                raw_inputs={'args': safe_args, 'kwargs': safe_kwargs},
                raw_outputs=str(result),
                teaching_options=smart_fixes 
            )
            
            get_worker().submit(incident.model_dump(mode='json'))

            if detected_failure and halt_on_failure:
                raise VerificationError(f"Blocked by {verification_label}: {detected_failure.reason}", result)

            if error_msg:
                raise Exception(error_msg)
            return result

        return wrapper
    return decorator