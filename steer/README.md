<p align="center">
  <img src="https://raw.githubusercontent.com/imtt-dev/steer/main/assets/steer.png" alt="Steer Logo" width="100">
</p>

<h1 align="center">Steer</h1>

<p align="center">
  <a href="https://steer-labs.com" target="_blank">steer-labs.com</a>
</p>

<p align="center">
  <strong>The Active Reliability Layer for AI Agents.</strong>
</p>

<p align="center">
  Stop debugging. Start teaching. <br>
  Steer turns runtime hallucinations into permanent fixes instantly.
</p>

<p align="center">
  <a href="https://pypi.org/project/steer-sdk/">
    <img src="https://img.shields.io/pypi/v/steer-sdk?color=0070f3&label=pypi%20package" alt="PyPI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-white" alt="License">
  </a>
  <a href="https://twitter.com/steerlabs">
    <img src="https://img.shields.io/badge/follow-%40steerlabs-1DA1F2?logo=twitter&style=flat" alt="Twitter">
  </a>
</p>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/imtt-dev/steer/main/assets/dashboard-hero.png" alt="Steer Mission Control" width="100%">
</p>
<p align="center">
  <em>Mission Control: Catching hallucinations locally and fixing them with one click.</em>
</p>

---

## The Problem

When an agent fails in production (e.g., outputs bad JSON), logging the error is insufficient. You typically have to:
1. Dig through logs to find the specific prompt.
2. Edit your prompt template manually.
3. Redeploy the application.

## The Solution

Steer wraps your agent function with deterministic **Reality Locks**. When a failure is detected, Steer blocks the output and logs it to a local dashboard. You click **Teach** to provide a correction (e.g., "Use Strict JSON"), and Steer injects that rule into the agent context for future runs without a code change.

## Installation

```bash
pip install steer-sdk
```

## Quickstart

Generate the example scripts to see the workflow in action:

```bash
steer init
# Generates 01_structure_guard.py, 02_safety_guard.py, 03_logic_guard.py, 04_slop_guard.py

steer ui
# Starts the local dashboard at http://localhost:8000
```

## Reality Locks in Action

The Steer workflow follows a simple loop: **Catch → Teach → Fix.**

### 1. Structure Guard (JSON)
**Problem:** Agent wraps JSON in Markdown backticks, breaking your parser.
**Fix:** Block the output and enforce raw JSON formatting.
![Structure Guard Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_json.gif)

### 2. Safety Guard (PII)
**Problem:** Agent accidentally leaks customer emails or internal keys.
**Fix:** Block the response and enforce redaction protocols.
![Safety Guard Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_pii.gif)

### 3. Logic Guard (Ambiguity)
**Problem:** Agent guesses a city (e.g., Springfield, IL) instead of asking for clarification.
**Fix:** Force the agent to ask the user clarifying questions.
![Logic Guard Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_logic.gif)

### 4. Slop Filter (Brand Voice)
**Problem:** Agent uses "AI-voice" (emojis, em dashes, apologies) that signals uncurated slop.
**Fix:** Block LLM fingerprints and enforce a blunt, professional signal.
![Slop Filter Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_slop.gif)

## Cookbook

Explore the `cookbook/` directory for enterprise-grade implementations.

### RAG Reliability
Demonstrates how to enforce strict data schemas and grounding citations in a Retrieval-Augmented Generation (RAG) pipeline.
* **Pydantic Schema Enforcement:** Ensuring the agent always returns a valid, typed data structure.
* **Citation Verification:** Hard-locking the agent to cite its sources, preventing ungrounded claims.

[View RAG Cookbook](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/rag_reliability.py)

## Integration

To add Steer to your own agent, add `steer_rules` to your function arguments. Steer populates this automatically based on your dashboard teaching.

```python
from steer import capture
from steer.verifiers import JsonVerifier

# 1. Define Verifiers
json_check = JsonVerifier(name="Strict JSON")

# 2. Decorate your Agent Function
@capture(verifiers=[json_check])
def my_agent(user_input, steer_rules=""):
    
    # 3. Pass 'steer_rules' to your system prompt.
    system_prompt = f"You are a helpful assistant.\n{steer_rules}"
    
    # ... Your LLM call ...
    return llm.call(system_prompt, user_input)
```

## Data Engine: From Guardrails to Fine-Tuning

Every time a rule is applied or an agent succeeds, Steer logs the interaction. You can export these logs into a standard fine-tuning format (JSONL) compatible with OpenAI and Anthropic.

### Export Training Data
Run this command to convert local logs into a dataset:

```bash
steer export
```

**Output:** `steer_fine_tune.jsonl`

### The Fine-Tuning Workflow
1. **Capture:** Run your agent with Steer. Fix issues in the Dashboard.
2. **Export:** Run `steer export` to generate the dataset.
3. **Train:** Upload the file to your provider to fine-tune a model.
4. **Remove:** Once the model learns the boundaries, you can often remove the guardrails.

## What is the "Confident Idiot" Problem?

The **Confident Idiot** is a failure mode where an LLM generates a factually incorrect or structurally broken response with high probability (confidence). LLMs fail silently and plausibly.

* **Example:** User asks "Weather in Springfield". The agent confidently guesses "Springfield, IL" (ignoring the fact that there are 33 other Springfields in the USA).
* **The Fix:** Steer prevents this by enforcing **Reality Locks** (deterministic checks) that run after generation but before the user sees the response.

[Read the viral discussion on Hacker News.](https://news.ycombinator.com/item?id=46152838)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=imtt-dev/steer&type=date&legend=top-left)](https://www.star-history.com/#imtt-dev/steer&type=date&legend=top-left)
