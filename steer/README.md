<p align="center">
  <img src="https://raw.githubusercontent.com/imtt-dev/steer/main/assets/steer.png" alt="Steer Logo" width="120">
</p>

<p align="center">
  <b><font size="7">Steer</font></b>
</p>

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

## The Problem: The Agent Lobotomy

Most developers are forced to "lobotomize" their agents in production (stripping autonomy, hardcoding paths, and removing tools) because they cannot verify probabilistic output. When an agent fails, simply logging the error is insufficient. You are usually forced to:
1. Dig through logs to find the specific prompt.
2. Edit your prompt template manually.
3. Redeploy the application to fix a single edge case.

## The Solution: Reality Locks

Steer wraps your agent functions with deterministic **Reality Locks**. When a failure is detected, Steer blocks the output and logs it to a local dashboard. You provide a correction via the UI, and Steer injects that rule into the agent context at runtime without a code change.

**Stop lobotomizing your agents.** Reality Locks allow you to keep the intelligence while the code enforces the boundaries.

## Operational Resilience

Steer is architected for mission-critical production environments:
* **Low-Latency Sidecar:** Steer adds <5ms latency per verification. It runs in-process with your agent, requiring no external network hops.
* **Fail-Safe Architecture:** Steer is designed to fail-safe. If the library encounters an internal error, it defaults to your configured policy to ensure system uptime.
* **Stateless by Design:** Steer uses local memory and file-based logging, making it compatible with serverless (Lambda) and containerized (K8s) environments.

## Privacy & Security

* **Zero Data Exfiltration:** Steer is Local-First. Traces, prompts, and tool-outputs never leave your infrastructure. Verification happens entirely on your compute.
* **Audit-Ready Logging:** Every blocked response is logged with a deterministic reason code for compliance and security audits.
* **Deterministic Integrity:** Steer uses hard-coded assertions (Regex, AST, Pydantic), eliminating the risk of "Verifier Hallucination" common in LLM-as-a-judge setups.

## Installation

```bash
pip install steer-sdk
```

## Quickstart

Generate the example scripts to see the workflow in action.

**Note: Ensure you run all commands from the same directory so the local database remains synced.**

```bash
steer init
# Generates 01_structure_guard.py, 02_safety_guard.py, 03_logic_guard.py, 04_slop_guard.py

steer ui
# Starts the local dashboard at http://localhost:8000
```

**Run a demo (from the same folder):**

1. **Fail:** Run `python 01_structure_guard.py`. Output will show `[-] Status: Blocked`.
2. **Teach:** Go to `http://localhost:8000`. Click the incident, select **Teach**, and save the rule.
3. **Fix:** Run `python 01_structure_guard.py` again. Output will show `[+] Status: Passed`.

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
Enforce strict data schemas and grounding citations in a RAG pipeline.
* [View RAG Cookbook](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/rag_reliability.py)

### SQL Security
Enforce read-only protocols and prevent destructive SQL injections in analytics agents.
* [View SQL Cookbook](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/sql_reliability.py)

## Integration

Add `steer_rules` to your function arguments. Steer populates this automatically via dependency injection.

```python
from steer import capture
from steer.verifiers import JsonVerifier

# 1. Define Reality Locks
json_check = JsonVerifier(name="Strict JSON")

# 2. Decorate your Agent Function
@capture(verifiers=[json_check])
def my_agent(user_input, steer_rules=""):
    # Rules are injected automatically at runtime. 
    # Update agent behavior from the dashboard without a code redeploy.
    system_prompt = f"You are a helpful assistant.\n{steer_rules}"
    
    # ... Your LLM call ...
    return llm.call(system_prompt, user_input)
```

## Data Engine: Synthetic Data for DPO

Steer transforms runtime failures into a competitive asset. By capturing the delta between a Blocked Response (the hallucination) and the Taught Response (the correction), Steer generates contrastive pairs for Direct Preference Optimization (DPO).

### Export Training Data
Run this command to generate a dataset ready for `trl`, `unsloth`, or OpenAI fine-tuning:

```bash
# Export successful runs for SFT
steer export --format openai

# Export contrastive pairs (Rejected vs Chosen) for DPO
steer export --format dpo
```

**DPO Output Schema:**
```json
{
  "prompt": "Create admin profile for user u-8821",
  "chosen": "{\n  \"id\": \"u-8821\",\n  \"status\": \"active\"\n}",
  "rejected": "```json\n{\n  \"id\": \"u-8821\",\n  \"status\": \"active\"\n}\n```"
}
```

---

## What is the "Confident Idiot" Problem?

The Confident Idiot is a failure mode where an LLM generates a factually incorrect or structurally broken response with high probability (confidence). Because LLMs fail silently and plausibly, traditional observability is insufficient. Steer provides the verification layer to catch these failures before they hit your users.

[Read the viral discussion on Hacker News.](https://news.ycombinator.com/item?id=46152838)

## Production-Ready Checklist

- [x] **Pydantic v2 Compatible:** Built on high-performance serialization.
- [x] **Thread-Safe:** Tested for high-concurrency environments.
- [x] **Zero Dependencies:** Minimal footprint to reduce supply-chain risk.
- [x] **Local-First:** No external API dependencies for core verification.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=imtt-dev/steer&type=date&legend=top-left)](https://www.star-history.com/#imtt-dev/steer&type=date&legend=top-left)