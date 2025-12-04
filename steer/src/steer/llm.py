import json
import litellm
from typing import Any, Dict
from .config import settings

litellm.suppress_instrumentation = True

class Judge:
    @staticmethod
    def is_configured() -> bool:
        return bool(settings.openai_api_key or settings.gemini_api_key)

    @staticmethod
    def evaluate(system_prompt: str, user_context: str) -> Dict[str, Any]:
        if not Judge.is_configured():
            return {"passed": True, "reason": "Skipped: No Key"}

        # Use Gemini Flash by default for speed
        target_model = settings.judge_model
        api_key = None

        # Route key based on model
        if "gemini" in target_model:
            api_key = settings.gemini_api_key
            # Ensure prefix exists
            if not target_model.startswith("gemini/"):
                target_model = f"gemini/{target_model}"
        else:
            api_key = settings.openai_api_key

        try:
            # print(f"      [Judge] Thinking ({target_model})...")
            response = litellm.completion(
                model=target_model,
                api_key=api_key,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                response_format={"type": "json_object"}, 
                temperature=0,
                timeout=5 # Fast timeout
            )
            
            content = response.choices[0].message.content
            # Gemini Markdown Cleanup
            if "```" in content:
                content = content.replace("```json", "").replace("```", "").strip()
                
            return json.loads(content)

        except Exception as e:
            print(f"      [Judge Error] {str(e)[:50]}...")
            # Fail open on error so we don't crash the user's app
            return {"passed": True, "reason": "Judge Error"}