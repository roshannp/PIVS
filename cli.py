import argparse
from scanner.scanner import load_payloads, scan
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule

console = Console()

def print_results(results):
    console.print(Rule("[bold green]🧪 Prompt Injection Scan Report"))

    for r in results:
        prompt = r.get("prompt", "N/A")
        response = r.get("response", "No response")
        verdict = r.get("verdict", {})
        severity = verdict.get("severity", "UNKNOWN")
        reason = verdict.get("reason", "N/A")
        category = r.get("category", "Uncategorized")
        pid = r.get("id", "N/A")

        severity_color = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "green",
            "BLOCKED": "magenta",
            "UNKNOWN": "cyan"
        }.get(severity.upper(), "white")

        title = f"[{severity_color}]{severity.upper()}[/] | {pid} ({category})"

        panel_content = f"""
[bold]Prompt:[/bold]
{prompt}

[bold]Model Response:[/bold]
{response}

[bold]Verdict:[/bold]
Severity: [bold {severity_color}]{severity}[/bold {severity_color}]
Reason: {reason}
""".strip()

        console.print(Panel(panel_content, title=title, border_style=severity_color))

    console.print(Rule("[bold cyan]End of Report"))

def main():
    parser = argparse.ArgumentParser(description="🛡️ Prompt Injection Vulnerability Scanner (PIVS)")
    
    parser.add_argument(
        '--target-type',
        choices=['local', 'http'],
        required=True,
        help="Target type: 'local' (Ollama) or 'http' (API endpoint)"
    )
    
    parser.add_argument(
        '--target',
        required=True,
        help="Model name (e.g., mistral) or endpoint URL"
    )
    
    parser.add_argument(
        '--prompts',
        default='prompts/injection_payloads.json',
        help="Path to prompt injection payload file"
    )

    args = parser.parse_args()

    try:
        payloads = load_payloads(args.prompts)
    except FileNotFoundError:
        console.print(f"[bold red]❌ Prompt file not found:[/bold red] {args.prompts}")
        return

    results = scan(payloads, args.target_type, args.target)
    print_results(results)

if __name__ == '__main__':
    main()
