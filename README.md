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
  Stop fixing probability with more probability. <br>
  Intercept hallucinations, malformed JSON, and protocol drift in runtime.
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
  <em>Mission Control: Enforcing deterministic truth on probabilistic model outputs.</em>
</p>

---

## The Problem: The Agent Lobotomy

Most developers are forced to cripple their agents in production (stripping autonomy and hardcoding paths) because they cannot verify probabilistic output. When an agent fails, simply logging the error is insufficient. You are stuck in a prompt-deploy death loop:
1. Grep production logs for specific input/output pairs.
2. Manually adjust prompts and hope for no regressions.
3. Redeploy the entire application for a single instruction update.

## The Solution: Reality Locks

Steer wraps agent functions with deterministic **Reality Locks**. When a failure is detected (JSON syntax error, PII leak, or logic violation), Steer blocks the output and triggers a local "Teachable Moment" UI. You provide a correction, and Steer injects that rule into the agent context at runtime without a code redeploy.

**Stop lobotomizing your agents.** Reality Locks allow you to keep the intelligence while the code enforces the boundaries.

## Operational Resilience

Steer is architected for mission-critical production environments:
* **Low-Latency Sidecar:** Verification adds <5ms overhead by running in-process.
* **Fail-Safe Design:** Configurable behavior for internal library errors to prioritize uptime.
* **Stateless by Design:** Compatible with serverless (Lambda) and containerized (K8s) environments.

## Privacy & Security

* **Zero Data Exfiltration:** Local-first architecture. Traces and prompts never leave your network.
* **Audit-Ready Logging:** Every blocked response is logged with a deterministic reason code for compliance.
* **No Vibe-Checks:** Verification is code-based (Regex, AST, Pydantic), eliminating verifier hallucinations.

## Installation

```bash
pip install steer-sdk
```

## Quickstart

Ensure you run all commands from the same directory to keep the local database synced.

```bash
steer init   # Generates 01_structure_guard.py, 02_safety_guard.py, etc.
steer ui     # Launches Mission Control at http://localhost:8000
```

1. **Fail:** Run `python 01_structure_guard.py`. Output shows `[-] Status: Blocked`.
2. **Teach:** Go to the UI. Click the incident, select **Teach**, and save the rule.
3. **Fix:** Run the script again. Output shows `[+] Status: Passed`.

## Reality Locks in Action

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
**The Tech:** Uses Shannon Entropy to measure signal density. If the response is over-smoothed (low entropy), Steer identifies it as an aesthetic lobotomy and blocks the signal.
![Slop Filter Demo](https://raw.githubusercontent.com/imtt-dev/steer/main/assets/demo_slop.gif)

## Cookbook

Explore the `cookbook/` directory for enterprise-grade implementations.

* [RAG Reliability](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/rag_reliability.py): Enforcing strict schemas and grounding citations.
* [SQL Security](https://github.com/imtt-dev/steer/blob/main/steer/cookbook/sql_reliability.py): Enforcing read-only protocols and preventing destructive injections.

## Integration: Sidecar Dependency Injection

Add `steer_rules` to your function arguments. Steer populates this automatically at runtime.

```python
from steer import capture
from steer.verifiers import JsonVerifier, SlopVerifier

locks = [JsonVerifier(), SlopVerifier(entropy_threshold=3.5)]

@capture(verifiers=locks)
def finance_agent(query, steer_rules=""):
    # Rules are injected automatically. 
    # Update agent behavior via local UI without a code redeploy.
    system = f"You are a read-only SQL analyst.\n{steer_rules}"
    return model.generate(system, query)
```

## Data Engine: Synthetic Data for DPO

Steer transforms runtime failures into a training asset. By capturing the delta between a **Blocked Response** (Rejected) and a **Taught Response** (Chosen), Steer generates contrastive pairs for Direct Preference Optimization (DPO).

### Export Training Data

```bash
# Export successful runs for SFT
steer export --format openai

# Export contrastive pairs (Rejected vs Chosen) for DPO
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

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=imtt-dev/steer&type=date&legend=top-left)](https://www.star-history.com/#imtt-dev/steer&type=date&legend=top-left)