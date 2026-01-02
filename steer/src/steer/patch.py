import wrapt
import sys
import threading
from .core import capture
from .policy import policy_engine

_state = threading.local()

def patch_pydantic_ai():
    targets = [
        ('pydantic_ai.agent', 'Agent'),
        ('pydantic_ai', 'Agent')
    ]
    
    for module_name, class_name in targets:
        try:
            # 1. If module is already loaded, patch the class directly
            if module_name in sys.modules:
                target_mod = sys.modules[module_name]
                if hasattr(target_mod, class_name):
                    target_cls = getattr(target_mod, class_name)
                    wrapt.wrap_function_wrapper(target_cls, 'run_sync', _wrap_run)
                    wrapt.wrap_function_wrapper(target_cls, 'run', _wrap_run)
            
            # 2. Also set up a lazy hook for future imports
            wrapt.patch_function_wrapper(module_name, f'{class_name}.run_sync', _wrap_run)
            wrapt.patch_function_wrapper(module_name, f'{class_name}.run', _wrap_run)
        except Exception:
            continue

def _wrap_run(wrapped, instance, args, kwargs):
    # Re-entrancy guard: skip if we are already inside a Steer interception
    if getattr(_state, 'intercepting', False):
        return wrapped(*args, **kwargs)

    agent_name = getattr(instance, 'name', 'unnamed_agent')
    active_locks = policy_engine.get_locks_for_agent(agent_name)
    
    _state.intercepting = True
    try:
        @capture(name=f"PydanticAI:{agent_name}", Judges=active_locks, tags=[agent_name])
        def execution_proxy(*a, **k):
            return wrapped(*a, **k)

        return execution_proxy(*args, **kwargs)
    finally:
        _state.intercepting = False
