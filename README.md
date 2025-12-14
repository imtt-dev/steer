<p align="center">
  <img src="https://raw.githubusercontent.com/imtt-dev/steer/main/assets/steer.png" alt="Steer Logo" width="100">
</p>

# Steer SDK

**Active Reliability Layer for AI Agents.**

Steer is an open-source Python library that intercepts agent failures (hallucinations, bad JSON, PII leaks) and allows you to inject fixes via a local dashboard without changing your code.

[![PyPI version](https://badge.fury.io/py/steer-sdk.svg)](https://badge.fury.io/py/steer-sdk)

## The Problem

When an agent fails in production (e.g., outputs bad JSON), logging the error isn't enough. You usually have to:
1.  Dig through logs to find the prompt.
2.  Edit your prompt template manually.
3.  Redeploy the application.

## The Solution

Steer wraps your agent function. When it detects a failure, it blocks the output and logs it to a local dashboard. You click **"Teach"** to provide a correction (e.g., "Use Strict JSON"), and Steer injects that rule into the agent's context for future runs.

**Visual Workflow:**

![Steer Dashboard](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/dashboard-hero.png)

## Installation

```bash
pip install steer-sdk
```

## Quickstart

Generate the example scripts to see the workflow in action:

```bash
steer init
# Generates 01_structure_guard.py, 02_safety_guard.py, etc.

steer ui
# Starts the local dashboard at http://localhost:8000
```

**Run a demo (Split-screen recommended):**

1.  Run `python 01_structure_guard.py`. It will fail (Blocked).
2.  Go to `http://localhost:8000`. Click **Teach**. Select **"Strict JSON"**.
3.  Run `python 01_structure_guard.py` again. It will succeed.

## Usage

Steer uses a decorator pattern to wrap your existing functions.

```python
from steer import capture
from steer.verifiers import JsonVerifier

# 1. Define Verifiers
json_check = JsonVerifier(name="Strict JSON")

# 2. Decorate your Agent Function
@capture(verifiers=[json_check])
def my_agent(user_input, steer_rules=""):
    
    # 3. Pass 'steer_rules' to your system prompt.
    # Steer populates this argument automatically based on your teaching.
    system_prompt = f"You are a helpful assistant.\n{steer_rules}"
    
    # ... Your LLM call ...
    return llm.call(system_prompt, user_input)
```

## Configuration

The Quickstart demos use a Mock LLM and require **no API keys**.

To use advanced LLM-based verifiers in production, set your environment variables:
```bash
export GEMINI_API_KEY=...
# OR
export OPENAI_API_KEY=...
```

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=imtt-dev/steer&type=date&legend=top-left)](https://www.star-history.com/#imtt-dev/steer&type=date&legend=top-left)