import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from agent.graph import agent
from agent.state import AgentState

load_dotenv()
console = Console()


def run_agent(task: str):
    console.print(Panel(f"[bold blue]Task:[/bold blue] {task}", title="Self-Healing Agent"))

    initial_state: AgentState = {
        "task": task,
        "generated_code": "",
        "execution_output": "",
        "error_message": None,
        "iterations": 0,
        "max_iterations": int(os.getenv("MAX_ITERATIONS", 5)),
        "attempt_history": [],
        "status": "running",
        "final_code": None
    }

    result = agent.invoke(initial_state)
    console.print(f"[yellow]Iterations used: {result['iterations']}[/yellow]")

    if result["status"] == "success":
        console.print(Panel("[bold green]✓ Code generated and verified![/bold green]", title="Result"))
        syntax = Syntax(result["final_code"], "python", theme="monokai", line_numbers=True)
        console.print(syntax)
    else:
        console.print(Panel("[bold red]✗ Agent could not solve the task.[/bold red]", title="Result"))
        console.print(f"Iterations used: {result['iterations']}")


if __name__ == "__main__":
    task = input("Enter your task in English: ")
    run_agent(task)