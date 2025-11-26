# ⚡ Steer
### The Active Reliability Layer for AI Agents.

**Stop debugging. Start teaching.**  
Steer is an open-source telemetry and verification SDK designed to catch "Confident Idiot" agents in production before they break trust with your users.

[![PyPI version](https://badge.fury.io/py/steer-sdk.svg)](https://badge.fury.io/py/steer-sdk)

---

## 🛑 The Problem

Agents fail in dangerous ways that standard evaluations miss:
1.  **Strict JSON failures:** Wrapping output in markdown.
2.  **Safety leaks:** Outputting PII despite system prompts.
3.  **Ambiguity:** Guessing "Springfield, IL" when the user didn't specify a state.

**Steer wraps your agent in a Verification Layer that catches these logic, context, and format failures in real-time.**

---
## 🚀 See Steer in Action

The Steer workflow is simple: **Catch → Teach → Fix.**

### 1. Fix Broken JSON
**The Problem:** Agents often wrap JSON in Markdown (```json), breaking your app.
**The Fix:** Steer blocks the bad output. You click "Strict JSON" in the UI. The agent learns.

```text
# Run 1: Failure
[Steer] 🤖 Generating profile...
[Steer] 🚨 BLOCKED: Structure Guard Triggered (Detected Markdown).
[Steer] 👉 Go to 'steer ui' to teach the agent.

# Run 2: Success (After Teaching)
[Steer] 🧠 Context loaded: Rules found! Applying fix...
[Steer] ✅ SUCCESS: Agent output valid JSON.
```

### 2. Prevent Data Leaks
**The Problem:** Agents accidentally output PII (emails/keys) despite system prompts.
**The Fix:** Steer's regex guard halts the execution before data leaves the server.

```text
[Steer] 🤖 Summarizing ticket...
[Steer] 🚨 BLOCKED: PII Shield Triggered (Visible email address).
[Steer] 🛡️ Action Blocked.
```

### 3. Enforce Business Logic
**The Problem:** An agent guesses an ambiguous answer (e.g., "Springfield") instead of asking the user.
**The Fix:** Steer forces the agent to ask clarifying questions when search results are ambiguous.

```text
# Run 1: Failure
[Steer] 🤖 Searching for 'Springfield'...
[Steer] 🚨 BLOCKED: Business Logic Guard (34 results found, expected clarification).

# Run 2: Success (After Teaching)
[Steer] 🧠 Context loaded: Ambiguity rules active.
[Steer] ✅ SUCCESS: Agent asked: "Which state are you interested in?"
```

---

## 🔮 Roadmap: From Verification to Learning

Steer v0.1 provides the "Fast Path" (Runtime Guardrails + Human Teaching).
Steer v0.2+ will introduce the "Slow Path" (Automated Model Improvement).

**Coming Soon:**

*   **Query by Committee:** Automated consensus checks for ambiguous prompts (e.g., asking 3 models and voting on the safest answer).
*   **Automated Fine-Tuning:** A pipeline to turn your accumulated (Incident -> Fix) logs into a fine-tuned model that stops making those mistakes entirely.
*   **CI/CD Integration:** Block Pull Requests if an agent fails a reliability test suite.

---

## 📦 Installation

```bash
pip install steer-sdk
```

## ⚡ Quickstart

The fastest way to see Steer in action is to generate the interactive examples.

### 1. Generate Demos
Run this in your terminal to create 3 example agents:
```bash
steer init
```
*> Created 01_structure_guard.py*
*> Created 02_safety_guard.py*
*> Created 03_logic_guard.py*

### 2. The Workflow (Fail → Teach → Fix)
Steer is designed to be interactive. Try the **Structure Guard** demo:

1.  **Run & Fail:**
    The agent attempts to output JSON but wraps it in Markdown (a common LLM error). Steer blocks it.
    ```bash
    python 01_structure_guard.py
    # 🚨 BLOCKED: Detected Markdown code blocks.
    ```

2.  **Teach:**
    Open the dashboard to see the incident and provide a fix.
    ```bash
    steer ui
    ```
    *   Go to **http://localhost:8000**
    *   Click **Teach** on the active incident.
    *   Select **"Strict JSON Mode"** (or write a custom rule) and click **Save**.

3.  **Run & Succeed:**
    Run the script again. The agent detects the new rule and self-corrects.
    ```bash
    python 01_structure_guard.py
    # 🧠 Context loaded: Rules found! Applying fix...
    # ✅ SUCCESS: Agent output valid JSON.
    ```

## 🛠️ Integration

To add Steer to your own existing agent:

```python
from steer import capture
from steer.verifiers import JsonVerifier

# 1. Define Verifiers
json_check = JsonVerifier(name="Strict JSON")

# 2. Decorate your Agent Function
@capture(verifiers=[json_check])
def my_agent(user_input):
    # Your LLM call here
    return llm_response
```

## 🔑 Configuration (Optional)

The Quickstart demos run locally and require **no API keys**.

To use advanced LLM-based verifiers (like `FactConsistencyVerifier`), set your keys:
```bash
export GEMINI_API_KEY=AIzaSy...
# OR
export OPENAI_API_KEY=sk-...
