import json
from typing import List, Dict, Any
from rich.console import Console
from .config import settings

console = Console()

def export_data(format_type: str = "openai", output_file: str = None):
    """
    Reads local Steer logs and converts them into fine-tuning datasets.
    Supported formats: 
    - 'openai': Standard SFT (Successes only)
    - 'dpo': Contrastive pairs (Rejected vs Chosen)
    """
    log_path = settings.log_file
    if not log_path.exists():
        console.print("[red]No logs found. Run some agents first.[/red]")
        return

    count = 0
    if format_type == "dpo":
        final_output = output_file or "steer_dpo_train.jsonl"
        count = _export_dpo(log_path, final_output)
    else:
        final_output = output_file or "steer_fine_tune.jsonl"
        count = _export_sft(log_path, final_output)

    if count > 0:
        console.print(f"[bold green]Successfully exported {count} training examples.[/bold green]")
        console.print(f"File created: [bold]{final_output}[/bold]")
        console.print("[dim]IMPORTANT: Review this file before use to ensure no PII is included.[/dim]")
        
        # Ensure the community hook is always called
        _print_community_hook()
    else:
        console.print("[yellow]No valid data pairs found to export.[/yellow]")

def _export_sft(log_path, output_file):
    """Standard Supervised Fine-Tuning: Exports verified successful runs."""
    count = 0
    with open(output_file, 'w', encoding='utf-8') as out:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if not _is_blocked(record):
                        user_content = _extract_input(record)
                        assistant_content = record.get('raw_outputs', '')
                        
                        if user_content and assistant_content:
                            example = {
                                "messages": [
                                    {"role": "system", "content": f"Agent: {record.get('agent_name', 'default')}"},
                                    {"role": "user", "content": user_content},
                                    {"role": "assistant", "content": assistant_content}
                                ]
                            }
                            out.write(json.dumps(example) + "\n")
                            count += 1
                except:
                    continue
    return count

def _export_dpo(log_path, output_file):
    """Contrastive Pairs: Groups a failed run with its subsequent successful fix."""
    history = {} # prompt -> {rejected: str, chosen: str}
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                prompt = _extract_input(record)
                output = record.get('raw_outputs', '')
                
                if prompt not in history:
                    history[prompt] = {"rejected": None, "chosen": None}
                
                if _is_blocked(record):
                    history[prompt]["rejected"] = output
                else:
                    history[prompt]["chosen"] = output
            except:
                continue

    count = 0
    with open(output_file, 'w', encoding='utf-8') as out:
        for prompt, pairs in history.items():
            if pairs['chosen'] and pairs['rejected']:
                example = {
                    "prompt": prompt,
                    "chosen": pairs['chosen'],
                    "rejected": pairs['rejected']
                }
                out.write(json.dumps(example) + "\n")
                count += 1
    return count

def _is_blocked(record: dict) -> bool:
    """Checks if a run was blocked by a Judge."""
    return any(step.get('type') == 'error' for step in record.get('trace', []))

def _extract_input(record: dict) -> str:
    """Extracts the user prompt string from the trace or raw arguments."""
    trace = record.get('trace', [])
    for step in trace:
        if step.get('type') == 'user':
            return step.get('content', '')
            
    raw_args = record.get('raw_inputs', {}).get('args', [])
    if raw_args:
        return str(raw_args[0])
        
    return ""

def _print_community_hook():
    """
    Directs users to GitHub Discussions for technical support.
    """
    console.print("\n" + "-"*60)
    console.print("Fine-tuning dataset generated.")
    console.print("Format: JSONL (OpenAI/Anthropic compatible)")
    console.print("\nTechnical feedback or results sharing:")
    console.print("https://github.com/imtt-dev/steer/discussions")
    console.print("-" * 60)