<p align="center">
  <img src="https://raw.githubusercontent.com/imtt-dev/steer/main/assets/steer.png" alt="Steer Labs Logo" width="120">
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
  Intercept hallucinations and protocol drift in runtime. <br>
  Enforce deterministic truth on probabilistic model outputs.
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
  <em>Mission Control: Enforcing deterministic protocols on frontier reasoning models.</em>
</p>

---

## Why Steer?

I built Steer because probability cannot fix probability. It provides the deterministic verification required to ship autonomous agents without performing an **Agent Lobotomy** (stripping features to ensure safety). 

Steer functions as an **Agent Service Mesh**. It decouples your reliability policy from your application logic, allowing you to secure entire frameworks or specific functions with a unified protocol.

## Operational Resilience

* **Low-Latency Sidecar:** Verification adds <5ms overhead by running in-process.
* **Fail-Safe Design:** Configurable behavior for internal errors to prioritize uptime.
* **Zero Data Exfiltration:** Local-first architecture. Traces and prompts never leave your network.
* **Audit-Ready Logging:** Every blocked response is logged with a deterministic reason code.

## Installation

```bash
pip install steer-sdk
```

## Integration Paths

### 1. The Agent Service Mesh (Global Governance)
Steer provides zero-touch reliability for frameworks like PydanticAI. Patch the framework at your application entry point to enforce a central policy across all agents.

```python
import steer
from pydantic_ai import Agent

# Initialize the Service Mesh via a central policy file
steer.init(patch=["pydantic_ai"], config="steer_policy.yaml")

# Steer auto-detects the agent name and introspects tools/types to apply locks.
agent = Agent('openai:gpt-5.2', name="finance_bot")
result = agent.run_sync("Query Q4 revenue")
```

### 2. Sidecar Dependency Injection (Manual Control)
For custom workflows or non-framework code, use the decorator pattern. Steer automatically injects taught rules into the `steer_rules` argument at runtime.

```python
from steer import capture, JsonJudge, SlopJudge

locks = [JsonJudge(), SlopJudge(entropy_threshold=3.5)]

@capture(Judges=locks)
def finance_agent(query, steer_rules=""):
    # steer_rules is populated automatically from Mission Control.
    # Update behavior via local UI without a code redeploy.
    system = f"You are a read-only SQL analyst.\n{steer_rules}"
    return model.generate(system, query)
```

## Quickstart

Ensure you run all commands from the same directory to keep the local database synced.

```bash
steer init   # Generates interactive demo agents
steer ui     # Launches Mission Control at http://localhost:8000
```

1. **Fail:** Run `python 01_structure_guard.py`. Output shows `[-] Status: Blocked`.
2. **Teach:** Go to the UI. Click the incident, select **Teach**, and save the rule.
3. **Fix:** Run the script again. Output shows `[+] Status: Passed`.

## Reality Locks in Action

The Steer workflow follows a simple loop: **Catch → Teach → Fix.**

### 1. Structure Guard (JSON)
**Problem:** Agent wraps JSON in Markdown backticks, breaking your parser.
**Fix:** Block the output and enforce raw JSON formatting via the dashboard.
![Structure Guard Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_json.gif)

### 2. Safety Guard (PII)
**Problem:** Agent accidentally leaks customer emails or internal keys despite system instructions.
**Fix:** Block the response and enforce redaction protocols across all agent outputs.
![Safety Guard Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_pii.gif)

### 3. Logic Guard (Ambiguity)
**Problem:** Agent guesses an ambiguous city (e.g., Springfield, IL) instead of asking for clarification.
**Fix:** Force the agent to ask the user clarifying questions when tool results are non-unique.
![Logic Guard Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_logic.gif)

### 4. Slop Filter (Brand Voice)
**Problem:** Agent uses sycophantic "AI-voice" (emojis, em-dashes, apologies) that pollutes data protocols. 
**The Fix:** Measures Shannon Entropy of the response. If the signal is too smooth (low entropy), Steer identifies it as an aesthetic lobotomy and blocks the output.
![Slop Filter Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_slop.gif)

## Cookbook

Explore the `cookbook/` directory for enterprise-grade implementations.

* [Zero-Touch Framework Patching](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/pydantic_ai_managed.py): Secure an entire PydanticAI agent fleet via a central policy file without decorators.
* [RAG Reliability](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/rag_reliability.py): Enforcing grounded citations and schema validity.
* [SQL Security](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/sql_reliability.py): Preventing destructive injections in analytics agents.

## Data Engine: Synthetic Data for DPO

Steer transforms runtime failures into a training asset. By capturing the delta between a **Blocked Response** (Rejected) and a **Taught Response** (Chosen), Steer generates contrastive pairs for Direct Preference Optimization (DPO).

```bash
# Export pairs ready for trl or unsloth
steer export --format dpo
```

## Production-Ready Checklist

- [x] **Pydantic v2 Compatible:** Built on high-performance serialization.
- [x] **Thread-Safe:** Tested for high-concurrency production environments.
- [x] **Zero Dependencies:** Minimal footprint to reduce supply-chain risk.
- [x] **Local-First:** No external API dependencies for core verification logic.

## What is the "Confident Idiot" Problem?

The Confident Idiot is a failure mode where an LLM generates a factually incorrect or structurally broken response with high probability (confidence). Because LLMs fail silently and plausibly, traditional observability is insufficient. Steer provides the verification layer to catch these failures before they hit your users.

[Read the viral discussion on Hacker News.](https://news.ycombinator.com/item?id=46152838)

## The Philosophy
Steer was built to close the divide between Model Intelligence (MMLU) and Engineering Control.

![Reliability Gap](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/reliability_gap_chart.png)