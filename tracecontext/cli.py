import click
import requests
import subprocess
import os
import sys
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

console = Console()

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")

@click.group()
def main():
    """TraceContext CLI - Persistent AI Intent Memory."""
    pass

@main.command()
def init():
    """Initialize TraceContext in the current repository."""
    if not os.path.exists(".git"):
        console.print("[red]Error: Not a git repository.[/red]")
        return

    hook_content = """#!/bin/bash
# TraceContext Git Hook
MESSAGE=$(git log -1 --pretty=%B)
DIFF=$(git diff HEAD~1 HEAD)
REPO_URL=$(git config --get remote.origin.url)
USER_NAME=$(whoami)

# Use Python to safely send the JSON request to avoid shell escaping issues
python -c "
import requests, json, sys
data = {
    'type': 'git_commit',
    'data': {'message': sys.argv[1], 'diff': sys.argv[2]},
    'metadata': {'repo': sys.argv[3], 'user': sys.argv[4]}
}
try:
    requests.post('http://localhost:8000/events', json=data, timeout=5)
except:
    pass
" \\"$MESSAGE\\" \\"$DIFF\\" \\"$REPO_URL\\" \\"$USER_NAME\\" &
"""
    hook_path = ".git/hooks/post-commit"
    with open(hook_path, "w") as f:
        f.write(hook_content)
    
    # Make hook executable (cross-platform handling might be needed, but this is for sh)
    if sys.platform != "win32":
        os.chmod(hook_path, 0o755)

    console.print(Panel("[green]TraceContext initialized successfully![/green]\nGit post-commit hook installed.", title="Success"))

@main.command()
def status():
    """Check the status of the TraceContext orchestrator."""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/")
        status_data = response.json()
        console.print(f"[bold]Orchestrator Status:[/bold] [green]{status_data.get('status')}[/green]")
    except Exception:
        console.print("[red]Orchestrator is offline.[/red]\nStart it with [bold]tracecontext serve[/bold] or docker-compose.")

@main.command()
def serve():
    """Start the TraceContext Orchestrator server."""
    console.print("[yellow]Starting TraceContext Orchestrator...[/yellow]")
    # In a real package, we'd use uvicorn to run tracecontext.orchestrator.main:app
    subprocess.run(["uvicorn", "tracecontext.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"])

@main.command()
@click.argument("query")
def search(query):
    """Search for relevant context excerpts."""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/context", params={"query": query})
        results = response.json().get("context", [])
        if not results:
            console.print("[yellow]No relevant context found.[/yellow]")
        for res in results:
            console.print(Panel(res, title="Context Found"))
    except Exception:
        console.print("[red]Error connecting to orchestrator.[/red]")

if __name__ == "__main__":
    main()
