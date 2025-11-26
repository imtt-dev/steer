import functools
import time
import uuid
import json
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, List

from .schemas import Incident, TraceStep, TeachingOption
from .worker import get_worker
from .verifiers import BaseVerifier
from .storage import rulebook 

class VerificationError(Exception):
    """Raised when a verifier blocks execution."""
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
            error_msg = None
            result = None
            trace_steps: List[TraceStep] = []
            
            # 1. Capture User Input
            display_input = ""
            if args and isinstance(args[0], str):
                display_input = args[0]
            elif kwargs:
                display_input = ", ".join([str(v) for v in kwargs.values()])
            else:
                display_input = "No Input"

            trace_steps.append(TraceStep(type="user", title="User Input", content=display_input))
            trace_steps.append(TraceStep(type="agent", title="Reasoning", content=f"Executing {func.__name__}..."))

            try:
                result = func(*args, **kwargs)
                
                # Format Output
                display_output = str(result)
                if isinstance(result, dict):
                    display_output = result.get("final_answer") or result.get("answer") or result.get("response") or str(result)

                trace_steps.append(TraceStep(type="success", title="Output Generated", content=display_output))
            except Exception as e:
                error_msg = str(e)
                trace_steps.append(TraceStep(type="error", title="Runtime Exception", content=f"❌ {error_msg}"))
            
            # --- VERIFICATION LOGIC ---
            detected_failure = None
            verification_label = "Runtime Monitor"
            smart_fixes = [] 

            current_agent = tags[0] if tags and len(tags) > 0 else "default_agent"

            if verifiers and error_msg is None:
                flat_inputs = {}
                if kwargs: flat_inputs.update(kwargs)
                
                active_rules_text = rulebook.get_rules_text(current_agent)
                flat_inputs['__active_rules__'] = active_rules_text
                
                for v in verifiers:
                    v_result = v.verify(flat_inputs, result)
                    
                    if not v_result.passed:
                        trace_steps.append(TraceStep(
                            type="error",
                            title=v_result.verifier_name.upper(),
                            content=f"❌ {v_result.reason}"
                        ))
                        detected_failure = v_result
                        verification_label = v_result.verifier_name
                        smart_fixes = v_result.suggested_fixes 
                        break 
            
            # --- 5. LOGGING (Updated to Log Everything) ---
            is_failure = error_msg is not None or detected_failure is not None
            
            if is_failure:
                log_status = "Active"
                log_title = f"{verification_label} Failure" if detected_failure else "Runtime Error"
                # Generate generic fix if none provided
                if not smart_fixes:
                    smart_fixes = [TeachingOption(title="Suppress", description="Ignore rule.", logic_change="None")]
            else:
                # SUCCESS CASE
                log_status = "Resolved" # Auto-resolved so it doesn't clutter Inbox
                log_title = "Execution Success"
                smart_fixes = []

            incident = Incident(
                title=log_title,
                agent_name=current_agent, 
                status=log_status,
                detection_source="FAST_PATH",
                detection_label=verification_label if detected_failure else "System",
                severity=severity if is_failure else "Low",
                timestamp=start_time,
                trace=trace_steps,
                raw_inputs={'args': args, 'kwargs': kwargs},
                raw_outputs=str(result),
                teaching_options=smart_fixes 
            )
            
            get_worker().submit(incident.model_dump(mode='json'))

            # --- 6. BLOCKING ACTION ---
            if detected_failure and halt_on_failure:
                raise VerificationError(f"Blocked by {verification_label}: {detected_failure.reason}", result)

            if error_msg:
                raise Exception(error_msg)
            return result

        return wrapper
    return decorator